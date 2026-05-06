"""
experiment_o2_graph.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment O Part 2 — Cross-Substrate Replication
2026

PURPOSE
───────
The minimal mechanism identified across G–O1:
  field-coupled anchor dynamics + spatial clustering

was established entirely within one physical substrate: a continuous 2D field
with Gaussian propagation, gradient detection, and Euclidean distance clustering.

A skeptic can correctly observe: all evidence so far is from one implementation.
The claim that this is a structural result — not a field-specific artifact —
requires demonstrating the phenomenon in a genuinely different substrate.

This experiment recreates the minimal two conditions in a GRAPH substrate:

  SUBSTRATE:     Erdős–Rényi sparse random graph, N=200 nodes
  PROPAGATION:   Activation spreads along edges (not Gaussian in space)
  ANCHORS:       Local activation maxima in graph (not gradient minima in field)
  DRIFT:         Anchor moves to highest-activation graph neighbor
                 (field-coupled: responds to activation landscape)
  CLUSTERING:    Connected components within hop-distance ≤ 2
                 (proximity grouping: graph hops, not Euclidean distance)

Nothing about this substrate is spatially continuous. Distances are graph hops.
Propagation is edge-weighted. Topology is adjacency-defined.

If the same three conditions pass (C1'', C2'', C3''') under graph dynamics,
the claim is substrate-agnostic. If they fail, the result is field-specific.

Both outcomes are informative. The document reports whichever occurs.

ADAPTED CONDITIONS
──────────────────
C1'' — Cluster separation stability
  Mean hop-distance between cluster medoids > 3 hops (second half of run)
  AND variance < 2.0
  (Analog to C1': spatial separation stability)

C2'' — Membership persistence
  Mean Jaccard similarity of cluster membership across consecutive log steps > 0.85
  (Analog to C2': topology persistence — cluster composition stable over time)

C3'' — Migration rate
  Anchor migrations per anchor per update < 0.05 (second half of run)
  (Identical definition to C3''' from K–O1)

COMPARISON MODES
────────────────
  graph_structured:      graph-coupled drift + hop clustering  (field-responsive)
  graph_random_walk:     random hop drift + hop clustering     (no field response)
                         Direct analog of O1's random_walk_cluster

SWEEP: decay_rate [0.75, 0.80, 0.85, 0.90, 0.95] ×
       event_strength [0.5, 0.7, 0.9, 1.1, 1.3] ×
       seeds [0-4] = 125 trials per mode
"""

import math, random, json, csv, time
import numpy as np
import networkx as nx
from dataclasses import dataclass, field as dc_field
from collections import defaultdict, deque

# ─── Graph constants ──────────────────────────────────────────────────────────

N_NODES             = 200       # graph size
EDGE_PROB           = 0.08      # Erdős–Rényi p (~16 neighbors per node)
ACTIVATION_FLOOR    = 0.15      # minimum activation to register as anchor
ACTIVATION_COLLAPSE = 0.05      # below this, anchor pruned
MAX_ANCHORS         = 32
STABILITY_THRESHOLD = 80        # ticks before anchor is "stable"
HOP_CLUSTER_RADIUS  = 2         # hops within which anchors cluster
EVENT_RATE          = 0.012     # events per tick
SPREAD_FACTOR       = 0.30      # fraction of activation spreading per edge
TICKS               = 2500
LOG_INTERVAL        = 50
UPDATE_INTERVAL     = 8         # anchor update frequency

# Adapted condition thresholds
C1_MIN_HOP_DIST     = 3.0       # minimum mean medoid-medoid distance (hops)
C1_MAX_VARIANCE     = 2.0       # maximum hop-distance variance
C2_THRESHOLD        = 0.85      # Jaccard similarity threshold
C3_RATE_THRESHOLD   = 0.05      # migration rate threshold (same as O1)


# ─── Graph construction ───────────────────────────────────────────────────────

def build_graph(seed):
    """Build a connected Erdős–Rényi random graph."""
    rng = random.Random(seed)
    np.random.seed(seed)
    while True:
        G = nx.erdos_renyi_graph(N_NODES, EDGE_PROB, seed=seed)
        if nx.is_connected(G):
            # Assign random edge weights [0.5, 1.0]
            for u, v in G.edges():
                G[u][v]["weight"] = 0.5 + rng.random() * 0.5
            return G
        seed += 1000  # retry with different seed if disconnected


def all_pairs_shortest_paths(G):
    """Precompute shortest hop distances for all pairs."""
    return dict(nx.all_pairs_shortest_path_length(G))


# ─── Anchor ───────────────────────────────────────────────────────────────────

@dataclass
class GraphAnchor:
    node: int
    strength: float
    age: int = 0
    cluster_id: int = -1

    @property
    def is_stable(self): return self.age >= STABILITY_THRESHOLD and self.strength > 0.1


# ─── Graph mechanics ──────────────────────────────────────────────────────────

def propagate_activation(G, activation, event_node, event_strength):
    """Spread activation from event_node along edges."""
    activation[event_node] = min(1.0, activation[event_node] + event_strength)
    for neighbor in G.neighbors(event_node):
        w = G[event_node][neighbor]["weight"]
        activation[neighbor] = min(1.0,
            activation[neighbor] + event_strength * SPREAD_FACTOR * w)


def decay_activation(activation, decay_rate):
    """Apply per-tick decay."""
    for node in range(N_NODES):
        activation[node] *= decay_rate


def detect_anchors_graph(G, activation):
    """Local maxima detection: node activation > all neighbors."""
    candidates = []
    for node in range(N_NODES):
        v = activation[node]
        if v < ACTIVATION_FLOOR: continue
        if all(activation[nb] <= v + 0.01 for nb in G.neighbors(node)):
            candidates.append({"node": node, "strength": v})
    return candidates


def drift_graph(anchor, G, activation, mode):
    """
    structured: move to highest-activation neighbor (field-coupled)
    random:     move to random neighbor (no field response)
    """
    neighbors = list(G.neighbors(anchor.node))
    if not neighbors:
        anchor.age += 1
        anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02
        return
    if mode == "structured":
        # Field-coupled: move toward highest activation
        best = max(neighbors, key=lambda n: activation[n])
        if activation[best] > activation[anchor.node]:
            anchor.node = best
    else:
        # Random walk: move to random neighbor
        anchor.node = random.choice(neighbors)
    anchor.age += 1
    anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02


def cluster_anchors_graph(anchors, shortest_paths):
    """Connected-component clustering by hop-distance ≤ HOP_CLUSTER_RADIUS."""
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
                dist = shortest_paths[anchors[curr].node].get(anchors[j].node, 999)
                if dist <= HOP_CLUSTER_RADIUS:
                    assignments[j] = cid; queue.append(j)
        cid += 1
    for i, a in enumerate(anchors): a.cluster_id = assignments[i]

    centroids = []
    for c in range(cid):
        members = [anchors[i] for i in range(n) if assignments[i] == c]
        if not members: continue
        # Medoid: node minimizing total hop-distance to other members in cluster
        member_nodes = [a.node for a in members]
        medoid = min(member_nodes,
                     key=lambda u: sum(shortest_paths[u].get(v, 999)
                                       for v in member_nodes))
        centroids.append({
            "id": c,
            "medoid": medoid,
            "size": len(members),
            "member_nodes": set(member_nodes),
        })
    return centroids


# ─── Topology analog for graph (Jaccard) ─────────────────────────────────────

def cluster_jaccard(prev_centroids, curr_centroids):
    """
    Mean Jaccard similarity of cluster membership between consecutive steps.
    Matches clusters by medoid proximity (closest medoid).
    """
    if not prev_centroids or not curr_centroids: return None
    sims = []
    for pc in prev_centroids:
        best_sim = 0.0
        for cc in curr_centroids:
            inter = len(pc["member_nodes"] & cc["member_nodes"])
            union = len(pc["member_nodes"] | cc["member_nodes"])
            sim = inter / union if union > 0 else 0.0
            if sim > best_sim: best_sim = sim
        sims.append(best_sim)
    return round(sum(sims) / len(sims), 4) if sims else None


# ─── Trial ────────────────────────────────────────────────────────────────────

def run_trial(decay_rate, event_strength, seed, mode):
    random.seed(seed); np.random.seed(seed)

    G = build_graph(seed)
    shortest_paths = all_pairs_shortest_paths(G)
    activation = [0.0] * N_NODES
    anchors = []
    log = []
    prev_centroids = None
    prev_assignments = {}
    migration_log = []

    for tick in range(1, TICKS + 1):
        # Events — random node activation
        if random.random() < EVENT_RATE:
            event_node = random.randint(0, N_NODES - 1)
            propagate_activation(G, activation, event_node, event_strength)

        decay_activation(activation, decay_rate)

        if tick % UPDATE_INTERVAL == 0:
            # Anchor detection
            candidates = detect_anchors_graph(G, activation)
            for c in candidates:
                existing = next((a for a in anchors if a.node == c["node"]), None)
                if existing:
                    existing.strength = existing.strength * 0.85 + c["strength"] * 0.15
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(GraphAnchor(c["node"], c["strength"]))

            # Drift
            for a in anchors:
                drift_graph(a, G, activation, mode)

            anchors = [a for a in anchors
                       if a.strength > ACTIVATION_COLLAPSE or a.age < 30]

            # Clustering
            centroids = cluster_anchors_graph(anchors, shortest_paths)

            # Migration tracking (second half only)
            current_assignments = {id(a): a.cluster_id for a in anchors}
            if tick > TICKS // 2:
                n_a = max(len(anchors), 1)
                for a in anchors:
                    aid = id(a)
                    prev = prev_assignments.get(aid, a.cluster_id)
                    if prev != a.cluster_id and prev != -1:
                        migration_log.append((tick, n_a))
            prev_assignments = current_assignments

        # Logging
        if tick % LOG_INTERVAL == 0:
            centroids = cluster_anchors_graph(anchors, shortest_paths)

            # Inter-cluster hop distances
            hop_distances = []
            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i + 1, len(centroids)):
                        d = shortest_paths[centroids[i]["medoid"]].get(
                            centroids[j]["medoid"], 999)
                        if d < 999: hop_distances.append(d)

            # Jaccard similarity vs previous
            jaccard = None
            if prev_centroids is not None:
                jaccard = cluster_jaccard(prev_centroids, centroids)
            prev_centroids = centroids

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "mean_hop_distance": round(sum(hop_distances)/len(hop_distances), 2)
                                     if hop_distances else None,
                "hop_variance": round(float(np.std(hop_distances)), 2)
                                if len(hop_distances) > 1 else None,
                "mean_jaccard": jaccard,
                "field_energy": round(sum(activation), 4),
            })

    # ── Condition evaluation ──────────────────────────────────────────────────
    half = len(log) // 2
    late = log[half:]

    # C1'' — separation stability (hop distance)
    hop_dists = [e["mean_hop_distance"] for e in late if e["mean_hop_distance"]]
    mean_hop = round(sum(hop_dists)/len(hop_dists), 2) if hop_dists else None
    hop_var = round(float(np.std(hop_dists)), 2) if len(hop_dists) > 1 else None
    c1 = (mean_hop is not None and mean_hop > C1_MIN_HOP_DIST and
           hop_var is not None and hop_var < C1_MAX_VARIANCE)

    # C2'' — membership persistence (Jaccard)
    jaccards = [e["mean_jaccard"] for e in late if e["mean_jaccard"] is not None]
    mean_jac = round(sum(jaccards)/len(jaccards), 4) if jaccards else None
    c2 = mean_jac is not None and mean_jac > C2_THRESHOLD

    # C3'' — migration rate (identical to O1)
    late_updates = (TICKS // 2) // UPDATE_INTERVAL
    rate = round(sum(1.0/n for _, n in migration_log) / late_updates, 6) \
           if migration_log and late_updates > 0 else 0.0
    c3 = rate < C3_RATE_THRESHOLD

    return {
        "mode": mode,
        "params": {"decay_rate": decay_rate, "event_strength": event_strength,
                   "seed": seed},
        "conditions": {
            "C1_double_prime": {"passed": c1, "mean_hop": mean_hop, "variance": hop_var},
            "C2_double_prime": {"passed": c2, "mean_jaccard": mean_jac},
            "C3_double_prime": {"passed": c3, "rate": rate},
        },
        "all_passed": c1 and c2 and c3,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    decay_rates     = [0.75, 0.80, 0.85, 0.90, 0.95]
    event_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds           = [0, 1, 2, 3, 4]
    modes           = ["graph_structured", "graph_random_walk"]
    trials          = len(decay_rates) * len(event_strengths) * len(seeds)

    print(f"\n{'='*65}")
    print(f"  EXPERIMENT O2 — Cross-Substrate Replication (Graph Dynamics)")
    print(f"  N={N_NODES} nodes, p={EDGE_PROB}, {trials} trials per mode")
    print(f"  Conditions: C1''(hop sep) + C2''(Jaccard) + C3''(rate)")
    print(f"{'='*65}\n")

    all_results = {}
    t0 = time.time()

    for mode in modes:
        print(f"  Mode: {mode}")
        results = []
        n = 0
        for dr in decay_rates:
            for es in event_strengths:
                for seed in seeds:
                    n += 1
                    print(f"    [{n:3d}/{trials}] dr={dr} es={es} seed={seed} "
                          f"elapsed={time.time()-t0:.0f}s", end="\r", flush=True)
                    results.append(run_trial(dr, es, seed, mode))
        print(f"\n    Done.")
        all_results[mode] = results

    # Save
    with open("exp_o2_results.json", "w") as f:
        json.dump({
            "experiment": "O2_cross_substrate_graph",
            "substrate": "Erdos-Renyi random graph",
            "n_nodes": N_NODES, "edge_prob": EDGE_PROB,
            "conditions": {
                "C1_min_hop": C1_MIN_HOP_DIST, "C1_max_var": C1_MAX_VARIANCE,
                "C2_threshold": C2_THRESHOLD, "C3_rate_threshold": C3_RATE_THRESHOLD,
            },
            "results": {
                mode: [{"params": r["params"], "conditions": r["conditions"],
                        "all_passed": r["all_passed"]}
                       for r in rlist]
                for mode, rlist in all_results.items()
            }
        }, f, indent=2)
    print("  JSON → exp_o2_results.json")

    # CSV
    for mode, rlist in all_results.items():
        fname = f"exp_o2_{mode}.csv"
        with open(fname, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([""] + [f"es={es}" for es in event_strengths])
            for dr in decay_rates:
                row = [f"dr={dr}"]
                for es in event_strengths:
                    cell_results = [r for r in rlist
                                    if r["params"]["decay_rate"] == dr
                                    and r["params"]["event_strength"] == es]
                    passed = sum(1 for r in cell_results if r["all_passed"])
                    row.append(f"{passed}/{len(cell_results)}")
                w.writerow(row)
        print(f"  CSV  → {fname}")

    # Summary
    print(f"\n{'─'*65}")
    print("CROSS-SUBSTRATE RESULTS")
    print(f"{'─'*65}")
    for mode in modes:
        results = all_results[mode]
        passed = sum(1 for r in results if r["all_passed"])
        c1s = [r["conditions"]["C1_double_prime"]["passed"] for r in results]
        c2s = [r["conditions"]["C2_double_prime"]["passed"] for r in results]
        c3s = [r["conditions"]["C3_double_prime"]["passed"] for r in results]
        rates = [r["conditions"]["C3_double_prime"]["rate"] for r in results]
        jacs  = [r["conditions"]["C2_double_prime"]["mean_jaccard"] for r in results
                 if r["conditions"]["C2_double_prime"]["mean_jaccard"]]
        hops  = [r["conditions"]["C1_double_prime"]["mean_hop"] for r in results
                 if r["conditions"]["C1_double_prime"]["mean_hop"]]
        label = {
            "graph_structured":   "field-coupled drift → hop clustering",
            "graph_random_walk":  "random hop drift → hop clustering",
        }[mode]
        print(f"\n  {mode}")
        print(f"    ({label})")
        print(f"    Passed: {passed}/125")
        print(f"    C1'' (hop sep):   {sum(c1s)}/125  mean_hop={round(np.mean(hops),2) if hops else 'N/A'}")
        print(f"    C2'' (Jaccard):   {sum(c2s)}/125  mean_jac={round(np.mean(jacs),4) if jacs else 'N/A'}")
        print(f"    C3'' (rate):      {sum(c3s)}/125  mean_rate={round(np.mean(rates),4)}")

    # Cross-substrate verdict
    gs_passed = sum(1 for r in all_results["graph_structured"] if r["all_passed"])
    gr_passed = sum(1 for r in all_results["graph_random_walk"] if r["all_passed"])

    print(f"\n{'─'*65}")
    print("VERDICT")
    print(f"{'─'*65}")
    print(f"  graph_structured:   {gs_passed}/125")
    print(f"  graph_random_walk:  {gr_passed}/125")

    if gs_passed >= 30 and gr_passed < gs_passed * 0.4:
        print(f"\n  → REPLICATION CONFIRMED")
        print(f"     Phenomenon emerges in graph substrate under the same two conditions.")
        print(f"     Field-responsive motion + proximity clustering is substrate-agnostic")
        print(f"     within the tested range.")
    elif gs_passed >= 30 and gr_passed >= gs_passed * 0.4:
        print(f"\n  → PARTIAL REPLICATION — null model not suppressed")
        print(f"     Graph substrate produces phenomenon but random walk also passes.")
        print(f"     Field-responsiveness may not be required in graph dynamics.")
    elif gs_passed < 30:
        print(f"\n  → REPLICATION FAILED")
        print(f"     Graph substrate does not reproduce the phenomenon.")
        print(f"     Result is likely field-specific, not substrate-agnostic.")
    else:
        print(f"\n  → INCONCLUSIVE — interpret raw numbers directly.")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
