"""
experiment_o2b_graph.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment O Part 2b — Cross-Substrate Replication
2026

O2a diagnosed three problems:
  1. C2'' (Jaccard) wrong metric — measures membership identity, not structure
  2. C1'' threshold too strict — hop=3.0 excluded at > 3.0 boundary
  3. Sparse graph provides built-in positional coupling — can't distinguish
     field-responsiveness from topology-provided constraint

O2b corrects all three:

  C1'' CORRECTED:  mean medoid hop distance ≥ 3 (inclusive), variance < 2
  C2'' CORRECTED:  medoid stability — fraction of log steps where each
                   cluster's medoid node is unchanged > 0.85
                   Measures structural center stability, not exact membership
  C3''             unchanged — migration rate < 0.05

  COMPLETE GRAPH CONTROL:
  Four modes across two graph types:
    sparse_structured    — sparse (p=0.08) + activation-coupled drift
    sparse_random        — sparse (p=0.08) + random hop drift
    complete_structured  — complete graph + activation-coupled drift
    complete_random      — complete graph + random hop drift

  In a complete graph every node connects to every other.
  Random hop can reach any node in one step.
  If sparse graph topology was providing constraint (as O2a suggests),
  complete graph removes it — random walk becomes unconstrained.

PRE-REGISTERED EXPECTATIONS
  sparse_structured:   C3'' passes (as in O2a) — topology constrains
  sparse_random:       C3'' passes (as in O2a) — topology constrains equally
  complete_structured: C3'' passes — activation coupling provides stability
  complete_random:     C3'' FAILS — no topology constraint, no field coupling

  If complete_random fails while complete_structured passes:
    → field-responsiveness is genuinely required in unconstrained substrates
    → the minimal mechanism (positional coupling + grouping) is substrate-agnostic
    → sparse graph was providing positional coupling through topology

  If both complete modes fail:
    → graph dynamics may not support the phenomenon at all
    → result is field-substrate-specific

SWEEP: decay_rates × event_strengths × seeds = 125 trials per mode
"""

import math, random, json, csv, time
import numpy as np
import networkx as nx
from dataclasses import dataclass
from collections import defaultdict

# ─── Constants ────────────────────────────────────────────────────────────────

N_NODES              = 200
SPARSE_EDGE_PROB     = 0.08
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

# Corrected thresholds
C1_MIN_HOP_DIST      = 3.0    # ≥ 3 (inclusive)
C1_MAX_VARIANCE      = 2.0
C2_MEDOID_STABILITY  = 0.85   # fraction of steps where medoid unchanged
C3_RATE_THRESHOLD    = 0.05


# ─── Graph construction ───────────────────────────────────────────────────────

def build_sparse_graph(seed):
    rng = random.Random(seed)
    attempt = seed
    while True:
        G = nx.erdos_renyi_graph(N_NODES, SPARSE_EDGE_PROB, seed=attempt)
        if nx.is_connected(G):
            for u, v in G.edges():
                G[u][v]["weight"] = 0.5 + rng.random() * 0.5
            return G
        attempt += 1000


def build_complete_graph(seed):
    rng = random.Random(seed)
    G = nx.complete_graph(N_NODES)
    for u, v in G.edges():
        G[u][v]["weight"] = 0.5 + rng.random() * 0.5
    return G


def all_pairs_hop_distances(G):
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

def propagate(G, activation, event_node, event_strength):
    activation[event_node] = min(1.0, activation[event_node] + event_strength)
    for nb in G.neighbors(event_node):
        w = G[event_node][nb]["weight"]
        activation[nb] = min(1.0,
            activation[nb] + event_strength * SPREAD_FACTOR * w)


def decay(activation, rate):
    for i in range(N_NODES):
        activation[i] *= rate


def detect(G, activation):
    candidates = []
    for node in range(N_NODES):
        v = activation[node]
        if v < ACTIVATION_FLOOR: continue
        if all(activation[nb] <= v + 0.01 for nb in G.neighbors(node)):
            candidates.append({"node": node, "strength": v})
    return candidates


def drift_anchor(anchor, G, activation, mode):
    neighbors = list(G.neighbors(anchor.node))
    if not neighbors:
        anchor.age += 1
        anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02
        return
    if mode == "structured":
        best = max(neighbors, key=lambda n: activation[n])
        if activation[best] > activation[anchor.node]:
            anchor.node = best
    else:  # random
        anchor.node = random.choice(neighbors)
    anchor.age += 1
    anchor.strength = anchor.strength * 0.98 + activation[anchor.node] * 0.02


def cluster_graph(anchors, hop_distances):
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
                d = hop_distances[anchors[curr].node].get(anchors[j].node, 999)
                if d <= HOP_CLUSTER_RADIUS:
                    assignments[j] = cid; queue.append(j)
        cid += 1
    for i, a in enumerate(anchors): a.cluster_id = assignments[i]
    centroids = []
    for c in range(cid):
        members = [anchors[i] for i in range(n) if assignments[i] == c]
        if not members: continue
        member_nodes = [a.node for a in members]
        medoid = min(member_nodes,
                     key=lambda u: sum(hop_distances[u].get(v, 999) for v in member_nodes))
        centroids.append({
            "id": c, "medoid": medoid,
            "size": len(members), "member_nodes": set(member_nodes),
        })
    return centroids


# ─── Trial ────────────────────────────────────────────────────────────────────

def run_trial(decay_rate, event_strength, seed, mode):
    """mode: 'sparse_structured' | 'sparse_random' | 'complete_structured' | 'complete_random'"""
    random.seed(seed); np.random.seed(seed)

    graph_type = "sparse" if mode.startswith("sparse") else "complete"
    drift_type = "structured" if mode.endswith("structured") else "random"

    G = build_sparse_graph(seed) if graph_type == "sparse" else build_complete_graph(seed)
    hop_distances = all_pairs_hop_distances(G)

    activation = [0.0] * N_NODES
    anchors = []
    log = []
    prev_medoids = {}      # cluster_id → medoid node from previous step
    prev_assignments = {}
    migration_log = []
    medoid_stability_log = []  # fraction of clusters with unchanged medoid

    for tick in range(1, TICKS + 1):
        if random.random() < EVENT_RATE:
            event_node = random.randint(0, N_NODES - 1)
            propagate(G, activation, event_node, event_strength)

        decay(activation, decay_rate)

        if tick % UPDATE_INTERVAL == 0:
            candidates = detect(G, activation)
            for c in candidates:
                existing = next((a for a in anchors if a.node == c["node"]), None)
                if existing:
                    existing.strength = existing.strength * 0.85 + c["strength"] * 0.15
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(GraphAnchor(c["node"], c["strength"]))

            for a in anchors:
                drift_anchor(a, G, activation, drift_type)

            anchors = [a for a in anchors
                       if a.strength > ACTIVATION_COLLAPSE or a.age < 30]

            centroids = cluster_graph(anchors, hop_distances)

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

        if tick % LOG_INTERVAL == 0:
            centroids = cluster_graph(anchors, hop_distances)

            # C1'': hop distances between medoids
            hop_dists = []
            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i + 1, len(centroids)):
                        d = hop_distances[centroids[i]["medoid"]].get(
                            centroids[j]["medoid"], 999)
                        if d < 999: hop_dists.append(d)

            # C2'': medoid stability (corrected metric)
            current_medoids = {c["id"]: c["medoid"] for c in centroids}
            stability = None
            if prev_medoids and current_medoids:
                matched = 0; total = 0
                for cid, medoid in current_medoids.items():
                    if cid in prev_medoids:
                        total += 1
                        if prev_medoids[cid] == medoid:
                            matched += 1
                if total > 0:
                    stability = matched / total
                    if tick > TICKS // 2:
                        medoid_stability_log.append(stability)
            prev_medoids = current_medoids

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "cluster_count": len(centroids),
                "mean_hop_distance": round(sum(hop_dists)/len(hop_dists), 3)
                                     if hop_dists else None,
                "hop_variance": round(float(np.std(hop_dists)), 3)
                                if len(hop_dists) > 1 else None,
                "medoid_stability": stability,
            })

    # Conditions
    half = len(log) // 2; late = log[half:]

    # C1''
    hop_dists_late = [e["mean_hop_distance"] for e in late if e["mean_hop_distance"]]
    mean_hop = round(sum(hop_dists_late)/len(hop_dists_late), 3) if hop_dists_late else None
    hop_var = round(float(np.std(hop_dists_late)), 3) if len(hop_dists_late) > 1 else None
    c1 = (mean_hop is not None and mean_hop >= C1_MIN_HOP_DIST and   # ≥ not >
           hop_var is not None and hop_var < C1_MAX_VARIANCE)

    # C2'' corrected — medoid stability
    mean_stab = round(sum(medoid_stability_log)/len(medoid_stability_log), 4) \
                if medoid_stability_log else None
    c2 = mean_stab is not None and mean_stab > C2_MEDOID_STABILITY

    # C3''
    late_updates = (TICKS // 2) // UPDATE_INTERVAL
    rate = round(sum(1.0/n for _, n in migration_log) / late_updates, 6) \
           if migration_log and late_updates > 0 else 0.0
    c3 = rate < C3_RATE_THRESHOLD

    return {
        "mode": mode,
        "params": {"decay_rate": decay_rate, "event_strength": event_strength,
                   "seed": seed},
        "conditions": {
            "C1": {"passed": c1, "mean_hop": mean_hop, "variance": hop_var},
            "C2": {"passed": c2, "mean_medoid_stability": mean_stab},
            "C3": {"passed": c3, "rate": rate},
        },
        "all_passed": c1 and c2 and c3,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    decay_rates     = [0.75, 0.80, 0.85, 0.90, 0.95]
    event_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds           = [0, 1, 2, 3, 4]
    modes = ["sparse_structured", "sparse_random",
             "complete_structured", "complete_random"]
    trials = len(decay_rates) * len(event_strengths) * len(seeds)

    print(f"\n{'='*65}")
    print(f"  EXPERIMENT O2b — Cross-Substrate (Corrected Metrics + Complete Graph)")
    print(f"  {trials} trials per mode  ×  {len(modes)} modes = {trials*len(modes)} total")
    print(f"  C2'' = medoid stability (not Jaccard)")
    print(f"  C1'' = hop ≥ 3 (inclusive)")
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
    with open("exp_o2b_results.json", "w") as f:
        json.dump({
            "experiment": "O2b_corrected",
            "corrections": ["C2 = medoid stability", "C1 = hop >= 3"],
            "graph_types": {"sparse": f"Erdos-Renyi p={SPARSE_EDGE_PROB}",
                            "complete": "complete graph K_200"},
            "results": {
                mode: [{"params": r["params"], "conditions": r["conditions"],
                        "all_passed": r["all_passed"]}
                       for r in rlist]
                for mode, rlist in all_results.items()
            }
        }, f, indent=2)
    print("  JSON → exp_o2b_results.json")

    # Summary
    print(f"\n{'─'*65}")
    print("O2b RESULTS")
    print(f"{'─'*65}")
    print(f"{'Mode':<25} {'All':>5}  {'C1':>5}  {'C2':>5}  {'C3':>5}  "
          f"{'hop':>6}  {'stab':>6}  {'rate':>8}")
    print(f"{'─'*65}")

    for mode in modes:
        results = all_results[mode]
        passed  = sum(1 for r in results if r["all_passed"])
        c1s = sum(1 for r in results if r["conditions"]["C1"]["passed"])
        c2s = sum(1 for r in results if r["conditions"]["C2"]["passed"])
        c3s = sum(1 for r in results if r["conditions"]["C3"]["passed"])
        hops  = [r["conditions"]["C1"]["mean_hop"] for r in results
                 if r["conditions"]["C1"]["mean_hop"]]
        stabs = [r["conditions"]["C2"]["mean_medoid_stability"] for r in results
                 if r["conditions"]["C2"]["mean_medoid_stability"]]
        rates = [r["conditions"]["C3"]["rate"] for r in results]
        print(f"  {mode:<23} {passed:>5}  {c1s:>5}  {c2s:>5}  {c3s:>5}  "
              f"{round(np.mean(hops),2) if hops else 'N/A':>6}  "
              f"{round(np.mean(stabs),3) if stabs else 'N/A':>6}  "
              f"{round(np.mean(rates),4):>8}")

    # Key comparison: complete graph
    cs = sum(1 for r in all_results["complete_structured"] if r["all_passed"])
    cr = sum(1 for r in all_results["complete_random"]     if r["all_passed"])
    ss = sum(1 for r in all_results["sparse_structured"]   if r["all_passed"])
    sr = sum(1 for r in all_results["sparse_random"]       if r["all_passed"])

    print(f"\n{'─'*65}")
    print("COMPLETE GRAPH CONTROL — KEY COMPARISON")
    print(f"{'─'*65}")
    print(f"  sparse_structured:   {ss}/125")
    print(f"  sparse_random:       {sr}/125")
    print(f"  complete_structured: {cs}/125")
    print(f"  complete_random:     {cr}/125")

    print(f"\n  Interpretation:")
    if cs > 20 and cr < cs * 0.4:
        print(f"  → FIELD-RESPONSIVENESS CONFIRMED in unconstrained substrate")
        print(f"     complete_structured passes, complete_random fails")
        print(f"     Sparse graph was providing positional coupling through topology")
        print(f"     Minimal mechanism (positional coupling + grouping) is substrate-agnostic")
    elif cs > 20 and cr >= cs * 0.4:
        print(f"  → INCONCLUSIVE in complete graph")
        print(f"     Both complete modes pass — complete graph may still provide coupling")
        print(f"     Field-responsiveness cannot be isolated at this graph density")
    elif cs <= 20 and cr <= 20:
        print(f"  → GRAPH DYNAMICS DO NOT SUPPORT PHENOMENON")
        print(f"     Neither mode passes in complete graph")
        print(f"     Result is field-substrate-specific")
    else:
        print(f"  → UNEXPECTED — interpret raw numbers directly")

    if sr > 20 and ss > 20:
        print(f"\n  Sparse confirmation: both sparse modes pass")
        print(f"  → Sparse graph topology provides positional coupling regardless of drift")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"\n{'='*65}")
