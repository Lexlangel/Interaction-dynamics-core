"""
experiment_r_fixed_structures.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment R — Environmental Fixed Structures
2026

PURPOSE
───────
Q established path-dependent structural bias through accumulated interaction
weighting. The remaining gap between topology and proto-identity is relevance:
not all anchors are equal, but the mechanism so far weights by stability alone.

Rae's framing: relevance doesn't require semantic import. It can be
structurally encoded in the environment through fixed structures that create
differential affordances — some regions constrain anchor movement more than
others not because of what they mean but because of what they physically are.

The reframe:
  relevance = structural position relative to fixed environmental features

This is proto-valuation without semantics: some anchors matter more because
of where they structurally sit, not what they represent.

DESIGN
──────
Two environmental conditions:

  UNIFORM: standard field — no fixed structures, uniform constraint
  STRUCTURED: fixed high-energy regions that don't decay, embedded in field

Fixed structures: three Gaussian "pillars" at stable field positions that
resist decay. They don't move, don't grow, just persist. The normal field
decays; these remain. Anchors near pillars sit in a permanently energized
region — more stable, reinforced by the memory field faster.

PREDICTIONS (pre-registered)
─────────────────────────────
1. Anchors near fixed structures are more stable (higher is_stable rate)
2. Anchors near fixed structures accumulate more memory field energy
3. Migration rate near fixed structures is lower (structural anchoring)
4. Basin topology forms preferentially around fixed structures
5. In STRUCTURED condition: anchor stability varies systematically with
   distance from nearest fixed structure

If predictions hold:
  → fixed environmental structures create differential anchor weighting
  → some anchors are structurally privileged without semantic import
  → proto-valuation emerges from structural position alone

STRUCTURAL DISTANCE ANALYSIS
─────────────────────────────
Key metric: stability_gradient — how anchor stability varies with distance
from nearest fixed structure. If stability degrades with distance, structural
position determines influence. That's relevance-without-semantics.

PARAMETERS
──────────
Same as Q: CF=0.85, IS=1.1, with_memory condition throughout
3 fixed structures at stable field positions
10 seeds per condition
"""

import math, random, json, time
import numpy as np
from dataclasses import dataclass, field as dc_field
from scipy.spatial.distance import cdist
from collections import defaultdict

# ─── Constants ────────────────────────────────────────────────────────────────

GAUSSIAN_SIGMA       = 18.0
WAVE_FIELD_DECAY     = 0.995
ANCHOR_GRAD_THRESH   = 0.12
ANCHOR_MIN_STRENGTH  = 0.15
ANCHOR_COLLAPSE      = 0.05
DRIFT_SPEED          = 0.18
EDGE_REPEL           = 8
MAX_ANCHORS          = 32
STABILITY_THRESHOLD  = 80
CLUSTER_RADIUS       = 30.0
TOPOLOGY_EDGE_DIST   = 55.0
EVENT_RATE           = 0.012
FIELD_W, FIELD_H     = 160, 120
TICKS                = 2500
LOG_INTERVAL         = 50

CONSTRAINT_FACTOR    = 0.85
INFLUENCE_STRENGTH   = 1.1

# Memory field
MEMORY_REINFORCE     = 0.002
MEMORY_SIGMA_MULT    = 1.5
MEMORY_DECAY         = 0.9995
MEMORY_WEIGHT        = 0.15

# Fixed structures — three pillars at stable positions
PILLAR_STRENGTH      = 0.35   # fixed energy level (above ANCHOR_MIN_STRENGTH)
PILLAR_SIGMA         = 12.0   # narrower than events — more localized
PILLAR_POSITIONS     = [      # (x, y) — spread across field
    (40,  40),
    (120, 40),
    (80,  85),
]

SEEDS                = list(range(10))
DISTANCE_BINS        = [0, 20, 40, 60, 80, 999]  # distance from nearest pillar


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


def build_pillar_field(w, h):
    """Create a fixed field with three persistent pillars."""
    pillar_field = Field(w, h)
    for px, py in PILLAR_POSITIONS:
        apply_gaussian(pillar_field, px, py, PILLAR_STRENGTH, sigma=PILLAR_SIGMA)
    return pillar_field


def dist_to_nearest_pillar(x, y):
    """Euclidean distance to nearest fixed structure."""
    return min(math.sqrt((x-px)**2 + (y-py)**2) for px, py in PILLAR_POSITIONS)


def pillar_bin(x, y):
    """Which distance bin does this position fall in?"""
    d = dist_to_nearest_pillar(x, y)
    for i in range(len(DISTANCE_BINS)-1):
        if d < DISTANCE_BINS[i+1]:
            return i
    return len(DISTANCE_BINS)-2


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

    def pillar_distance(self):
        return dist_to_nearest_pillar(self.x, self.y)

    def pillar_bin(self):
        return pillar_bin(self.x, self.y)


# ─── Mechanics ────────────────────────────────────────────────────────────────

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


def reinforce_memory(memory_field, anchors):
    for a in anchors:
        if a.is_stable:
            apply_gaussian(memory_field, a.x, a.y,
                           MEMORY_REINFORCE, sigma=GAUSSIAN_SIGMA*MEMORY_SIGMA_MULT)


# ─── Topology ─────────────────────────────────────────────────────────────────

def topology_signature(anchors):
    n = len(anchors)
    if not n:
        return {"nodes":0,"laplacian_eigenvalues":[],"density":0.0,"components":0}
    positions = np.array([[a.x, a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < TOPOLOGY_EDGE_DIST) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0-dists/TOPOLOGY_EDGE_DIST, 0.0)
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
    edge_count = int(np.sum(adj)//2)
    max_edges = n*(n-1)/2
    density = edge_count/max_edges if max_edges > 0 else 0.0
    return {"nodes":n,"laplacian_eigenvalues":lap_eigs,
            "density":round(density,4),"components":components}


# ─── Trial ────────────────────────────────────────────────────────────────────

def run_trial(seed, condition):
    """condition: 'uniform' | 'structured'"""
    random.seed(seed); np.random.seed(seed)

    gauss_field  = Field(FIELD_W, FIELD_H)
    wave_field   = Field(FIELD_W, FIELD_H)
    combined     = Field(FIELD_W, FIELD_H)
    memory_field = Field(FIELD_W, FIELD_H)
    pillar_field = build_pillar_field(FIELD_W, FIELD_H) if condition=="structured" else None

    anchors = []
    prev_assignments = {}
    migration_log = []

    # Per-bin tracking: stability counts and anchor counts by distance bin
    bin_stable   = defaultdict(int)   # stable anchor appearances per bin
    bin_total    = defaultdict(int)   # total anchor appearances per bin
    bin_mig      = defaultdict(int)   # migrations per bin
    bin_mig_den  = defaultdict(int)   # anchor-updates per bin (denominator)

    log = []

    for tick in range(1, TICKS + 1):
        if random.random() < EVENT_RATE:
            ex = EDGE_REPEL + random.random()*(FIELD_W-EDGE_REPEL*2)
            ey = EDGE_REPEL + random.random()*(FIELD_H-EDGE_REPEL*2)
            apply_gaussian(gauss_field, ex, ey, INFLUENCE_STRENGTH)

        gauss_field.decay(CONSTRAINT_FACTOR)
        wave_field.reset(); wave_field.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss_field); combined.add_field(wave_field)

        # Add pillars (they don't decay — reapplied each tick)
        if pillar_field is not None:
            combined.data += pillar_field.data

        # Memory field
        memory_field.decay(MEMORY_DECAY)
        combined.data += MEMORY_WEIGHT * memory_field.data

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
            reinforce_memory(memory_field, anchors)

            # Track stability and migration by distance bin (second half only)
            if tick > TICKS // 2:
                current = {id(a): a.cluster_id for a in anchors}
                n_a = max(len(anchors), 1)
                for a in anchors:
                    b = a.pillar_bin() if condition=="structured" else 0
                    bin_total[b] += 1
                    if a.is_stable: bin_stable[b] += 1
                    bin_mig_den[b] += 1
                    aid = id(a)
                    prev = prev_assignments.get(aid, a.cluster_id)
                    if prev != a.cluster_id and prev != -1:
                        bin_mig[b] += 1
                        migration_log.append(1.0/n_a)
                prev_assignments.clear(); prev_assignments.update(current)

        if tick % LOG_INTERVAL == 0:
            centroids = s_cluster(anchors)
            sig = topology_signature(anchors)

            # Pillar proximity of stable anchors
            if condition == "structured":
                stable_dists = [a.pillar_distance() for a in anchors if a.is_stable]
                all_dists    = [a.pillar_distance() for a in anchors]
                mean_stable_dist = round(np.mean(stable_dists), 2) if stable_dists else None
                mean_all_dist    = round(np.mean(all_dists), 2) if all_dists else None
            else:
                mean_stable_dist = None; mean_all_dist = None

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "stable_count": sum(1 for a in anchors if a.is_stable),
                "topology_nodes": sig["nodes"],
                "topology_components": sig["components"],
                "memory_energy": round(memory_field.total_energy(), 4),
                "mean_stable_pillar_dist": mean_stable_dist,
                "mean_all_pillar_dist": mean_all_dist,
            })

    # Aggregate second-half metrics
    late = log[len(log)//2:]

    # Stability rate overall
    overall_stable = round(
        np.mean([e["stable_count"]/max(e["anchor_count"],1) for e in late]), 3)

    # Stability by distance bin (structured only)
    bin_stability = {}
    bin_migration_rate = {}
    if condition == "structured":
        for b in range(len(DISTANCE_BINS)-1):
            lo, hi = DISTANCE_BINS[b], DISTANCE_BINS[b+1]
            label = f"d{lo}-{hi}"
            tot = bin_total.get(b, 0)
            stab = bin_stable.get(b, 0)
            mig = bin_mig.get(b, 0)
            den = bin_mig_den.get(b, 0)
            bin_stability[label] = round(stab/tot, 3) if tot > 0 else None
            bin_migration_rate[label] = round(mig/den, 5) if den > 0 else None

    # Mean pillar distances in late period
    stable_dists = [e["mean_stable_pillar_dist"] for e in late
                    if e["mean_stable_pillar_dist"] is not None]
    all_dists    = [e["mean_all_pillar_dist"] for e in late
                    if e["mean_all_pillar_dist"] is not None]

    # Migration rate overall
    late_updates = (TICKS//2) // 8
    mig_rate = round(sum(migration_log)/max(late_updates,1), 6) if migration_log else 0.0

    return {
        "seed": seed,
        "condition": condition,
        "overall_stability_rate": overall_stable,
        "overall_migration_rate": mig_rate,
        "mean_stable_anchor_pillar_dist": round(np.mean(stable_dists),2) if stable_dists else None,
        "mean_all_anchor_pillar_dist": round(np.mean(all_dists),2) if all_dists else None,
        "bin_stability": bin_stability,
        "bin_migration_rate": bin_migration_rate,
        "late_mean_stable_count": round(np.mean([e["stable_count"] for e in late]),2),
        "late_mean_cluster_count": round(np.mean([e["cluster_count"] for e in late]),2),
        "late_memory_energy": round(np.mean([e["memory_energy"] for e in late]),2),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*65}")
    print(f"  EXPERIMENT R — Fixed Environmental Structures")
    print(f"  Pillar positions: {PILLAR_POSITIONS}")
    print(f"  {len(SEEDS)} seeds × 2 conditions = {len(SEEDS)*2} trials")
    print(f"  Key metric: stability gradient by distance from pillars")
    print(f"{'='*65}\n")

    all_results = {}
    t0 = time.time()

    for condition in ["uniform", "structured"]:
        print(f"  Condition: {condition}")
        results = []
        for seed in SEEDS:
            print(f"    seed={seed} elapsed={time.time()-t0:.1f}s", end="\r", flush=True)
            results.append(run_trial(seed, condition))
        print(f"\n    Done.")
        all_results[condition] = results

    with open("exp_r_results.json", "w") as f:
        json.dump({"experiment": "R_fixed_structures",
                   "pillar_positions": PILLAR_POSITIONS,
                   "results": all_results}, f, indent=2)
    print("  JSON → exp_r_results.json\n")

    # Summary
    print(f"{'─'*65}")
    print("CONDITION COMPARISON")
    print(f"{'─'*65}")
    for cond in ["uniform", "structured"]:
        R = all_results[cond]
        stab  = round(np.mean([r["overall_stability_rate"] for r in R]), 3)
        mig   = round(np.mean([r["overall_migration_rate"] for r in R]), 5)
        mem   = round(np.mean([r["late_memory_energy"] for r in R]), 1)
        sc    = round(np.mean([r["late_mean_stable_count"] for r in R]), 2)
        cc    = round(np.mean([r["late_mean_cluster_count"] for r in R]), 2)
        print(f"  {cond:<12}  stability={stab}  mig_rate={mig}  "
              f"memory_energy={mem}  stable_anchors={sc}  clusters={cc}")

    # Stability gradient (structured only)
    print(f"\n{'─'*65}")
    print("STABILITY GRADIENT BY PILLAR DISTANCE (structured condition)")
    print(f"{'─'*65}")
    structured_r = all_results["structured"]
    all_bins = {}
    for r in structured_r:
        for label, val in r["bin_stability"].items():
            if val is not None:
                all_bins.setdefault(label, []).append(val)

    all_mig_bins = {}
    for r in structured_r:
        for label, val in r["bin_migration_rate"].items():
            if val is not None:
                all_mig_bins.setdefault(label, []).append(val)

    for label in sorted(all_bins.keys()):
        stab = round(np.mean(all_bins[label]), 3) if all_bins.get(label) else None
        mig  = round(np.mean(all_mig_bins[label]), 5) if all_mig_bins.get(label) else None
        print(f"  {label:<12}  stability={stab}  mig_rate={mig}")

    # Proximity of stable vs all anchors
    print(f"\n{'─'*65}")
    print("STABLE ANCHOR PROXIMITY TO PILLARS")
    print(f"{'─'*65}")
    stable_dists = [r["mean_stable_anchor_pillar_dist"] for r in structured_r
                    if r["mean_stable_anchor_pillar_dist"]]
    all_dists    = [r["mean_all_anchor_pillar_dist"] for r in structured_r
                    if r["mean_all_anchor_pillar_dist"]]
    if stable_dists and all_dists:
        print(f"  Mean distance stable anchors → nearest pillar: {round(np.mean(stable_dists),2)}")
        print(f"  Mean distance all anchors    → nearest pillar: {round(np.mean(all_dists),2)}")
        gap = round(np.mean(all_dists) - np.mean(stable_dists), 2)
        print(f"  Gap (all - stable):                            {gap}")
        if gap > 3:
            verdict = "PROXIMITY BIAS CONFIRMED — stable anchors cluster near fixed structures"
        elif gap > 1:
            verdict = "WEAK PROXIMITY BIAS — directional but marginal"
        else:
            verdict = "NO PROXIMITY BIAS — stable anchors not preferentially near pillars"
        print(f"\n  → {verdict}")

    # Verdict
    print(f"\n{'─'*65}")
    print("PROTO-VALUATION VERDICT")
    print(f"{'─'*65}")
    u_stab = np.mean([r["overall_stability_rate"] for r in all_results["uniform"]])
    s_stab = np.mean([r["overall_stability_rate"] for r in all_results["structured"]])
    gradient_present = len(all_bins) > 1 and (
        max(np.mean(v) for v in all_bins.values()) -
        min(np.mean(v) for v in all_bins.values()) > 0.05)

    print(f"  Structured vs uniform stability: {round(s_stab,3)} vs {round(u_stab,3)}")
    print(f"  Stability gradient across bins:  {'YES' if gradient_present else 'NO'}")

    if gradient_present and gap > 3:
        print(f"\n  → PROTO-VALUATION EMERGENT")
        print(f"     Structural position determines anchor influence.")
        print(f"     Relevance without semantics confirmed at structural layer.")
    elif gradient_present:
        print(f"\n  → PARTIAL — gradient present, proximity bias marginal")
    else:
        print(f"\n  → NOT CONFIRMED — no systematic stability gradient found")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
