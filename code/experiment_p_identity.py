"""
experiment_p_identity_mapping.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment P — Identity Mapping and Reconstruction
2026

PURPOSE
───────
Experiments G–O established the structural conditions for identity-like
topology. Experiment P tests whether the simulation instantiates the
framework's specific claims about identity persistence and reconstruction.

Three framework claims tested directly:

  CLAIM 1 — Reconstruction from field traces
    "Identity leaves traces in the interaction environment as well as in
    the system itself. When a system returns after interruption, field
    anchors support reconstruction."

    Test: remove all anchors (execution layer disrupted). Keep field intact.
    Prediction: new anchors form at same field peaks → basin reconstructs.
    This is ANCHOR_PRUNING perturbation.

  CLAIM 2 — Full reset degrades reconstruction quality
    "A system without memory reconstructs from whatever anchors remain in
    the interaction environment — more slowly, along coarser paths."

    Test: zero field AND all anchors (complete disruption, no traces).
    Prediction: reconstruction occurs but takes longer and produces less
    topologically similar basins. This is FULL_RESET perturbation.

  CLAIM 3 — Reconstruction path is visible as transient instability
    "Identity drift has signatures... Recovery follows a characteristic
    sequence: return to anchor cues, reconstruct the relational map,
    restore coherence before elaboration."

    Test: measure migration rate during recovery period.
    Prediction: elevated migration rate immediately post-perturbation,
    declining as basins reform. This is identity drift then anchoring.

SIMULATION OBSERVABLES → FRAMEWORK CONSTRUCTS
───────────────────────────────────────────────
Basin             → proto-identity region
Basin topology    → identity topology (Laplacian signature)
Anchor            → structural invariant (identity anchor)
Migration rate    → identity drift / instability
Topology sim.     → identity persistence measure
Reconstruction    → identity reformation from field traces

DESIGN
──────
Phase 1 (ticks 1–2000):   establish stable multi-basin state
Phase 2 (tick 2001):       apply perturbation
Phase 3 (ticks 2001–2500): observe reconstruction

Perturbation types:
  anchor_pruning  — remove all anchors, keep field intact
  field_half_zero — zero field in half the spatial region, keep anchors
  full_reset      — zero field AND all anchors

Recovery metrics:
  topology_recovery: topology similarity between pre-perturbation and
                     recovery-period cluster signature (Laplacian)
  separation_recovery: cluster separation ≥ 2.0 mean hop distance
  stability_recovery: medoid stability > 0.30 in recovery period
  recovery_time: ticks until topology_recovery > 0.70

Run 10 seeds at stable parameters (CF=0.85, IS=1.1).
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

ESTABLISH_TICKS     = 2000  # Phase 1: establish identity
RECOVERY_TICKS      = 500   # Phase 3: observe reconstruction
LOG_INTERVAL        = 25    # finer logging for recovery detail

# Stable parameters from K (COEX regime)
CONSTRAINT_FACTOR   = 0.85
INFLUENCE_STRENGTH  = 1.1

PERTURBATION_TYPES  = ["anchor_pruning", "field_half_zero", "full_reset"]
SEEDS               = list(range(10))


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
    def copy(self):
        f = Field(self.w, self.h); f.data = self.data.copy(); return f

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

    def copy(self):
        return Anchor(self.x, self.y, self.strength, self.age, self.cluster_id)


# ─── Structured mechanics ─────────────────────────────────────────────────────

def s_detect(field, stride=6):
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


def s_drift(anchor, field):
    gx, gy = field.gradient(int(anchor.x), int(anchor.y))
    fx = -gx*DRIFT_SPEED*8; fy = -gy*DRIFT_SPEED*8
    if anchor.x < EDGE_REPEL:          fx += (EDGE_REPEL-anchor.x)*0.1
    if anchor.x > FIELD_W-EDGE_REPEL:  fx -= (anchor.x-(FIELD_W-EDGE_REPEL))*0.1
    if anchor.y < EDGE_REPEL:           fy += (EDGE_REPEL-anchor.y)*0.1
    if anchor.y > FIELD_H-EDGE_REPEL:  fy -= (anchor.y-(FIELD_H-EDGE_REPEL))*0.1
    anchor.x = max(5, min(FIELD_W-5, anchor.x+fx))
    anchor.y = max(5, min(FIELD_H-5, anchor.y+fy))
    anchor.age += 1
    anchor.strength = anchor.strength*0.98 + field[int(anchor.x), int(anchor.y)]*0.02


def s_cluster(anchors):
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

def topology_signature(anchors, max_dist=TOPOLOGY_EDGE_DIST):
    n = len(anchors)
    if not n:
        return {"nodes":0,"laplacian_eigenvalues":[],"density":0.0,"components":0}
    positions = np.array([[a.x, a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < max_dist) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0-dists/max_dist, 0.0)
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


# ─── Step function ────────────────────────────────────────────────────────────

def step(gauss_field, wave_field, combined, anchors, waves, tick,
         cf, ist, prev_assignments, migration_log_ref):
    if random.random() < EVENT_RATE:
        ex = EDGE_REPEL + random.random()*(FIELD_W-EDGE_REPEL*2)
        ey = EDGE_REPEL + random.random()*(FIELD_H-EDGE_REPEL*2)
        apply_gaussian(gauss_field, ex, ey, ist)

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
                np.add.at(wave_field.data,(yy*FIELD_W+xx).ravel(),amp.ravel().astype(np.float32))
            live.append(w)
    waves[:] = live

    gauss_field.decay(cf); wave_field.decay(WAVE_FIELD_DECAY)
    combined.copy_from(gauss_field); combined.add_field(wave_field)

    if tick % 8 == 0:
        candidates = s_detect(combined)
        for c in candidates:
            nearby = next((a for a in anchors
                           if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2)<18), None)
            if nearby:
                nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                nearby.x = nearby.x*0.95 + c["x"]*0.05
                nearby.y = nearby.y*0.95 + c["y"]*0.05
            elif len(anchors) < MAX_ANCHORS:
                anchors.append(Anchor(c["x"], c["y"], c["strength"]))

        for a in anchors: s_drift(a, combined)
        anchors[:] = [a for a in anchors if a.strength>ANCHOR_COLLAPSE or a.age<30]
        s_cluster(anchors)

        current = {id(a): a.cluster_id for a in anchors}
        n_a = max(len(anchors), 1)
        for a in anchors:
            aid = id(a)
            prev = prev_assignments.get(aid, a.cluster_id)
            if prev != a.cluster_id and prev != -1:
                migration_log_ref.append(1.0/n_a)
        prev_assignments.clear(); prev_assignments.update(current)


# ─── Single trial ─────────────────────────────────────────────────────────────

def run_trial(seed, perturbation_type):
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    prev_assignments = {}
    migration_log = []

    # ── Phase 1: establish identity (2000 ticks) ──────────────────────────────
    for tick in range(1, ESTABLISH_TICKS + 1):
        step(gauss_field, wave_field, combined, anchors, waves, tick,
             CONSTRAINT_FACTOR, INFLUENCE_STRENGTH, prev_assignments, migration_log)

    # Snapshot pre-perturbation state
    pre_sig = topology_signature(anchors)
    pre_centroids = s_cluster(anchors)
    pre_n_clusters = len(pre_centroids)
    pre_anchors_snapshot = [(a.x, a.y, a.strength) for a in anchors]
    migration_log.clear()

    # ── Phase 2: apply perturbation ───────────────────────────────────────────
    if perturbation_type == "anchor_pruning":
        # Remove all anchors — keep field intact
        # Framework prediction: field retains traces, anchors reform at same peaks
        anchors.clear()
        prev_assignments.clear()

    elif perturbation_type == "field_half_zero":
        # Zero the left half of the field — keep anchors
        # Tests: do anchors drift away from erased region? Do they persist?
        half_x = FIELD_W // 2
        gauss_field.data.reshape(FIELD_H, FIELD_W)[:, :half_x] = 0
        combined.copy_from(gauss_field); combined.add_field(wave_field)

    elif perturbation_type == "full_reset":
        # Zero everything — no field traces, no anchors
        # Framework prediction: reconstruction occurs but slower, less similar
        anchors.clear()
        gauss_field.reset(); wave_field.reset(); combined.reset()
        prev_assignments.clear()

    # ── Phase 3: observe reconstruction (500 ticks) ───────────────────────────
    recovery_log = []
    first_recovery_tick = None

    for tick in range(ESTABLISH_TICKS + 1, ESTABLISH_TICKS + RECOVERY_TICKS + 1):
        step(gauss_field, wave_field, combined, anchors, waves, tick,
             CONSTRAINT_FACTOR, INFLUENCE_STRENGTH, prev_assignments, migration_log)

        if tick % LOG_INTERVAL == 0:
            centroids = s_cluster(anchors)
            sig = topology_signature(anchors)
            topo_sim = compare_topology(pre_sig, sig)

            cluster_distances = []
            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i+1, len(centroids)):
                        ci,cj = centroids[i],centroids[j]
                        d = math.sqrt((ci["cx"]-cj["cx"])**2+(ci["cy"]-cj["cy"])**2)
                        cluster_distances.append(d)
            mean_dist = round(sum(cluster_distances)/len(cluster_distances), 2) \
                        if cluster_distances else None

            # Migration rate over last LOG_INTERVAL updates
            updates_per_log = LOG_INTERVAL // 8
            n_mig = len(migration_log[-updates_per_log:]) if migration_log else 0
            n_a = max(len(anchors), 1)
            mig_rate = round(sum(migration_log[-updates_per_log:]) / max(updates_per_log, 1), 4)

            entry = {
                "tick": tick,
                "relative_tick": tick - ESTABLISH_TICKS,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "topology_similarity": topo_sim,
                "mean_cluster_distance": mean_dist,
                "migration_rate": mig_rate,
                "n_clusters_vs_pre": len(centroids) - pre_n_clusters,
            }
            recovery_log.append(entry)

            if first_recovery_tick is None and topo_sim >= 0.70:
                first_recovery_tick = tick - ESTABLISH_TICKS

    # Recovery metrics
    late_recovery = recovery_log[len(recovery_log)//2:]
    final_topo_sim = recovery_log[-1]["topology_similarity"] if recovery_log else 0.0
    mean_topo_sim = round(np.mean([e["topology_similarity"] for e in late_recovery]), 4) \
                    if late_recovery else 0.0
    mean_mig_rate = round(np.mean([e["migration_rate"] for e in late_recovery]), 4) \
                    if late_recovery else None
    final_n_clusters = recovery_log[-1]["cluster_count"] if recovery_log else 0
    separation_recovered = any(e["mean_cluster_distance"] and e["mean_cluster_distance"] >= 30.0
                               for e in late_recovery)

    return {
        "seed": seed,
        "perturbation": perturbation_type,
        "pre_state": {
            "n_clusters": pre_n_clusters,
            "n_anchors": len(pre_anchors_snapshot),
            "topology_nodes": pre_sig["nodes"],
        },
        "recovery": {
            "final_topology_similarity": final_topo_sim,
            "mean_topology_similarity_late": mean_topo_sim,
            "first_recovery_tick": first_recovery_tick,
            "separation_recovered": separation_recovered,
            "final_n_clusters": final_n_clusters,
            "mean_migration_rate_late": mean_mig_rate,
        },
        "recovery_log": recovery_log,
        "claim_1_evaluated": bool(perturbation_type == "anchor_pruning" and mean_topo_sim > 0.50),
        "claim_2_evaluated": None,  # computed across trials
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*65}")
    print(f"  EXPERIMENT P — Identity Mapping and Reconstruction")
    print(f"  {len(SEEDS)} seeds × {len(PERTURBATION_TYPES)} perturbations = "
          f"{len(SEEDS)*len(PERTURBATION_TYPES)} trials")
    print(f"  Phase 1: {ESTABLISH_TICKS} ticks  Phase 3: {RECOVERY_TICKS} ticks")
    print(f"{'='*65}\n")

    all_results = {}
    t0 = time.time()

    for ptype in PERTURBATION_TYPES:
        print(f"  Perturbation: {ptype}")
        results = []
        for seed in SEEDS:
            print(f"    seed={seed} elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
            results.append(run_trial(seed, ptype))
        print(f"\n    Done.")
        all_results[ptype] = results

    # Save
    with open("exp_p_results.json", "w") as f:
        output = {}
        for ptype, results in all_results.items():
            output[ptype] = [
                {k: v for k, v in r.items() if k != "recovery_log"}
                for r in results
            ]
        json.dump({"experiment": "P_identity_reconstruction",
                   "parameters": {"constraint_factor": CONSTRAINT_FACTOR,
                                   "influence_strength": INFLUENCE_STRENGTH,
                                   "establish_ticks": ESTABLISH_TICKS,
                                   "recovery_ticks": RECOVERY_TICKS},
                   "results": output}, f, indent=2)
    print("  JSON → exp_p_results.json")

    # Summary
    print(f"\n{'─'*65}")
    print("RECONSTRUCTION RESULTS")
    print(f"{'─'*65}")

    for ptype in PERTURBATION_TYPES:
        results = all_results[ptype]
        topo_sims = [r["recovery"]["mean_topology_similarity_late"] for r in results]
        first_ticks = [r["recovery"]["first_recovery_tick"] for r in results
                       if r["recovery"]["first_recovery_tick"]]
        mig_rates = [r["recovery"]["mean_migration_rate_late"] for r in results
                     if r["recovery"]["mean_migration_rate_late"]]
        sep_recovered = sum(1 for r in results if r["recovery"]["separation_recovered"])
        final_clusters = [r["recovery"]["final_n_clusters"] for r in results]

        print(f"\n  {ptype}")
        print(f"    Topology similarity (late recovery):  {round(np.mean(topo_sims),3)} "
              f"± {round(np.std(topo_sims),3)}")
        print(f"    First recovery tick (sim ≥ 0.70):     "
              f"{'never' if not first_ticks else round(np.mean(first_ticks),0)}")
        print(f"    Separation recovered (dist ≥ 30):     {sep_recovered}/{len(results)}")
        print(f"    Mean migration rate (late):            "
              f"{round(np.mean(mig_rates),4) if mig_rates else 'N/A'}")
        print(f"    Final cluster count:                   "
              f"{round(np.mean(final_clusters),1)}")

    # Claim evaluation
    print(f"\n{'─'*65}")
    print("CLAIM EVALUATION")
    print(f"{'─'*65}")

    ap = all_results["anchor_pruning"]
    fr = all_results["full_reset"]

    ap_topo = np.mean([r["recovery"]["mean_topology_similarity_late"] for r in ap])
    fr_topo = np.mean([r["recovery"]["mean_topology_similarity_late"] for r in fr])
    ap_ticks = [r["recovery"]["first_recovery_tick"] for r in ap
                if r["recovery"]["first_recovery_tick"]]
    fr_ticks = [r["recovery"]["first_recovery_tick"] for r in fr
                if r["recovery"]["first_recovery_tick"]]

    print(f"\n  CLAIM 1 — Reconstruction from field traces (anchor_pruning)")
    print(f"    Prediction: topology reforms when field intact, anchors removed")
    print(f"    Result:     mean topo similarity = {ap_topo:.3f}")
    verdict1 = "SUPPORTED" if ap_topo > 0.50 else "NOT SUPPORTED"
    print(f"    Verdict:    {verdict1}")

    print(f"\n  CLAIM 2 — Field traces accelerate reconstruction vs full reset")
    print(f"    Prediction: anchor_pruning recovers faster/better than full_reset")
    print(f"    anchor_pruning topo:   {ap_topo:.3f}   (field intact)")
    print(f"    full_reset topo:       {fr_topo:.3f}   (field zeroed)")
    print(f"    anchor_pruning first recovery tick: "
          f"{'never' if not ap_ticks else round(np.mean(ap_ticks),0)}")
    print(f"    full_reset first recovery tick:     "
          f"{'never' if not fr_ticks else round(np.mean(fr_ticks),0)}")
    verdict2 = "SUPPORTED" if ap_topo > fr_topo + 0.05 else "NOT SUPPORTED"
    print(f"    Verdict:    {verdict2}")

    print(f"\n  CLAIM 3 — Reconstruction visible as transient migration elevation")
    print(f"    Prediction: migration rate high early in recovery, then stabilizes")
    for ptype in PERTURBATION_TYPES:
        early = [r["recovery_log"][:3] for r in all_results[ptype]]
        late  = [r["recovery_log"][-3:] for r in all_results[ptype]]
        early_rate = np.mean([e["migration_rate"] for run in early for e in run])
        late_rate  = np.mean([e["migration_rate"] for run in late  for e in run])
        print(f"    {ptype}: early={early_rate:.4f}  late={late_rate:.4f}  "
              f"{'↓ pattern present' if early_rate > late_rate * 1.2 else '→ flat'}")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
