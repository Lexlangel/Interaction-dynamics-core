"""
experiment_o1_isolation.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment O Part 1 — Field-Responsiveness Isolation
2026

PURPOSE
───────
Experiment N revised the minimal mechanism to:
  registration + field-responsive motion + spatial clustering

But left one structural question open:

  Does random walk + spatial clustering (no field response) also pass?

Experiment M showed removing drift entirely reduced passes from 88 to 19.
Those 19 may be noise, or they may indicate clustering alone is sufficient.

This experiment tests that directly with three modes:

  RANDOM_WALK_CLUSTER
    random detection + random walk + spatial clustering
    No field response at any level.
    Pure test of clustering alone.

  FIELD_WALK_CLUSTER (control)
    random detection + gradient drift + spatial clustering
    Field-responsive but not detection-specific.
    Replicates M's no_detection finding (91/125 passed).

  FULL_STRUCTURED (reference)
    Standard mechanics from G–K.

PRE-REGISTERED DECISION RULE
──────────────────────────────
If RANDOM_WALK_CLUSTER passes >= 15/45:
  Field-responsiveness is not strictly necessary.
  Clustering alone is the irreducible mechanism.
  The minimal mechanism revises further.

If RANDOM_WALK_CLUSTER passes < 15/45:
  Field-responsiveness is an irreducible second condition.
  The minimal mechanism holds: field-responsive motion + spatial clustering.

Threshold 15/45 (33%) chosen as half the full_structured reference rate.
Below that, the difference is structurally significant.

SAME SWEEP AS N
  CF [0.75, 0.85, 0.95] × IS [0.7, 0.9, 1.1] × seeds [0-4] = 45 trials
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

C1_MIN_DISTANCE     = 30.0
C1_MAX_VARIANCE     = 15.0
C2_THRESHOLD        = 0.85
C3_RATE_THRESHOLD   = 0.05


# ─── Field ────────────────────────────────────────────────────────────────────

class Field:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.data = np.zeros(w * h, dtype=np.float32)

    def _idx(self, x, y):
        return int(max(0, min(self.h-1, int(y)))) * self.w + \
               int(max(0, min(self.w-1, int(x))))

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

    @property
    def is_stable(self): return self.age >= STABILITY_THRESHOLD and self.strength > 0.1

    def distance_to(self, o):
        return math.sqrt((self.x-o.x)**2 + (self.y-o.y)**2)


# ─── Detection ────────────────────────────────────────────────────────────────

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
                if (di,dj)!=(0,0) and 0<=i+di<field.w and 0<=j+dj<field.h)
            if is_max:
                candidates.append({"x": float(i), "y": float(j), "strength": v})
    return candidates


def random_detect(field, n=4):
    """No field structure used — random placement."""
    candidates = []
    for _ in range(n):
        x = float(random.randint(EDGE_REPEL, field.w-EDGE_REPEL))
        y = float(random.randint(EDGE_REPEL, field.h-EDGE_REPEL))
        s = field[x, y]
        if s > ANCHOR_COLLAPSE:
            candidates.append({"x": x, "y": y, "strength": s})
    return candidates


# ─── Drift ────────────────────────────────────────────────────────────────────

def gradient_drift(anchor, field):
    """Field-responsive: gradient descent."""
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    fx = -gx*DRIFT_SPEED*8; fy = -gy*DRIFT_SPEED*8
    if anchor.x < EDGE_REPEL:         fx += (EDGE_REPEL-anchor.x)*0.1
    if anchor.x > FIELD_W-EDGE_REPEL: fx -= (anchor.x-(FIELD_W-EDGE_REPEL))*0.1
    if anchor.y < EDGE_REPEL:          fy += (EDGE_REPEL-anchor.y)*0.1
    if anchor.y > FIELD_H-EDGE_REPEL: fy -= (anchor.y-(FIELD_H-EDGE_REPEL))*0.1
    anchor.x = max(5, min(FIELD_W-5, anchor.x+fx))
    anchor.y = max(5, min(FIELD_H-5, anchor.y+fy))
    anchor.age += 1
    anchor.strength = anchor.strength*0.98 + field[int(anchor.x), int(anchor.y)]*0.02


def random_walk(anchor, field, step=1.5):
    """No field response — pure random walk."""
    dx = random.uniform(-step, step)
    dy = random.uniform(-step, step)
    anchor.x = max(EDGE_REPEL, min(field.w-EDGE_REPEL, anchor.x+dx))
    anchor.y = max(EDGE_REPEL, min(field.h-EDGE_REPEL, anchor.y+dy))
    anchor.strength = anchor.strength*0.98 + field[int(anchor.x), int(anchor.y)]*0.02
    anchor.age += 1


# ─── Clustering ───────────────────────────────────────────────────────────────

def spatial_cluster(anchors):
    """Proximity-based connected-component clustering."""
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
        })
    return centroids


# ─── Topology ─────────────────────────────────────────────────────────────────

def topology_signature(anchors):
    n = len(anchors)
    if not n:
        return {"nodes":0,"laplacian_eigenvalues":[],"density":0.0,"components":0}
    positions = np.array([[a.x,a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < TOPOLOGY_EDGE_DIST) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0-dists/TOPOLOGY_EDGE_DIST, 0.0)
    edge_count = int(np.sum(adj)//2)
    max_edges = n*(n-1)/2
    density = edge_count/max_edges if max_edges > 0 else 0.0
    D = np.diag(np.sum(weights,axis=1)); L = D-weights
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
    return {"nodes":n,"laplacian_eigenvalues":lap_eigs,
            "density":round(density,4),"components":components}


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


# ─── Trial ────────────────────────────────────────────────────────────────────

def run_trial(constraint_factor, influence_strength, seed, mode):
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    log = []
    prev_cluster_sigs = {}
    prev_assignments = {}
    migration_log = []

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
                r = WAVE_SPEED*age; scan = int(r+WAVE_SPEED*10)
                ys = np.arange(max(0,cy-scan),min(FIELD_H,cy+scan))
                xs = np.arange(max(0,cx-scan),min(FIELD_W,cx+scan))
                if len(xs) and len(ys):
                    yy,xx = np.meshgrid(ys,xs,indexing="ij")
                    dist = np.sqrt(((xx-cx)**2+(yy-cy)**2).astype(np.float32))
                    phase = dist-r; mask = np.abs(phase)<WAVE_SPEED*8
                    amp = np.where(mask,
                        0.3*np.cos(phase*0.25)*np.exp(-WAVE_DECAY*dist)*np.exp(-age*0.008),0.0)
                    np.add.at(wave_field.data,(yy*FIELD_W+xx).ravel(),
                              amp.ravel().astype(np.float32))
                live.append(w)
        waves = live

        gauss_field.decay(constraint_factor)
        wave_field.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss_field)
        combined.add_field(wave_field)

        if tick % 8 == 0:
            # Detection
            if mode == "random_walk_cluster":
                candidates = random_detect(combined)
            else:  # full_structured or field_walk_cluster
                candidates = structured_detect(combined) if mode == "full_structured" \
                             else random_detect(combined)

            for c in candidates:
                nearby = next((a for a in anchors
                               if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2)<18), None)
                if nearby:
                    nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                    nearby.x = nearby.x*0.95 + c["x"]*0.05
                    nearby.y = nearby.y*0.95 + c["y"]*0.05
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["x"], c["y"], c["strength"]))

            # Drift — the key variable
            for a in anchors:
                if mode == "random_walk_cluster":
                    random_walk(a, combined)       # NO field response
                else:
                    gradient_drift(a, combined)    # field-responsive

            anchors = [a for a in anchors if a.strength>ANCHOR_COLLAPSE or a.age<30]

            # Clustering — spatial proximity in all modes
            centroids = spatial_cluster(anchors)

            current = {id(a): a.cluster_id for a in anchors}
            if tick > TICKS//2:
                n_a = max(len(anchors), 1)
                for a in anchors:
                    aid = id(a)
                    prev = prev_assignments.get(aid, a.cluster_id)
                    if prev != a.cluster_id and prev != -1:
                        migration_log.append((tick, n_a))
            prev_assignments = current

        if tick % LOG_INTERVAL == 0:
            centroids = spatial_cluster(anchors)
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
            })

    # Condition evaluation
    half = len(log)//2; late = log[half:]
    distances = [e["mean_cluster_distance"] for e in late if e["mean_cluster_distance"]]
    mean_dist = round(sum(distances)/len(distances),2) if distances else None
    dist_var = round(float(np.std(distances)),2) if len(distances)>1 else None
    c1p = (mean_dist is not None and mean_dist > C1_MIN_DISTANCE and
           dist_var is not None and dist_var < C1_MAX_VARIANCE)

    sims = [e["mean_within_similarity"] for e in late if e["mean_within_similarity"]]
    mean_sim = round(sum(sims)/len(sims),4) if sims else None
    c2p = mean_sim is not None and mean_sim > C2_THRESHOLD

    late_updates = (TICKS//2)//8
    rate = round(sum(1.0/n for _,n in migration_log)/late_updates,6) \
           if migration_log and late_updates > 0 else 0.0
    c3ppp = rate < C3_RATE_THRESHOLD

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
            "C3_triple_prime": {"passed": c3ppp, "rate": rate},
        },
        "regime": regime,
        "all_passed": c1p and c2p and c3ppp,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    constraint_factors  = [0.75, 0.85, 0.95]
    influence_strengths = [0.7,  0.9,  1.1]
    seeds               = [0, 1, 2, 3, 4]
    modes = ["full_structured", "field_walk_cluster", "random_walk_cluster"]
    trials = len(constraint_factors)*len(influence_strengths)*len(seeds)

    print(f"\n{'='*65}")
    print(f"  EXPERIMENT O1 — Field-Responsiveness Isolation Test")
    print(f"  {trials} trials per mode")
    print(f"  Decision rule: random_walk_cluster >= 15/45 → clustering alone sufficient")
    print(f"{'='*65}\n")

    all_results = {}
    t0 = time.time()

    for mode in modes:
        print(f"  Mode: {mode}")
        results = []
        n = 0
        for cf in constraint_factors:
            for ist in influence_strengths:
                for seed in seeds:
                    n += 1
                    print(f"    [{n:3d}/{trials}] cf={cf} is={ist} seed={seed} "
                          f"elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
                    results.append(run_trial(cf, ist, seed, mode))
        print(f"\n    Done.")
        all_results[mode] = results

    # Save
    with open("exp_o1_results.json","w") as f:
        json.dump({"experiment":"O1_isolation",
                   "decision_rule": "random_walk_cluster >= 15/45 → clustering alone sufficient",
                   "results": {
                       mode: [{"params":r["params"],"conditions":r["conditions"],
                               "regime":r["regime"],"all_passed":r["all_passed"]}
                              for r in rlist]
                       for mode, rlist in all_results.items()
                   }}, f, indent=2)
    print("  JSON → exp_o1_results.json")

    # Summary
    print(f"\n{'─'*65}")
    print("ISOLATION RESULTS")
    print(f"{'─'*65}")

    for mode in modes:
        results = all_results[mode]
        passed = sum(1 for r in results if r["all_passed"])
        rates = [r["conditions"]["C3_triple_prime"]["rate"] for r in results]
        sims  = [r["conditions"]["C2_prime"]["mean_similarity"] for r in results
                 if r["conditions"]["C2_prime"]["mean_similarity"]]
        c1s   = [r["conditions"]["C1_prime"]["passed"] for r in results]
        mean_rate = round(np.mean(rates),4)
        mean_sim  = round(np.mean(sims),4) if sims else None
        c1_pass   = sum(c1s)
        label = {
            "full_structured":    "reference",
            "field_walk_cluster": "field-responsive, no detection bias",
            "random_walk_cluster":"NO field response — clustering only",
        }[mode]
        print(f"  {mode:<25} {passed:2d}/45  rate={mean_rate}  "
              f"sim={mean_sim}  C1={c1_pass}/45")
        print(f"    ({label})")

    rwc_passed = sum(1 for r in all_results["random_walk_cluster"] if r["all_passed"])

    print(f"\n{'─'*65}")
    print("DECISION")
    print(f"{'─'*65}")
    if rwc_passed >= 15:
        print(f"  random_walk_cluster: {rwc_passed}/45 — ABOVE THRESHOLD (15)")
        print(f"  → Spatial clustering alone is sufficient.")
        print(f"  → Field-responsiveness is not an irreducible second condition.")
        print(f"  → Minimal mechanism revises to: registration + spatial clustering")
    else:
        print(f"  random_walk_cluster: {rwc_passed}/45 — BELOW THRESHOLD (15)")
        print(f"  → Field-responsiveness is an irreducible second condition.")
        print(f"  → Minimal mechanism holds: field-responsive motion + spatial clustering")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
