"""
experiment_o2c_density.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment O Part 2c — Density Sweep
2026

WHY NOT COMPLETE GRAPH
───────────────────────
O2b showed that HOP_CLUSTER_RADIUS=2 collapses all K₂₀₀ anchors into one
cluster (hop distance=1 for all pairs). Reducing to radius=1 in a complete
graph still collapses everything — every node is 1 hop from every other.

This is not a calibration problem. It is a structural one:

  The phenomenon requires LOCALITY — that some nodes are meaningfully
  closer to some nodes than others.

  A complete graph eliminates locality entirely. Proximity-based grouping
  becomes undefined. The phenomenon cannot occur not because constraint is
  absent, but because the substrate has no spatial differentiation to group.

This reveals something important about the minimal mechanism:

  Persistent positional constraint + proximity-based grouping

  Both conditions require LOCALITY in the substrate. Constraint without
  locality cannot produce differentiated regions. Grouping without locality
  cannot produce stable separated clusters.

O2C DESIGN
───────────
Instead of the complete graph control, O2c sweeps graph density:

  p = 0.08 (sparse   — strong locality, ~16 neighbors)
  p = 0.20 (medium   — moderate locality, ~40 neighbors)
  p = 0.40 (dense    — weak locality, ~80 neighbors)
  p = 0.70 (very dense — minimal locality, ~140 neighbors)

At each density, structured vs random drift are compared.

PRE-REGISTERED EXPECTATIONS
────────────────────────────
At low density (p=0.08): strong discrimination (replicates O2b sparse result)
At medium density (p=0.20): reduced but present discrimination
At high density (p=0.40+): discrimination collapses — locality too weak

The density at which discrimination collapses is the locality threshold:
below it, graph topology provides sufficient constraint; above it, it doesn't.

GRAPH-CALIBRATED THRESHOLDS (based on O2b)
────────────────────────────────────────────
O2b found: sparse_structured medoid stability 0.544, sparse_random 0.049
Threshold set between these: C2 > 0.30 (passes structured, fails random)

C1: mean medoid hop distance ≥ 2 (more lenient than O2b's ≥3 to accommodate
    denser graphs where path lengths are shorter)
C2: medoid stability > 0.30
C3: migration rate < 0.05 (same)

SWEEP: decay_rates × event_strengths × seeds = 125 trials per (mode × density)
"""

import math, random, json, csv, time
import numpy as np
import networkx as nx
from dataclasses import dataclass
from collections import defaultdict

# ─── Constants ────────────────────────────────────────────────────────────────

N_NODES              = 200
ACTIVATION_FLOOR     = 0.15
ACTIVATION_COLLAPSE  = 0.05
MAX_ANCHORS          = 32
STABILITY_THRESHOLD  = 80
HOP_CLUSTER_RADIUS   = 2
EVENT_RATE           = 0.012
SPREAD_FACTOR        = 0.30
TICKS                = 2500
LOG_INTERVAL         = 50
UPDATE_INTERVAL      = 8

# Graph-calibrated thresholds (from O2b)
C1_MIN_HOP           = 2.0    # ≥ 2 hops (lenient for denser graphs)
C1_MAX_VARIANCE      = 2.0
C2_MEDOID_STABILITY  = 0.30   # calibrated: structured ~0.544, random ~0.049
C3_RATE_THRESHOLD    = 0.05

DENSITIES            = [0.08, 0.20, 0.40, 0.70]


# ─── Graph ────────────────────────────────────────────────────────────────────

def build_graph(n, p, seed):
    rng = random.Random(seed)
    attempt = seed
    while True:
        G = nx.erdos_renyi_graph(n, p, seed=attempt)
        if nx.is_connected(G):
            for u, v in G.edges():
                G[u][v]["weight"] = 0.5 + rng.random() * 0.5
            return G
        attempt += 1000


def hop_distances(G):
    return dict(nx.all_pairs_shortest_path_length(G))


# ─── Anchor ───────────────────────────────────────────────────────────────────

@dataclass
class Anchor:
    node: int
    strength: float
    age: int = 0
    cluster_id: int = -1

    @property
    def is_stable(self): return self.age >= STABILITY_THRESHOLD and self.strength > 0.1


# ─── Mechanics ────────────────────────────────────────────────────────────────

def propagate(G, activation, node, strength):
    activation[node] = min(1.0, activation[node] + strength)
    for nb in G.neighbors(node):
        w = G[node][nb]["weight"]
        activation[nb] = min(1.0, activation[nb] + strength * SPREAD_FACTOR * w)


def detect_anchors(G, activation):
    candidates = []
    for node in range(N_NODES):
        v = activation[node]
        if v < ACTIVATION_FLOOR: continue
        if all(activation[nb] <= v + 0.01 for nb in G.neighbors(node)):
            candidates.append({"node": node, "strength": v})
    return candidates


def drift(anchor, G, activation, mode):
    neighbors = list(G.neighbors(anchor.node))
    if not neighbors:
        anchor.age += 1
        anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02
        return
    if mode == "structured":
        best = max(neighbors, key=lambda n: activation[n])
        if activation[best] > activation[anchor.node]:
            anchor.node = best
    else:
        anchor.node = random.choice(neighbors)
    anchor.age += 1
    anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02


def cluster(anchors, hops):
    n = len(anchors)
    if not n: return []
    assignments = [-1] * n; cid = 0
    for i in range(n):
        if assignments[i] != -1: continue
        assignments[i] = cid; queue = [i]
        while queue:
            curr = queue.pop()
            for j in range(n):
                if assignments[j] != -1: continue
                d = hops[anchors[curr].node].get(anchors[j].node, 999)
                if d <= HOP_CLUSTER_RADIUS:
                    assignments[j] = cid; queue.append(j)
        cid += 1
    for i, a in enumerate(anchors): a.cluster_id = assignments[i]
    centroids = []
    for c in range(cid):
        members = [anchors[i] for i in range(n) if assignments[i] == c]
        if not members: continue
        mnodes = [a.node for a in members]
        medoid = min(mnodes, key=lambda u: sum(hops[u].get(v, 999) for v in mnodes))
        centroids.append({"id": c, "medoid": medoid,
                          "size": len(members), "member_nodes": set(mnodes)})
    return centroids


# ─── Trial ────────────────────────────────────────────────────────────────────

def run_trial(decay_rate, event_strength, seed, density, mode):
    random.seed(seed); np.random.seed(seed)

    G = build_graph(N_NODES, density, seed)
    hops = hop_distances(G)
    activation = [0.0] * N_NODES
    anchors = []
    log = []
    prev_medoids = {}
    prev_assignments = {}
    migration_log = []
    medoid_stability_log = []

    for tick in range(1, TICKS + 1):
        if random.random() < EVENT_RATE:
            node = random.randint(0, N_NODES - 1)
            propagate(G, activation, node, event_strength)

        for i in range(N_NODES):
            activation[i] *= decay_rate

        if tick % UPDATE_INTERVAL == 0:
            candidates = detect_anchors(G, activation)
            for c in candidates:
                ex = next((a for a in anchors if a.node == c["node"]), None)
                if ex:
                    ex.strength = ex.strength * 0.85 + c["strength"] * 0.15
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["node"], c["strength"]))

            for a in anchors:
                drift(a, G, activation, mode)

            anchors = [a for a in anchors if a.strength > ACTIVATION_COLLAPSE or a.age < 30]
            centroids = cluster(anchors, hops)

            current = {id(a): a.cluster_id for a in anchors}
            if tick > TICKS // 2:
                n_a = max(len(anchors), 1)
                for a in anchors:
                    aid = id(a)
                    prev = prev_assignments.get(aid, a.cluster_id)
                    if prev != a.cluster_id and prev != -1:
                        migration_log.append((tick, n_a))
            prev_assignments = current

        if tick % LOG_INTERVAL == 0:
            centroids = cluster(anchors, hops)
            hop_dists = []
            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i + 1, len(centroids)):
                        d = hops[centroids[i]["medoid"]].get(centroids[j]["medoid"], 999)
                        if d < 999: hop_dists.append(d)

            current_medoids = {c["id"]: c["medoid"] for c in centroids}
            stability = None
            if prev_medoids and current_medoids:
                matched = total = 0
                for cid, med in current_medoids.items():
                    if cid in prev_medoids:
                        total += 1
                        if prev_medoids[cid] == med: matched += 1
                if total > 0:
                    stability = matched / total
                    if tick > TICKS // 2:
                        medoid_stability_log.append(stability)
            prev_medoids = current_medoids

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "mean_hop": round(sum(hop_dists)/len(hop_dists), 3) if hop_dists else None,
                "hop_var": round(float(np.std(hop_dists)), 3) if len(hop_dists) > 1 else None,
                "medoid_stability": stability,
            })

    half = len(log) // 2; late = log[half:]

    hops_late = [e["mean_hop"] for e in late if e["mean_hop"]]
    mean_hop = round(sum(hops_late)/len(hops_late), 3) if hops_late else None
    hop_var = round(float(np.std(hops_late)), 3) if len(hops_late) > 1 else None
    c1 = (mean_hop is not None and mean_hop >= C1_MIN_HOP and
           hop_var is not None and hop_var < C1_MAX_VARIANCE)

    mean_stab = round(sum(medoid_stability_log)/len(medoid_stability_log), 4) \
                if medoid_stability_log else None
    c2 = mean_stab is not None and mean_stab > C2_MEDOID_STABILITY

    late_updates = (TICKS // 2) // UPDATE_INTERVAL
    rate = round(sum(1.0/n for _, n in migration_log) / late_updates, 6) \
           if migration_log and late_updates > 0 else 0.0
    c3 = rate < C3_RATE_THRESHOLD

    return {
        "density": density, "mode": mode,
        "params": {"decay_rate": decay_rate, "event_strength": event_strength, "seed": seed},
        "conditions": {
            "C1": {"passed": c1, "mean_hop": mean_hop, "variance": hop_var},
            "C2": {"passed": c2, "mean_stability": mean_stab},
            "C3": {"passed": c3, "rate": rate},
        },
        "all_passed": c1 and c2 and c3,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    decay_rates     = [0.75, 0.80, 0.85, 0.90, 0.95]
    event_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds           = [0, 1, 2, 3, 4]
    modes           = ["structured", "random"]
    trials          = len(decay_rates) * len(event_strengths) * len(seeds)

    print(f"\n{'='*65}")
    print(f"  EXPERIMENT O2c — Density Sweep")
    print(f"  Densities: {DENSITIES}")
    print(f"  {trials} trials per (mode × density) = {trials*len(modes)*len(DENSITIES)} total")
    print(f"  C2 threshold: {C2_MEDOID_STABILITY} (graph-calibrated from O2b)")
    print(f"{'='*65}\n")

    all_results = {}
    t0 = time.time()

    for density in DENSITIES:
        for mode in modes:
            key = f"p{density}_{mode}"
            print(f"  [{key}]")
            results = []
            n = 0
            for dr in decay_rates:
                for es in event_strengths:
                    for seed in seeds:
                        n += 1
                        print(f"    [{n:3d}/{trials}] dr={dr} es={es} seed={seed} "
                              f"elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
                        results.append(run_trial(dr, es, seed, density, mode))
            print(f"\n    Done.")
            all_results[key] = results

    # Save
    with open("exp_o2c_results.json", "w") as f:
        json.dump({
            "experiment": "O2c_density_sweep",
            "densities": DENSITIES,
            "thresholds": {"C1_min_hop": C1_MIN_HOP, "C2_stability": C2_MEDOID_STABILITY,
                           "C3_rate": C3_RATE_THRESHOLD},
            "results": {
                k: [{"params": r["params"], "conditions": r["conditions"],
                     "all_passed": r["all_passed"]}
                    for r in rlist]
                for k, rlist in all_results.items()
            }
        }, f, indent=2)
    print("  JSON → exp_o2c_results.json")

    # Summary table
    print(f"\n{'─'*65}")
    print("DENSITY SWEEP — DISCRIMINATION TABLE")
    print(f"{'─'*65}")
    print(f"{'Density':<12} {'Struct all':>10}  {'Random all':>10}  "
          f"{'C1 S/R':>10}  {'C2 stab S/R':>14}  {'C3 S/R':>10}")
    print(f"{'─'*65}")

    locality_threshold = None
    for density in DENSITIES:
        ks = f"p{density}_structured"
        kr = f"p{density}_random"
        rs = all_results[ks]; rr = all_results[kr]

        ps = sum(1 for r in rs if r["all_passed"])
        pr = sum(1 for r in rr if r["all_passed"])
        c1s = sum(1 for r in rs if r["conditions"]["C1"]["passed"])
        c1r = sum(1 for r in rr if r["conditions"]["C1"]["passed"])
        c3s = sum(1 for r in rs if r["conditions"]["C3"]["passed"])
        c3r = sum(1 for r in rr if r["conditions"]["C3"]["passed"])
        stabs = [r["conditions"]["C2"]["mean_stability"] for r in rs
                 if r["conditions"]["C2"]["mean_stability"]]
        stabr = [r["conditions"]["C2"]["mean_stability"] for r in rr
                 if r["conditions"]["C2"]["mean_stability"]]
        ms = round(np.mean(stabs), 3) if stabs else None
        mr = round(np.mean(stabr), 3) if stabr else None

        disc = ps - pr
        if locality_threshold is None and disc < 10:
            locality_threshold = density

        print(f"  p={density:<8} {ps:>8}/125  {pr:>8}/125  "
              f"{c1s:>4}/{c1r:<4}    "
              f"{ms if ms else 'N/A':>6}/{mr if mr else 'N/A':<6}  "
              f"{c3s:>4}/{c3r:<4}")

    print(f"\n{'─'*65}")
    if locality_threshold:
        print(f"  Locality threshold: discrimination collapses at p≈{locality_threshold}")
        print(f"  Below this density: graph topology provides sufficient positional constraint")
        print(f"  Above this density: locality degraded, structured/random indistinguishable")
    else:
        print(f"  No locality threshold found — discrimination persists across tested densities")
        print(f"  OR discrimination absent at all densities — inspect raw numbers")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
