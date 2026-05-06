"""
experiment_j_ratio_c3.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment J — Ratio-Based C3
2026

PURPOSE
───────
Experiment I showed that C3' (raw count of gradient-correlated migrations)
failed as a discriminator. The null model averaged 216 gradient-correlated
events vs 19 in structured — backwards from the prediction — because random
reassignment generates hundreds of total migrations, and ~50% correlate with
the gradient by chance.

The fix: measure the *ratio* of gradient-correlated migrations to total
migrations. Expected values:
  Random walk   → ~0.50 (chance correlation)
  Gradient drift → ~0.85–0.95 (systematic downhill movement)

TIGHTENED CONDITIONS (C1' and C2' unchanged from Experiment I)
───────────────────────────────────────────────────────────────
C1' — Spatial stability: mean centroid distance > 30, variance < 15
C2' — Topology persistence: mean within-cluster similarity > 0.85
C3'' — Gradient correlation ratio: correlated / total migrations > 0.65
       (threshold set between expected random ~0.50 and structured ~0.85)
       Minimum 5 total migrations required (avoids ratio instability on small n)

EXPECTED OUTCOME (pre-registered)
──────────────────────────────────
Structured: passes C3'' — gradient-following drift produces consistent
  downhill movement; ratio ~0.85–0.95.
Null: fails C3'' — random walk produces ~0.50 ratio; below threshold.
C1' and C2' expected to replicate Experiment I: structured passes, null fails.

SAME SWEEP AS G, H, I
"""

import math, random, json, csv, time
import numpy as np
from dataclasses import dataclass
from scipy.spatial.distance import cdist
from collections import defaultdict

# ─── Constants ────────────────────────────────────────────────────────────────

GAUSSIAN_SIGMA      = 18.0
WAVE_SPEED          = 1.8
WAVE_DECAY          = 0.015
WAVE_FIELD_DECAY    = 0.995
ANCHOR_GRAD_THRESH  = 0.12
ANCHOR_MIN_STRENGTH = 0.15
ANCHOR_COLLAPSE     = 0.05
DRIFT_SPEED         = 0.18
EDGE_REPEL          = 8
MAX_ANCHORS         = 32
STABILITY_THRESHOLD = 80
CLUSTER_RADIUS      = 30.0
TOPOLOGY_EDGE_DIST  = 55.0
EVENT_RATE          = 0.012
FIELD_W, FIELD_H    = 160, 120
TICKS               = 2500
LOG_INTERVAL        = 50
NULL_K              = 2

C1_MIN_DISTANCE     = 30.0
C1_MAX_VARIANCE     = 15.0
C2_THRESHOLD        = 0.85
C3_RATIO_THRESHOLD  = 0.65   # gradient-correlated / total migrations
C3_MIN_TOTAL        = 5      # minimum total migrations for ratio to be valid


# ─── Field ────────────────────────────────────────────────────────────────────

class Field:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.data = np.zeros(w * h, dtype=np.float32)

    def _idx(self, x, y):
        return int(max(0, min(self.h-1, int(y)))) * self.w + int(max(0, min(self.w-1, int(x))))

    def __getitem__(self, pos):   return float(self.data[self._idx(*pos)])
    def decay(self, k):           self.data *= k
    def reset(self):              self.data[:] = 0
    def add_field(self, other):   self.data += other.data
    def copy_from(self, other):   self.data = other.data.copy()
    def total_energy(self):       return float(np.sum(self.data))

    def gradient(self, x, y):
        xi = max(1, min(self.w-2, int(x)))
        yi = max(1, min(self.h-2, int(y)))
        gx = (self.data[yi*self.w+xi+1] - self.data[yi*self.w+xi-1]) * 0.5
        gy = (self.data[(yi+1)*self.w+xi] - self.data[(yi-1)*self.w+xi]) * 0.5
        return float(gx), float(gy)

    def gradient_magnitude(self, x, y):
        gx, gy = self.gradient(x, y)
        return math.sqrt(gx*gx + gy*gy)


def apply_gaussian(field, ex, ey, strength, sigma=GAUSSIAN_SIGMA):
    cx, cy = int(ex), int(ey)
    r = int(sigma * 3)
    ys = np.arange(max(0, cy-r), min(field.h, cy+r))
    xs = np.arange(max(0, cx-r), min(field.w, cx+r))
    if not len(xs) or not len(ys): return
    yy, xx = np.meshgrid(ys, xs, indexing="ij")
    vals = strength * np.exp(
        -((xx-cx)**2 + (yy-cy)**2).astype(np.float32) / (2*sigma**2))
    np.add.at(field.data, (yy*field.w+xx).ravel(), vals.ravel())


# ─── Anchor ───────────────────────────────────────────────────────────────────

@dataclass
class Anchor:
    x: float; y: float; strength: float
    age: int = 0
    cluster_id: int = -1
    drift_vx: float = 0.0
    drift_vy: float = 0.0

    @property
    def is_stable(self): return self.age >= STABILITY_THRESHOLD and self.strength > 0.1

    def distance_to(self, o):
        return math.sqrt((self.x-o.x)**2 + (self.y-o.y)**2)


# ─── Structured mechanics ─────────────────────────────────────────────────────

def structured_detect(field, stride=6):
    candidates = []
    for j in range(stride, field.h-stride, stride):
        for i in range(stride, field.w-stride, stride):
            v = field[i, j]
            if v < ANCHOR_MIN_STRENGTH: continue
            if field.gradient_magnitude(i, j) >= ANCHOR_GRAD_THRESH: continue
            is_max = all(
                field[i+di, j+dj] <= v+0.01
                for di in range(-stride, stride+1, stride)
                for dj in range(-stride, stride+1, stride)
                if (di,dj) != (0,0) and 0<=i+di<field.w and 0<=j+dj<field.h)
            if is_max:
                candidates.append({"x": float(i), "y": float(j), "strength": v})
    return candidates


def structured_drift(anchor, field):
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    fx = -gx*DRIFT_SPEED*8; fy = -gy*DRIFT_SPEED*8
    if anchor.x < EDGE_REPEL:         fx += (EDGE_REPEL-anchor.x)*0.1
    if anchor.x > FIELD_W-EDGE_REPEL: fx -= (anchor.x-(FIELD_W-EDGE_REPEL))*0.1
    if anchor.y < EDGE_REPEL:          fy += (EDGE_REPEL-anchor.y)*0.1
    if anchor.y > FIELD_H-EDGE_REPEL: fy -= (anchor.y-(FIELD_H-EDGE_REPEL))*0.1
    anchor.drift_vx = fx; anchor.drift_vy = fy
    anchor.x = max(5, min(FIELD_W-5, anchor.x+fx))
    anchor.y = max(5, min(FIELD_H-5, anchor.y+fy))
    anchor.age += 1
    anchor.strength = anchor.strength*0.98 + field[int(anchor.x), int(anchor.y)]*0.02


def structured_cluster(anchors):
    n = len(anchors)
    if not n: return []
    assignments = [-1]*n; cid = 0
    for i in range(n):
        if assignments[i] != -1: continue
        assignments[i] = cid; queue = [i]
        while queue:
            curr = queue.pop()
            for j in range(n):
                if assignments[j] != -1: continue
                if anchors[curr].distance_to(anchors[j]) <= CLUSTER_RADIUS:
                    assignments[j] = cid; queue.append(j)
        cid += 1
    for i, a in enumerate(anchors): a.cluster_id = assignments[i]
    centroids = []
    for c in range(cid):
        members = [anchors[i] for i in range(n) if assignments[i]==c]
        if not members: continue
        centroids.append({
            "id": c,
            "cx": round(sum(a.x for a in members)/len(members), 2),
            "cy": round(sum(a.y for a in members)/len(members), 2),
            "size": len(members),
            "stable": sum(1 for a in members if a.is_stable),
        })
    return centroids


# ─── Null mechanics ───────────────────────────────────────────────────────────

def null_detect(field, n=4):
    candidates = []
    for _ in range(n):
        x = float(random.randint(EDGE_REPEL, field.w-EDGE_REPEL))
        y = float(random.randint(EDGE_REPEL, field.h-EDGE_REPEL))
        s = field[x, y]
        if s > ANCHOR_COLLAPSE:
            candidates.append({"x": x, "y": y, "strength": s})
    return candidates


def null_drift(anchor, field, step=1.5):
    dx = random.uniform(-step, step); dy = random.uniform(-step, step)
    anchor.drift_vx = dx; anchor.drift_vy = dy
    anchor.x = max(EDGE_REPEL, min(field.w-EDGE_REPEL, anchor.x+dx))
    anchor.y = max(EDGE_REPEL, min(field.h-EDGE_REPEL, anchor.y+dy))
    anchor.strength = anchor.strength*0.98 + field[int(anchor.x), int(anchor.y)]*0.02
    anchor.age += 1


def null_cluster(anchors, k=NULL_K):
    for a in anchors: a.cluster_id = random.randint(0, k-1)
    centroids = []
    for c in range(k):
        members = [a for a in anchors if a.cluster_id==c]
        if not members: continue
        centroids.append({
            "id": c,
            "cx": round(sum(a.x for a in members)/len(members), 2),
            "cy": round(sum(a.y for a in members)/len(members), 2),
            "size": len(members),
            "stable": sum(1 for a in members if a.is_stable),
        })
    return centroids


# ─── Topology ─────────────────────────────────────────────────────────────────

def topology_signature(anchors, max_dist=TOPOLOGY_EDGE_DIST):
    n = len(anchors)
    if not n:
        return {"nodes":0,"edges":0,"density":0.0,"components":0,
                "laplacian_eigenvalues":[],"mean_strength":0.0,"stable_count":0}
    positions = np.array([[a.x, a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < max_dist) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0-dists/max_dist, 0.0)
    edge_count = int(np.sum(adj)//2)
    max_edges = n*(n-1)/2
    density = edge_count/max_edges if max_edges > 0 else 0.0
    D = np.diag(np.sum(weights, axis=1)); L = D - weights
    try: lap_eigs = sorted([round(float(e),6) for e in np.linalg.eigvalsh(L)])
    except: lap_eigs = []
    parent = list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b): parent[find(a)]=find(b)
    for i in range(n):
        for j in range(i+1,n):
            if adj[i,j]: union(i,j)
    components = len(set(find(i) for i in range(n)))
    return {"nodes":n,"edges":edge_count,"density":round(density,4),
            "components":components,"laplacian_eigenvalues":lap_eigs,
            "mean_strength":round(float(np.mean([a.strength for a in anchors])),4),
            "stable_count":sum(1 for a in anchors if a.is_stable)}


def compare_topology(s1, s2):
    if s1["nodes"]==0 and s2["nodes"]==0: return 1.0
    if s1["nodes"]==0 or s2["nodes"]==0: return 0.0
    e1=s1["laplacian_eigenvalues"]; e2=s2["laplacian_eigenvalues"]
    ml=max(len(e1),len(e2))
    e1p=np.array(e1+[0.0]*(ml-len(e1))); e2p=np.array(e2+[0.0]*(ml-len(e2)))
    eig_score=math.exp(-float(np.linalg.norm(e1p-e2p))*0.15)
    c1,c2=s1["components"],s2["components"]
    cluster_score=1.0-abs(c1-c2)/max(c1,c2,1)
    density_score=1.0-abs(s1["density"]-s2["density"])
    node_score=min(s1["nodes"],s2["nodes"])/max(s1["nodes"],s2["nodes"])
    return round(0.50*eig_score+0.20*cluster_score+0.15*density_score+0.15*node_score,4)


def is_gradient_correlated(anchor, field):
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    gmag = math.sqrt(gx*gx + gy*gy)
    dmag = math.sqrt(anchor.drift_vx**2 + anchor.drift_vy**2)
    if gmag < 1e-6 or dmag < 1e-6: return False
    dot = anchor.drift_vx*gx + anchor.drift_vy*gy
    return dot < 0


# ─── Single trial ─────────────────────────────────────────────────────────────

def run_trial(constraint_factor, influence_strength, seed, mode="structured"):
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    log = []
    prev_cluster_sigs = {}
    prev_assignments = {}
    total_migrations = 0
    correlated_migrations = 0

    for tick in range(1, TICKS+1):
        if random.random() < EVENT_RATE:
            ex = EDGE_REPEL + random.random()*(FIELD_W-EDGE_REPEL*2)
            ey = EDGE_REPEL + random.random()*(FIELD_H-EDGE_REPEL*2)
            apply_gaussian(gauss_field, ex, ey, influence_strength)

        wave_field.reset()
        live = []
        for w in waves:
            age = tick - w["born"]
            if age < 300:
                cx,cy = int(w["x"]),int(w["y"])
                r = WAVE_SPEED*age
                scan = int(r+WAVE_SPEED*10)
                ys = np.arange(max(0,cy-scan),min(FIELD_H,cy+scan))
                xs = np.arange(max(0,cx-scan),min(FIELD_W,cx+scan))
                if len(xs) and len(ys):
                    yy,xx = np.meshgrid(ys,xs,indexing="ij")
                    dist = np.sqrt(((xx-cx)**2+(yy-cy)**2).astype(np.float32))
                    phase = dist-r
                    mask = np.abs(phase)<WAVE_SPEED*8
                    amp = np.where(mask,
                        0.3*np.cos(phase*0.25)*np.exp(-WAVE_DECAY*dist)*np.exp(-age*0.008),0.0)
                    np.add.at(wave_field.data,(yy*FIELD_W+xx).ravel(),amp.ravel().astype(np.float32))
                live.append(w)
        waves = live

        gauss_field.decay(constraint_factor)
        wave_field.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss_field)
        combined.add_field(wave_field)

        if tick % 8 == 0:
            candidates = structured_detect(combined) if mode=="structured" else null_detect(combined)
            for c in candidates:
                nearby = next((a for a in anchors
                               if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2)<18), None)
                if nearby:
                    nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                    nearby.x = nearby.x*0.95 + c["x"]*0.05
                    nearby.y = nearby.y*0.95 + c["y"]*0.05
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["x"], c["y"], c["strength"]))

            for a in anchors:
                if mode=="structured": structured_drift(a, combined)
                else: null_drift(a, combined)

            anchors = [a for a in anchors if a.strength>ANCHOR_COLLAPSE or a.age<30]
            centroids = structured_cluster(anchors) if mode=="structured" else null_cluster(anchors)

            # Migration tracking — ratio-based C3''
            current = {id(a): a.cluster_id for a in anchors}
            for a in anchors:
                aid = id(a)
                prev = prev_assignments.get(aid, a.cluster_id)
                if prev != a.cluster_id and prev != -1:
                    total_migrations += 1
                    if is_gradient_correlated(a, combined):
                        correlated_migrations += 1
            prev_assignments = current

        if tick % LOG_INTERVAL == 0:
            centroids = structured_cluster(anchors) if mode=="structured" else null_cluster(anchors)
            cluster_distances = []
            within_sims = []

            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i+1, len(centroids)):
                        ci,cj = centroids[i],centroids[j]
                        d = math.sqrt((ci["cx"]-cj["cx"])**2+(ci["cy"]-cj["cy"])**2)
                        cluster_distances.append(round(d,2))

            for c in centroids:
                members = [a for a in anchors if a.cluster_id==c["id"]]
                sig = topology_signature(members)
                key = f"c{c['id']}"
                prev_sig = prev_cluster_sigs.get(key)
                if prev_sig: within_sims.append(compare_topology(prev_sig, sig))
                prev_cluster_sigs[key] = sig

            ratio = round(correlated_migrations/total_migrations, 4) if total_migrations >= C3_MIN_TOTAL else None
            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "mean_cluster_distance": round(sum(cluster_distances)/len(cluster_distances),2)
                                         if cluster_distances else None,
                "distance_variance": round(float(np.std(cluster_distances)),2)
                                     if len(cluster_distances)>1 else None,
                "mean_within_similarity": round(sum(within_sims)/len(within_sims),4)
                                          if within_sims else None,
                "gradient_correlation_ratio": ratio,
                "total_migrations": total_migrations,
                "correlated_migrations": correlated_migrations,
            })

    # ── Condition evaluation ──────────────────────────────────────────────────
    half = len(log)//2
    late = log[half:]

    distances = [e["mean_cluster_distance"] for e in late if e["mean_cluster_distance"]]
    mean_dist = round(sum(distances)/len(distances),2) if distances else None
    dist_var = round(float(np.std(distances)),2) if len(distances)>1 else None
    c1p = (mean_dist is not None and mean_dist > C1_MIN_DISTANCE and
           dist_var is not None and dist_var < C1_MAX_VARIANCE)

    sims = [e["mean_within_similarity"] for e in late if e["mean_within_similarity"]]
    mean_sim = round(sum(sims)/len(sims),4) if sims else None
    c2p = mean_sim is not None and mean_sim > C2_THRESHOLD

    # C3'' — ratio-based
    ratio = round(correlated_migrations/total_migrations, 4) if total_migrations >= C3_MIN_TOTAL else None
    c3pp = ratio is not None and ratio > C3_RATIO_THRESHOLD

    if c1p and c2p and dist_var is not None and dist_var < 6.0:
        regime = "stable_coexistence"
    elif c1p and c2p:
        regime = "oscillatory_exchange"
    elif c1p and not c2p:
        regime = "transient_separation"
    elif not c1p and c2p:
        regime = "single_stable_basin"
    else:
        regime = "no_separation"

    return {
        "mode": mode,
        "params": {"constraint_factor": constraint_factor,
                   "influence_strength": influence_strength, "seed": seed},
        "conditions": {
            "C1_prime": {"passed": c1p, "mean_distance": mean_dist, "variance": dist_var},
            "C2_prime": {"passed": c2p, "mean_similarity": mean_sim},
            "C3_double_prime": {
                "passed": c3pp,
                "ratio": ratio,
                "total_migrations": total_migrations,
                "correlated_migrations": correlated_migrations,
                "threshold": C3_RATIO_THRESHOLD,
            },
        },
        "regime": regime,
        "all_passed": c1p and c2p and c3pp,
    }


# ─── Sweep ────────────────────────────────────────────────────────────────────

def run_sweep(mode):
    constraint_factors  = [0.75, 0.80, 0.85, 0.90, 0.95]
    influence_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds               = [0, 1, 2, 3, 4]
    total = len(constraint_factors)*len(influence_strengths)*len(seeds)
    regime_map = []
    t0 = time.time(); n = 0

    for cf in constraint_factors:
        for ist in influence_strengths:
            cell = []
            for seed in seeds:
                n += 1
                print(f"  [{mode}] [{n:3d}/{total}] cf={cf} is={ist} seed={seed} "
                      f"elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
                cell.append(run_trial(cf, ist, seed, mode=mode))

            regimes = [r["regime"] for r in cell]
            rc = defaultdict(int)
            for r in regimes: rc[r] += 1
            dom = max(rc, key=rc.get)
            passed = sum(1 for r in cell if r["all_passed"])
            ratios = [r["conditions"]["C3_double_prime"]["ratio"]
                      for r in cell if r["conditions"]["C3_double_prime"]["ratio"] is not None]
            sims = [r["conditions"]["C2_prime"]["mean_similarity"]
                    for r in cell if r["conditions"]["C2_prime"]["mean_similarity"]]

            regime_map.append({
                "constraint_factor": cf,
                "influence_strength": ist,
                "dominant_regime": dom,
                "all_conditions_passed": passed,
                "trials": len(seeds),
                "mean_gradient_ratio": round(np.mean(ratios),4) if ratios else None,
                "mean_topology_similarity": round(np.mean(sims),4) if sims else None,
            })

    print(f"\n  [{mode}] complete in {time.time()-t0:.1f}s")
    return regime_map


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    constraint_factors  = [0.75, 0.80, 0.85, 0.90, 0.95]
    influence_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]

    print(f"\n{'='*60}")
    print(f"  EXPERIMENT J — Ratio-Based C3''")
    print(f"  C3'' threshold: gradient-correlated/total > {C3_RATIO_THRESHOLD}")
    print(f"  Expected: structured ~0.85-0.95, null ~0.50")
    print(f"{'='*60}")

    print("\nRunning STRUCTURED mechanics...")
    g_map = run_sweep("structured")

    print("\nRunning NULL mechanics...")
    h_map = run_sweep("null")

    # Save
    with open("exp_j_results.json","w") as f:
        json.dump({"experiment":"J_ratio_c3",
                   "C3_double_prime_threshold": C3_RATIO_THRESHOLD,
                   "structured": g_map, "null": h_map}, f, indent=2)
    print("  JSON → exp_j_results.json")

    for mode, rmap, fname in [("structured",g_map,"exp_j_structured.csv"),
                               ("null",h_map,"exp_j_null.csv")]:
        with open(fname,"w",newline="") as f:
            w = csv.writer(f)
            w.writerow([""] + [f"is={ist}" for ist in influence_strengths])
            for cf in constraint_factors:
                row = [f"cf={cf}"]
                for ist in influence_strengths:
                    cell = next(c for c in rmap
                                if c["constraint_factor"]==cf and c["influence_strength"]==ist)
                    label = {"stable_coexistence":"COEX","oscillatory_exchange":"OSCL",
                             "transient_separation":"TRNS","single_stable_basin":"SNGL",
                             "no_separation":"NONE"}.get(cell["dominant_regime"],"????")
                    row.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
                w.writerow(row)
        print(f"  CSV  → {fname}")

    # Summary
    g_total = sum(c["all_conditions_passed"] for c in g_map)
    h_total = sum(c["all_conditions_passed"] for c in h_map)
    g_full  = sum(1 for c in g_map if c["all_conditions_passed"]==5)
    h_full  = sum(1 for c in h_map if c["all_conditions_passed"]==5)
    g_ratio = round(np.mean([c["mean_gradient_ratio"] for c in g_map if c["mean_gradient_ratio"]]),4)
    h_ratio = round(np.mean([c["mean_gradient_ratio"] for c in h_map if c["mean_gradient_ratio"]]),4)
    g_topo  = round(np.mean([c["mean_topology_similarity"] for c in g_map if c["mean_topology_similarity"]]),4)
    h_topo  = round(np.mean([c["mean_topology_similarity"] for c in h_map if c["mean_topology_similarity"]]),4)

    print(f"\n{'─'*60}")
    print("STRUCTURED — C1' C2' C3''")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in g_map if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            label = {"stable_coexistence":"COEX","oscillatory_exchange":"OSCL",
                     "transient_separation":"TRNS","single_stable_basin":"SNGL",
                     "no_separation":"NONE"}.get(cell["dominant_regime"],"????")
            row_parts.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\n{'─'*60}")
    print("NULL MODEL — C1' C2' C3''")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in h_map if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            label = {"stable_coexistence":"COEX","oscillatory_exchange":"OSCL",
                     "transient_separation":"TRNS","single_stable_basin":"SNGL",
                     "no_separation":"NONE"}.get(cell["dominant_regime"],"????")
            row_parts.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\n{'─'*60}")
    print("HEAD TO HEAD")
    print(f"{'─'*60}")
    print(f"  Structured:  {g_total}/125 passed  ({g_full}/25 cells full)")
    print(f"  Null model:  {h_total}/125 passed  ({h_full}/25 cells full)")
    print(f"  Structured mean gradient ratio:    {g_ratio}  (expected ~0.85-0.95)")
    print(f"  Null mean gradient ratio:          {h_ratio}  (expected ~0.50)")
    print(f"  Structured mean topology sim:      {g_topo}")
    print(f"  Null mean topology sim:            {h_topo}")

    sep = g_total - h_total
    if sep >= 40:
        verdict = "C3'' DISCRIMINATES: all three conditions now isolate structured mechanics"
    elif sep >= 20:
        verdict = "PARTIAL: C3'' improves discrimination but conditions not fully isolating"
    else:
        verdict = "C3'' INSUFFICIENT: further condition design required"

    print(f"\n  → {verdict}")
    print(f"\n{'='*60}")
