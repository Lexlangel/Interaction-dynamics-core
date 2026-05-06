"""
experiment_i_tightened.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment I — Tightened Conditions
2026

PURPOSE
───────
Experiments G and H showed that the original conditions (C1, C2, C3) were
partially trivial under null mechanics — specifically:
  - C1 was satisfied by random cluster assignment producing two groups
  - C3 was contaminated by random reassignment generating fake migrations

This experiment runs both structured (G) and null (H) mechanics against
tightened conditions designed to discriminate them:

  C1' — Spatial separation stability
         Mean inter-cluster centroid distance > 30 field units (second half)
         AND distance variance < 15
         Requires genuine spatial distinctness, not just numeric presence.

  C2' — Topological persistence (raised threshold)
         Mean within-cluster similarity > 0.85
         Previous threshold (0.70) allowed null model to pass technically.

  C3' — Gradient-correlated migration
         At least 3 migration events where the anchor's drift direction
         is negatively correlated with the local field gradient
         (i.e., moving downhill — driven by field structure, not random walk).
         Filters out random reassignment noise.

EXPECTED OUTCOME (pre-registered)
──────────────────────────────────
  Structured mechanics: pass C1', C2', C3' — drift is gradient-following,
    clusters form spatially, topology coherence is high.
  Null mechanics: fail C3' — random drift has ~50% gradient alignment by
    chance; 3 gradient-correlated migrations in a run requires sustained
    field-driven movement that random walk cannot reliably produce.
    Also expected to fail C1' in low-energy parameter regions.

SAME PARAMETER SWEEP AS G AND H
─────────────────────────────────
constraint_factor  : [0.75, 0.80, 0.85, 0.90, 0.95]
influence_strength : [0.5, 0.7, 0.9, 1.1, 1.3]
seeds              : 0–4
"""

import math, random, json, csv, time
import numpy as np
from dataclasses import dataclass, field as dc_field
from scipy.spatial.distance import cdist
from collections import defaultdict

# ─── Physics constants (identical across both modes) ──────────────────────────

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

# ─── Tightened condition thresholds (pre-registered) ─────────────────────────

C1_MIN_DISTANCE     = 30.0   # minimum mean inter-cluster centroid distance
C1_MAX_VARIANCE     = 15.0   # maximum distance variance
C2_THRESHOLD        = 0.85   # raised from 0.70
C3_MIN_MIGRATIONS   = 3      # minimum gradient-correlated migration events


# ─── Field ────────────────────────────────────────────────────────────────────

class Field:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.data = np.zeros(w * h, dtype=np.float32)

    def _idx(self, x, y):
        return int(max(0, min(self.h-1, int(y)))) * self.w + int(max(0, min(self.w-1, int(x))))

    def __getitem__(self, pos):    return float(self.data[self._idx(*pos)])
    def decay(self, k):            self.data *= k
    def reset(self):               self.data[:] = 0
    def add_field(self, other):    self.data += other.data
    def copy_from(self, other):    self.data = other.data.copy()
    def total_energy(self):        return float(np.sum(self.data))

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


# ─── Structured mechanics (Experiment G) ─────────────────────────────────────

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
                if (di, dj) != (0, 0) and 0<=i+di<field.w and 0<=j+dj<field.h)
            if is_max:
                candidates.append({"x": float(i), "y": float(j), "strength": v})
    return candidates


def structured_drift(anchor, field):
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    fx = -gx*DRIFT_SPEED*8; fy = -gy*DRIFT_SPEED*8
    if anchor.x < EDGE_REPEL:          fx += (EDGE_REPEL - anchor.x)*0.1
    if anchor.x > FIELD_W-EDGE_REPEL:  fx -= (anchor.x - (FIELD_W-EDGE_REPEL))*0.1
    if anchor.y < EDGE_REPEL:           fy += (EDGE_REPEL - anchor.y)*0.1
    if anchor.y > FIELD_H-EDGE_REPEL:  fy -= (anchor.y - (FIELD_H-EDGE_REPEL))*0.1
    anchor.drift_vx = fx; anchor.drift_vy = fy
    anchor.x = max(5, min(FIELD_W-5, anchor.x+fx))
    anchor.y = max(5, min(FIELD_H-5, anchor.y+fy))
    anchor.age += 1
    fv = field[int(anchor.x), int(anchor.y)]
    anchor.strength = anchor.strength*0.98 + fv*0.02


def structured_cluster(anchors, radius=CLUSTER_RADIUS):
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
                if anchors[curr].distance_to(anchors[j]) <= radius:
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
            "mean_strength": round(sum(a.strength for a in members)/len(members), 4),
        })
    return centroids


# ─── Null mechanics (Experiment H) ───────────────────────────────────────────

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
    dx = random.uniform(-step, step)
    dy = random.uniform(-step, step)
    anchor.drift_vx = dx; anchor.drift_vy = dy
    anchor.x = max(EDGE_REPEL, min(field.w-EDGE_REPEL, anchor.x+dx))
    anchor.y = max(EDGE_REPEL, min(field.h-EDGE_REPEL, anchor.y+dy))
    fv = field[int(anchor.x), int(anchor.y)]
    anchor.strength = anchor.strength*0.98 + fv*0.02
    anchor.age += 1


def null_cluster(anchors, k=NULL_K):
    for a in anchors: a.cluster_id = random.randint(0, k-1)
    centroids = []
    for c in range(k):
        members = [a for a in anchors if a.cluster_id == c]
        if not members: continue
        centroids.append({
            "id": c,
            "cx": round(sum(a.x for a in members)/len(members), 2),
            "cy": round(sum(a.y for a in members)/len(members), 2),
            "size": len(members),
            "stable": sum(1 for a in members if a.is_stable),
            "mean_strength": round(sum(a.strength for a in members)/len(members), 4),
        })
    return centroids


# ─── Topology ─────────────────────────────────────────────────────────────────

def topology_signature(anchors, max_dist=TOPOLOGY_EDGE_DIST):
    n = len(anchors)
    if not n:
        return {"nodes": 0, "edges": 0, "density": 0.0, "components": 0,
                "laplacian_eigenvalues": [], "mean_strength": 0.0, "stable_count": 0}
    positions = np.array([[a.x, a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < max_dist) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0 - dists/max_dist, 0.0)
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
    return {"nodes":n, "edges":edge_count, "density":round(density,4),
            "components":components, "laplacian_eigenvalues":lap_eigs,
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


# ─── C3' — gradient-correlated migration check ───────────────────────────────

def is_gradient_correlated(anchor, field):
    """
    Returns True if the anchor's drift direction is negatively correlated
    with the local field gradient — i.e., moving downhill (gradient descent).
    This is the signature of field-driven movement vs random walk.
    """
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    gmag = math.sqrt(gx*gx + gy*gy)
    dmag = math.sqrt(anchor.drift_vx**2 + anchor.drift_vy**2)
    if gmag < 1e-6 or dmag < 1e-6:
        return False
    # dot product of drift with gradient — negative means moving downhill
    dot = anchor.drift_vx*gx + anchor.drift_vy*gy
    return dot < 0


# ─── Single trial ─────────────────────────────────────────────────────────────

def run_trial(constraint_factor, influence_strength, seed, mode="structured"):
    """mode: 'structured' uses G mechanics, 'null' uses H mechanics."""
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    log = []
    prev_cluster_sigs = {}
    prev_assignments = {}

    # Migration tracking — now records gradient correlation
    all_migrations = []           # all migration events
    gradient_correlated = []      # subset: C3' qualifying events

    for tick in range(1, TICKS+1):
        if random.random() < EVENT_RATE:
            ex = EDGE_REPEL + random.random()*(FIELD_W-EDGE_REPEL*2)
            ey = EDGE_REPEL + random.random()*(FIELD_H-EDGE_REPEL*2)
            apply_gaussian(gauss_field, ex, ey, influence_strength)

        # Wave propagation (identical in both modes)
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
            # Detection
            candidates = (structured_detect(combined)
                          if mode=="structured" else null_detect(combined))
            for c in candidates:
                nearby = next(
                    (a for a in anchors
                     if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2)<18), None)
                if nearby:
                    nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                    nearby.x = nearby.x*0.95 + c["x"]*0.05
                    nearby.y = nearby.y*0.95 + c["y"]*0.05
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["x"], c["y"], c["strength"]))

            # Drift — record before cluster assignment for C3'
            for a in anchors:
                if mode=="structured":
                    structured_drift(a, combined)
                else:
                    null_drift(a, combined)

            anchors = [a for a in anchors if a.strength>ANCHOR_COLLAPSE or a.age<30]

            # Cluster assignment
            if mode=="structured":
                centroids = structured_cluster(anchors)
            else:
                centroids = null_cluster(anchors)

            # Migration tracking with gradient correlation check
            current = {id(a): a.cluster_id for a in anchors}
            for a in anchors:
                aid = id(a)
                prev = prev_assignments.get(aid, a.cluster_id)
                if prev != a.cluster_id and prev != -1:
                    correlated = is_gradient_correlated(a, combined)
                    event = {
                        "tick": tick,
                        "from": prev,
                        "to": a.cluster_id,
                        "gradient_correlated": correlated,
                    }
                    all_migrations.append(event)
                    if correlated:
                        gradient_correlated.append(event)
            prev_assignments = current

        # Logging
        if tick % LOG_INTERVAL == 0:
            centroids = (structured_cluster(anchors) if mode=="structured"
                         else null_cluster(anchors))
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
                if prev_sig:
                    within_sims.append(compare_topology(prev_sig, sig))
                prev_cluster_sigs[key] = sig

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "stable_count": sum(1 for a in anchors if a.is_stable),
                "cluster_count": len(centroids),
                "mean_cluster_distance": round(sum(cluster_distances)/len(cluster_distances),2)
                                         if cluster_distances else None,
                "distance_variance": round(float(np.std(cluster_distances)),2)
                                     if len(cluster_distances)>1 else None,
                "mean_within_similarity": round(sum(within_sims)/len(within_sims),4)
                                          if within_sims else None,
                "field_energy": round(combined.total_energy(),4),
                "gradient_correlated_migrations": len(gradient_correlated),
            })

    # ── Tightened condition evaluation ────────────────────────────────────────
    half = len(log)//2
    late = log[half:]

    # C1' — spatial separation stability
    distances = [e["mean_cluster_distance"] for e in late if e["mean_cluster_distance"]]
    mean_dist = round(sum(distances)/len(distances),2) if distances else None
    dist_var = round(float(np.std(distances)),2) if len(distances)>1 else None
    c1p = (mean_dist is not None and mean_dist > C1_MIN_DISTANCE and
           dist_var is not None and dist_var < C1_MAX_VARIANCE)

    # C2' — raised topology threshold
    sims = [e["mean_within_similarity"] for e in late if e["mean_within_similarity"]]
    mean_sim = round(sum(sims)/len(sims),4) if sims else None
    c2p = mean_sim is not None and mean_sim > C2_THRESHOLD

    # C3' — gradient-correlated migrations
    n_correlated = len(gradient_correlated)
    c3p = n_correlated >= C3_MIN_MIGRATIONS

    # Regime
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
            "C1_prime_spatial_stability": {
                "passed": c1p,
                "mean_inter_cluster_distance": mean_dist,
                "distance_variance": dist_var,
                "thresholds": {"min_distance": C1_MIN_DISTANCE,
                               "max_variance": C1_MAX_VARIANCE},
            },
            "C2_prime_topology_persistence": {
                "passed": c2p,
                "mean_within_similarity": mean_sim,
                "threshold": C2_THRESHOLD,
            },
            "C3_prime_gradient_migration": {
                "passed": c3p,
                "gradient_correlated_events": n_correlated,
                "total_migration_events": len(all_migrations),
                "min_required": C3_MIN_MIGRATIONS,
            },
        },
        "regime": regime,
        "all_passed": c1p and c2p and c3p,
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
            mean_sep = round(np.mean([
                r["conditions"]["C1_prime_spatial_stability"]["mean_inter_cluster_distance"] or 0
                for r in cell]), 2)
            sims = [r["conditions"]["C2_prime_topology_persistence"]["mean_within_similarity"]
                    for r in cell
                    if r["conditions"]["C2_prime_topology_persistence"]["mean_within_similarity"]]
            mean_topo = round(np.mean(sims),4) if sims else None
            mean_corr = round(np.mean([
                r["conditions"]["C3_prime_gradient_migration"]["gradient_correlated_events"]
                for r in cell]),2)

            regime_map.append({
                "constraint_factor": cf,
                "influence_strength": ist,
                "dominant_regime": dom,
                "regime_counts": dict(rc),
                "all_conditions_passed": passed,
                "trials": len(seeds),
                "mean_inter_cluster_distance": mean_sep,
                "mean_topology_similarity": mean_topo,
                "mean_gradient_correlated_migrations": mean_corr,
            })

    print(f"\n  [{mode}] complete in {time.time()-t0:.1f}s")
    return regime_map


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT I — Tightened Conditions")
    print(f"  Structured vs Null — head to head")
    print(f"  C1': spatial stability  C2': sim>0.85  C3': gradient migration")
    print(f"{'='*60}")

    print("\nRunning STRUCTURED mechanics...")
    g_map = run_sweep("structured")

    print("\nRunning NULL mechanics...")
    h_map = run_sweep("null")

    # ── Save ──────────────────────────────────────────────────────────────────
    constraint_factors  = [0.75, 0.80, 0.85, 0.90, 0.95]
    influence_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]

    results = {
        "experiment": "I_tightened_conditions",
        "conditions": {
            "C1_prime": f"mean_distance > {C1_MIN_DISTANCE} AND variance < {C1_MAX_VARIANCE}",
            "C2_prime": f"mean_within_similarity > {C2_THRESHOLD}",
            "C3_prime": f">= {C3_MIN_MIGRATIONS} gradient-correlated migrations",
        },
        "structured": g_map,
        "null": h_map,
    }
    with open("exp_i_results.json","w") as f:
        json.dump(results, f, indent=2)
    print("  JSON → exp_i_results.json")

    # ── CSV ───────────────────────────────────────────────────────────────────
    for mode, rmap, fname in [("structured", g_map, "exp_i_structured.csv"),
                               ("null",       h_map, "exp_i_null.csv")]:
        with open(fname,"w",newline="") as f:
            w = csv.writer(f)
            w.writerow([""] + [f"is={ist}" for ist in influence_strengths])
            for cf in constraint_factors:
                row = [f"cf={cf}"]
                for ist in influence_strengths:
                    cell = next(c for c in rmap
                                if c["constraint_factor"]==cf
                                and c["influence_strength"]==ist)
                    label = {
                        "stable_coexistence":   "COEX",
                        "oscillatory_exchange": "OSCL",
                        "transient_separation": "TRNS",
                        "single_stable_basin":  "SNGL",
                        "no_separation":        "NONE",
                    }.get(cell["dominant_regime"],"????")
                    row.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
                w.writerow(row)
        print(f"  CSV  → {fname}")

    # ── Summary ───────────────────────────────────────────────────────────────
    g_total = sum(c["all_conditions_passed"] for c in g_map)
    h_total = sum(c["all_conditions_passed"] for c in h_map)
    g_full  = sum(1 for c in g_map if c["all_conditions_passed"]==5)
    h_full  = sum(1 for c in h_map if c["all_conditions_passed"]==5)
    g_topo  = round(np.mean([c["mean_topology_similarity"] for c in g_map
                              if c["mean_topology_similarity"]]),4)
    h_topo  = round(np.mean([c["mean_topology_similarity"] for c in h_map
                              if c["mean_topology_similarity"]]),4)
    g_corr  = round(np.mean([c["mean_gradient_correlated_migrations"] for c in g_map]),2)
    h_corr  = round(np.mean([c["mean_gradient_correlated_migrations"] for c in h_map]),2)

    print(f"\n{'─'*60}")
    print("STRUCTURED — tightened conditions")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in g_map
                        if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            label = {"stable_coexistence":"COEX","oscillatory_exchange":"OSCL",
                     "transient_separation":"TRNS","single_stable_basin":"SNGL",
                     "no_separation":"NONE"}.get(cell["dominant_regime"],"????")
            row_parts.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\n{'─'*60}")
    print("NULL MODEL — tightened conditions")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in h_map
                        if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            label = {"stable_coexistence":"COEX","oscillatory_exchange":"OSCL",
                     "transient_separation":"TRNS","single_stable_basin":"SNGL",
                     "no_separation":"NONE"}.get(cell["dominant_regime"],"????")
            row_parts.append(f"{label}({cell['all_conditions_passed']}/{cell['trials']})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\n{'─'*60}")
    print("HEAD TO HEAD COMPARISON")
    print(f"{'─'*60}")
    print(f"  Structured:  {g_total}/125 passed  ({g_full}/25 cells full)")
    print(f"  Null model:  {h_total}/125 passed  ({h_full}/25 cells full)")
    print(f"  Structured mean topo sim:   {g_topo}")
    print(f"  Null mean topo sim:         {h_topo}")
    print(f"  Structured mean C3' events: {g_corr}")
    print(f"  Null mean C3' events:       {h_corr}")

    separation = g_total - h_total
    if separation >= 40:
        verdict = "TIGHTENED CONDITIONS DISCRIMINATE: structured mechanics isolated"
    elif separation >= 20:
        verdict = "PARTIAL DISCRIMINATION: structured mechanics contribute but conditions not fully isolating"
    else:
        verdict = "CONDITIONS STILL INSUFFICIENT: further tightening required"

    print(f"\n  → {verdict}")
    print(f"\n{'='*60}")
