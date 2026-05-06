"""
experiment_h_null_model.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment H — Null Model Control
2026

PURPOSE
───────
Experiment G found spontaneous multi-basin emergence across all 125 parameter
combinations. This raises the question: are the specific physics doing the
work, or is the measurement finding structure it built in?

This experiment replaces three structured mechanisms with random equivalents:

  1. Anchor detection — gradient-based local maxima detection
     → replaced with random anchor placement anywhere in the field

  2. Anchor drift — movement toward field gradient minima
     → replaced with random walk (no directional bias)

  3. Cluster assignment — spatial proximity (connected components)
     → replaced with random cluster assignment (anchors assigned randomly
        to one of K clusters)

All other parameters are identical to Experiment G.

If Experiment G's conditions still pass under null mechanics:
  → the result is a measurement artifact, not a physical phenomenon.

If conditions fail:
  → the specific mechanisms are doing real work.
  → Experiment G's result is not explained by measurement bias alone.

SAME CONDITIONS AS EXPERIMENT G (defined prior to execution)
─────────────────────────────────────────────────────────────
C1 — Spontaneous basin formation: separation fraction > 0.40
C2 — Topological persistence: mean within-cluster similarity > 0.70
C3 — Co-existence without merger: C1 + C2 + at least 1 migration

SAME PARAMETER SWEEP
─────────────────────
constraint_factor  : [0.75, 0.80, 0.85, 0.90, 0.95]
influence_strength : [0.5, 0.7, 0.9, 1.1, 1.3]
seeds              : 0–4

OUTPUT
──────
  exp_h_regime_map.json
  exp_h_regime_map.csv
  exp_h_comparison.json   — direct comparison with Experiment G
"""

import math, random, json, csv, time
import numpy as np
from dataclasses import dataclass
from scipy.spatial.distance import cdist
from collections import defaultdict

# ─── Physics constants — identical to Experiment G ────────────────────────────

GAUSSIAN_SIGMA      = 18.0
WAVE_SPEED          = 1.8
WAVE_DECAY          = 0.015
WAVE_FIELD_DECAY    = 0.995
ANCHOR_MIN_STRENGTH = 0.15
ANCHOR_COLLAPSE     = 0.05
EDGE_REPEL          = 8
MAX_ANCHORS         = 32
STABILITY_THRESHOLD = 80
TOPOLOGY_EDGE_DIST  = 55.0
EVENT_RATE          = 0.012
FIELD_W, FIELD_H    = 160, 120
TICKS               = 2500
LOG_INTERVAL        = 50
NULL_K_CLUSTERS     = 2   # number of random clusters to assign anchors to


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


# ─── NULL MECHANISM 1 — Random anchor placement ───────────────────────────────
# Replaces: gradient-based local maxima detection
# Anchors are placed at random positions regardless of field structure.

def null_detect_anchors(field, n_anchors=4):
    """Place anchors randomly. No gradient, no local maxima detection."""
    candidates = []
    for _ in range(n_anchors):
        x = float(random.randint(EDGE_REPEL, field.w - EDGE_REPEL))
        y = float(random.randint(EDGE_REPEL, field.h - EDGE_REPEL))
        strength = field[x, y]   # still read field strength at position
        if strength > ANCHOR_COLLAPSE:
            candidates.append({"x": x, "y": y, "strength": strength})
    return candidates


# ─── NULL MECHANISM 2 — Random anchor drift ───────────────────────────────────
# Replaces: gradient-following drift toward field minima
# Anchors perform a random walk with no directional bias.

def null_drift_anchor(anchor, field, step=1.5):
    """Random walk. No gradient computation."""
    dx = random.uniform(-step, step)
    dy = random.uniform(-step, step)
    anchor.x = max(EDGE_REPEL, min(field.w - EDGE_REPEL, anchor.x + dx))
    anchor.y = max(EDGE_REPEL, min(field.h - EDGE_REPEL, anchor.y + dy))
    fv = field[int(anchor.x), int(anchor.y)]
    anchor.strength = anchor.strength * 0.98 + fv * 0.02
    anchor.age += 1


# ─── NULL MECHANISM 3 — Random cluster assignment ─────────────────────────────
# Replaces: spatial proximity connected-component clustering
# Anchors are assigned randomly to one of K clusters.

def null_cluster_anchors(anchors, k=NULL_K_CLUSTERS):
    """Assign cluster_id randomly. No spatial proximity used."""
    for a in anchors:
        a.cluster_id = random.randint(0, k-1)
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


# ─── Topology signature (unchanged from Experiment G) ────────────────────────

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
    try:
        lap_eigs = sorted([round(float(e), 6) for e in np.linalg.eigvalsh(L)])
    except:
        lap_eigs = []
    parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b): parent[find(a)] = find(b)
    for i in range(n):
        for j in range(i+1, n):
            if adj[i, j]: union(i, j)
    components = len(set(find(i) for i in range(n)))
    return {
        "nodes": n, "edges": edge_count,
        "density": round(density, 4), "components": components,
        "laplacian_eigenvalues": lap_eigs,
        "mean_strength": round(float(np.mean([a.strength for a in anchors])), 4),
        "stable_count": sum(1 for a in anchors if a.is_stable)
    }


def compare_topology(s1, s2):
    if s1["nodes"] == 0 and s2["nodes"] == 0: return 1.0
    if s1["nodes"] == 0 or s2["nodes"] == 0: return 0.0
    e1 = s1["laplacian_eigenvalues"]; e2 = s2["laplacian_eigenvalues"]
    ml = max(len(e1), len(e2))
    e1p = np.array(e1 + [0.0]*(ml-len(e1))); e2p = np.array(e2 + [0.0]*(ml-len(e2)))
    eig_score = math.exp(-float(np.linalg.norm(e1p-e2p)) * 0.15)
    c1, c2 = s1["components"], s2["components"]
    cluster_score = 1.0 - abs(c1-c2)/max(c1, c2, 1)
    density_score = 1.0 - abs(s1["density"]-s2["density"])
    node_score = min(s1["nodes"], s2["nodes"])/max(s1["nodes"], s2["nodes"])
    return round(0.50*eig_score + 0.20*cluster_score + 0.15*density_score + 0.15*node_score, 4)


# ─── Single trial (null mechanics) ───────────────────────────────────────────

def run_null_trial(constraint_factor, influence_strength, seed,
                   ticks=TICKS, log_interval=LOG_INTERVAL):
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    log = []
    prev_cluster_sigs = {}
    migrations = []
    prev_assignments = {}

    for tick in range(1, ticks+1):
        # Background noise — identical to Experiment G
        if random.random() < EVENT_RATE:
            ex = EDGE_REPEL + random.random()*(FIELD_W - EDGE_REPEL*2)
            ey = EDGE_REPEL + random.random()*(FIELD_H - EDGE_REPEL*2)
            apply_gaussian(gauss_field, ex, ey, influence_strength)

        # Wave propagation — identical to Experiment G
        wave_field.reset()
        live = []
        for w in waves:
            age = tick - w["born"]
            if age < 300:
                cx, cy = int(w["x"]), int(w["y"])
                r = WAVE_SPEED * age
                scan = int(r + WAVE_SPEED*10)
                ys = np.arange(max(0, cy-scan), min(FIELD_H, cy+scan))
                xs = np.arange(max(0, cx-scan), min(FIELD_W, cx+scan))
                if len(xs) and len(ys):
                    yy, xx = np.meshgrid(ys, xs, indexing="ij")
                    dist = np.sqrt(((xx-cx)**2 + (yy-cy)**2).astype(np.float32))
                    phase = dist - r
                    mask = np.abs(phase) < WAVE_SPEED*8
                    amp = np.where(mask,
                        0.3*np.cos(phase*0.25)*np.exp(-WAVE_DECAY*dist)*np.exp(-age*0.008), 0.0)
                    np.add.at(wave_field.data, (yy*FIELD_W+xx).ravel(), amp.ravel().astype(np.float32))
                live.append(w)
        waves = live

        gauss_field.decay(constraint_factor)
        wave_field.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss_field)
        combined.add_field(wave_field)

        # Anchor update — NULL MECHANICS
        if tick % 8 == 0:
            # NULL 1: random placement instead of gradient detection
            candidates = null_detect_anchors(combined, n_anchors=4)
            for c in candidates:
                nearby = next(
                    (a for a in anchors if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2) < 18),
                    None)
                if nearby:
                    nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                    nearby.x = nearby.x*0.95 + c["x"]*0.05
                    nearby.y = nearby.y*0.95 + c["y"]*0.05
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["x"], c["y"], c["strength"]))

            # NULL 2: random drift instead of gradient following
            for a in anchors:
                null_drift_anchor(a, combined)

            anchors = [a for a in anchors if a.strength > ANCHOR_COLLAPSE or a.age < 30]

            # NULL 3: random cluster assignment instead of spatial proximity
            centroids = null_cluster_anchors(anchors, k=NULL_K_CLUSTERS)

            # Track migrations (same logic — but now migration = random reassignment)
            current_assignments = {id(a): a.cluster_id for a in anchors}
            for a in anchors:
                aid = id(a)
                prev = prev_assignments.get(aid, a.cluster_id)
                if prev != a.cluster_id and prev != -1:
                    migrations.append({"tick": tick, "from": prev, "to": a.cluster_id})
            prev_assignments = current_assignments

        # Logging — identical to Experiment G
        if tick % log_interval == 0:
            centroids = null_cluster_anchors(anchors, k=NULL_K_CLUSTERS)
            n_clusters = len(centroids)
            cluster_distances = []
            within_sims = []

            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i+1, len(centroids)):
                        ci, cj = centroids[i], centroids[j]
                        d = math.sqrt((ci["cx"]-cj["cx"])**2 + (ci["cy"]-cj["cy"])**2)
                        cluster_distances.append(round(d, 2))

            for c in centroids:
                members = [a for a in anchors if a.cluster_id == c["id"]]
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
                "cluster_count": n_clusters,
                "mean_cluster_distance": round(sum(cluster_distances)/len(cluster_distances), 2)
                                         if cluster_distances else None,
                "distance_variance": round(float(np.std(cluster_distances)), 2)
                                     if len(cluster_distances) > 1 else None,
                "mean_within_similarity": round(sum(within_sims)/len(within_sims), 4)
                                          if within_sims else None,
                "field_energy": round(combined.total_energy(), 4),
                "migrations_total": len(migrations),
            })

    # Condition evaluation — identical thresholds to Experiment G
    half = len(log)//2
    late = log[half:]

    multi_ticks = sum(1 for e in late if e["cluster_count"] >= 2)
    separation_fraction = multi_ticks / len(late) if late else 0.0
    distances = [e["mean_cluster_distance"] for e in late if e["mean_cluster_distance"]]
    mean_dist = round(sum(distances)/len(distances), 2) if distances else None
    dist_var = round(float(np.std(distances)), 2) if len(distances) > 1 else None
    c1 = separation_fraction > 0.40

    sims = [e["mean_within_similarity"] for e in late if e["mean_within_similarity"]]
    mean_sim = round(sum(sims)/len(sims), 4) if sims else None
    c2 = mean_sim is not None and mean_sim > 0.70

    n_migrations = len(migrations)
    c3 = c1 and c2 and n_migrations > 0

    if c1 and c2 and dist_var is not None and dist_var < 6.0:
        regime = "stable_coexistence"
    elif c1 and c2 and dist_var is not None and dist_var >= 6.0:
        regime = "oscillatory_exchange"
    elif c1 and not c2:
        regime = "transient_separation"
    elif not c1 and c2:
        regime = "single_stable_basin"
    else:
        regime = "no_separation"

    return {
        "params": {
            "constraint_factor": constraint_factor,
            "influence_strength": influence_strength,
            "seed": seed,
        },
        "conditions": {
            "C1_spontaneous_formation": {
                "passed": c1,
                "separation_fraction": round(separation_fraction, 3),
                "mean_inter_cluster_distance": mean_dist,
                "distance_variance": dist_var,
            },
            "C2_topological_persistence": {
                "passed": c2,
                "mean_within_similarity": mean_sim,
                "threshold": 0.70,
            },
            "C3_coexistence_without_merger": {
                "passed": c3,
                "migration_events": n_migrations,
            },
        },
        "regime": regime,
        "all_passed": c1 and c2 and c3,
        "log": log,
        "migrations": migrations,
    }


# ─── Parameter sweep ──────────────────────────────────────────────────────────

def run_null_sweep():
    constraint_factors  = [0.75, 0.80, 0.85, 0.90, 0.95]
    influence_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds               = [0, 1, 2, 3, 4]

    total = len(constraint_factors) * len(influence_strengths) * len(seeds)
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT H — Null Model Control")
    print(f"  Three structured mechanics replaced with random equivalents")
    print(f"  {total} trials — identical conditions and sweep to Experiment G")
    print(f"{'='*60}\n")

    regime_map = []
    t0 = time.time()
    trial_n = 0

    for cf in constraint_factors:
        for ist in influence_strengths:
            cell_results = []
            for seed in seeds:
                trial_n += 1
                print(f"  [{trial_n:3d}/{total}] cf={cf}  is={ist}  seed={seed}  "
                      f"elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
                result = run_null_trial(cf, ist, seed)
                cell_results.append(result)

            regimes = [r["regime"] for r in cell_results]
            regime_counts = defaultdict(int)
            for r in regimes: regime_counts[r] += 1
            dominant_regime = max(regime_counts, key=regime_counts.get)
            all_passed_count = sum(1 for r in cell_results if r["all_passed"])
            mean_sep = round(np.mean([
                r["conditions"]["C1_spontaneous_formation"]["separation_fraction"]
                for r in cell_results]), 3)
            sims = [r["conditions"]["C2_topological_persistence"]["mean_within_similarity"]
                    for r in cell_results
                    if r["conditions"]["C2_topological_persistence"]["mean_within_similarity"]]
            mean_topo = round(np.mean(sims), 4) if sims else None

            regime_map.append({
                "constraint_factor": cf,
                "influence_strength": ist,
                "dominant_regime": dominant_regime,
                "regime_counts": dict(regime_counts),
                "all_conditions_passed": all_passed_count,
                "trials": len(seeds),
                "mean_separation_fraction": mean_sep,
                "mean_topology_similarity": mean_topo,
            })

    print(f"\n\n  Sweep complete. {total} trials in {time.time()-t0:.1f}s")

    # ── Save ──────────────────────────────────────────────────────────────────
    with open("exp_h_regime_map.json", "w") as f:
        json.dump({
            "experiment": "H_null_model_control",
            "null_mechanics": [
                "anchor_detection: random placement (no gradient)",
                "anchor_drift: random walk (no directional bias)",
                "cluster_assignment: random (no spatial proximity)",
            ],
            "identical_to_G": {
                "conditions": True,
                "parameter_sweep": True,
                "seeds": True,
                "field_physics": True,
            },
            "regime_map": regime_map,
        }, f, indent=2)
    print("  JSON → exp_h_regime_map.json")

    with open("exp_h_regime_map.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([""] + [f"is={ist}" for ist in influence_strengths])
        for cf in constraint_factors:
            row = [f"cf={cf}"]
            for ist in influence_strengths:
                cell = next(c for c in regime_map
                            if c["constraint_factor"]==cf and c["influence_strength"]==ist)
                row.append(f"{cell['dominant_regime']} ({cell['all_conditions_passed']}/{cell['trials']})")
            w.writerow(row)
    print("  CSV  → exp_h_regime_map.csv")

    # ── Print summary ──────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("NULL MODEL REGIME MAP")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in regime_map
                        if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            n = cell["all_conditions_passed"]
            total_t = cell["trials"]
            label = {
                "stable_coexistence":   "COEX",
                "oscillatory_exchange": "OSCL",
                "transient_separation": "TRNS",
                "single_stable_basin":  "SNGL",
                "no_separation":        "NONE",
            }.get(cell["dominant_regime"], "????")
            row_parts.append(f"{label}({n}/{total_t})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\nLegend: COEX=stable coexistence  OSCL=oscillatory exchange")
    print(f"        TRNS=transient separation  SNGL=single basin  NONE=no separation")

    # ── Load Experiment G for comparison ──────────────────────────────────────
    try:
        with open("exp_g_regime_map.json") as f:
            g_data = json.load(f)
        g_map = {(c["constraint_factor"], c["influence_strength"]): c
                 for c in g_data["regime_map"]}
        h_map = {(c["constraint_factor"], c["influence_strength"]): c
                 for c in regime_map}

        g_total_passed = sum(c["all_conditions_passed"] for c in g_data["regime_map"])
        h_total_passed = sum(c["all_conditions_passed"] for c in regime_map)
        g_cells_full   = sum(1 for c in g_data["regime_map"] if c["all_conditions_passed"] == 5)
        h_cells_full   = sum(1 for c in regime_map if c["all_conditions_passed"] == 5)

        comparison = {
            "experiment_g": {
                "total_trials_passed": g_total_passed,
                "cells_with_all_seeds_passed": g_cells_full,
                "total_cells": 25,
            },
            "experiment_h_null": {
                "total_trials_passed": h_total_passed,
                "cells_with_all_seeds_passed": h_cells_full,
                "total_cells": 25,
            },
            "interpretation": (
                "NULL MODEL REPLICATES G: result likely measurement artifact"
                if h_total_passed >= g_total_passed * 0.8
                else "NULL MODEL DIVERGES FROM G: structured mechanics doing real work"
            ),
            "g_mean_topology_sim": round(np.mean([
                c["mean_topology_similarity"] for c in g_data["regime_map"]
                if c["mean_topology_similarity"]]), 4),
            "h_mean_topology_sim": round(np.mean([
                c["mean_topology_similarity"] for c in regime_map
                if c["mean_topology_similarity"]]), 4),
        }

        with open("exp_h_comparison.json", "w") as f:
            json.dump(comparison, f, indent=2)
        print("  JSON → exp_h_comparison.json")

        print(f"\n{'─'*60}")
        print("COMPARISON WITH EXPERIMENT G")
        print(f"{'─'*60}")
        print(f"  G (structured):  {g_total_passed}/125 trials passed  "
              f"({g_cells_full}/25 cells full)")
        print(f"  H (null model):  {h_total_passed}/125 trials passed  "
              f"({h_cells_full}/25 cells full)")
        print(f"  G mean topology similarity: {comparison['g_mean_topology_sim']}")
        print(f"  H mean topology similarity: {comparison['h_mean_topology_sim']}")
        print(f"\n  → {comparison['interpretation']}")

    except FileNotFoundError:
        print("\n  (exp_g_regime_map.json not found — run Experiment G first for comparison)")

    print(f"\n{'='*60}")
    return regime_map


if __name__ == "__main__":
    run_null_sweep()
