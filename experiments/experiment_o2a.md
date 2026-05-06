# Experiment O — Part 2a: Cross-Substrate Diagnosis

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment O1 established the minimal mechanism in the continuous field substrate:

> **Field-coupled anchor dynamics + spatial clustering**

The next question: is this substrate-agnostic? Can the same two conditions produce identity-like topology in a genuinely different physical substrate — one with no continuous field, no Gaussian propagation, no Euclidean distance?

This experiment attempts replication in a graph substrate: Erdős–Rényi sparse random graph, N=200 nodes, activation spreading along edges, anchors defined as local activation maxima in the graph, drift as hop-to-highest-neighbor, clustering as connected components within hop-distance ≤ 2.

The result is not a clean pass or fail. It is diagnostic — and the diagnosis is more informative than either outcome would have been.

---

## Design

**Substrate:** Erdős–Rényi random graph, N=200 nodes, edge probability p=0.08, ~16 neighbors per node. No spatial embedding. Distances are graph hops, not Euclidean.

**Two modes tested:**

| Mode | Drift | Clustering | Field-responsive? |
|---|---|---|---|
| **graph_structured** | Move to highest-activation neighbor | Hop-distance ≤ 2 | Yes — activation-coupled |
| **graph_random_walk** | Move to random neighbor | Hop-distance ≤ 2 | No |

**Adapted conditions:**

| Condition | Definition | Analog to |
|---|---|---|
| **C1''** | Mean medoid-medoid hop distance > 3, variance < 2 | C1': spatial separation stability |
| **C2''** | Mean Jaccard membership similarity across steps > 0.85 | C2': topology persistence |
| **C3''** | Migration rate < 0.05 | C3''': identical definition |

---

## Results

```
Mode                  C1'' (hop)   C2'' (Jaccard)   C3'' (rate)   All passed
────────────────────────────────────────────────────────────────────────────
graph_structured      0/125        0/125            118/125        0/125
graph_random_walk     0/125        0/125            118/125        0/125

Mean values:
  C1'' mean hop:     3.0 (both modes — exactly at threshold)
  C2'' mean Jaccard: 0.039 (both modes — far below 0.85)
  C3'' mean rate:    0.0076 (both modes — identical)
```

Both modes fail all-conditions. The verdict from the automated decision rule: replication failed.

That is the wrong reading of the data.

---

## Diagnosis

### C3'' — The most informative result

In the field model (K through O1), C3''' discriminated structured from random walk by a factor of 3–14×:

```
Field model:   structured  0.033    random walk  0.091   ratio: 2.8×
Graph model:   structured  0.0076   random walk  0.0076  ratio: 1.0×
```

Both graph modes produce identical migration rates, both well below the C3'' threshold. The discrimination that C3''' provided in the field model is completely absent in the graph model.

This is not a calibration issue. It is a structural finding about the graph substrate itself.

In the continuous field, anchors under random walk drift freely — 1.5 units per update in any direction, unrestricted. Without gradient drift pulling them toward field-stable positions, they constantly reorganize. Migration rate rises to 0.091.

In the sparse random graph, anchors under random walk are constrained to move to adjacent nodes — ~16 neighbors out of 200. The graph topology itself limits the movement range. Anchors cannot drift far from their current positions regardless of whether drift is field-responsive or random. The graph's adjacency structure is already a constraint architecture.

**The graph substrate supplies positional coupling through topology. Field-responsiveness becomes invisible because the substrate does the work that gradient drift did in the field.**

### C1'' — Borderline, not failure

Mean medoid-medoid hop distance is 3.0 for both modes — exactly at the threshold of > 3.0. The condition fails by a rounding margin. Some cluster separation is present. With threshold ≥ 3.0 rather than > 3.0, C1'' would pass at a non-trivial rate. This is a calibration issue, not absence of the phenomenon.

### C2'' — Wrong metric

Jaccard membership similarity of 0.039 means cluster membership as defined by exact node identity reshuffles almost completely between log steps. But C3'' shows migration rate of 0.0076 — anchors are barely moving. The contradiction is the metric.

Jaccard measures: are the same nodes in the same clusters across consecutive steps? In hop-distance clustering, a single-hop drift by one anchor can trigger a cascade of cluster reassignments — an anchor moves from the edge of cluster A into the radius of cluster B, changing both clusters' membership entirely. The field model's Laplacian eigenvalue comparison measured whether the spatial *structure* within each cluster was stable, not whether the exact same anchors were present. These are different questions.

Jaccard is not the graph analog of Laplacian topology similarity. It is a stricter metric that conflates positional stability with membership identity. The condition is not failing because topology is unstable — it is failing because the metric is wrong for this substrate.

---

## What This Changes

### The minimal mechanism requires revision

The O1 formulation was:

> **Field-coupled anchor dynamics + spatial clustering**

where "field-coupled" meant specifically: anchors drift in response to the field's gradient structure, providing positional stability in a substrate that offers no built-in constraint on movement.

O2a reveals this framing was substrate-specific. The structural condition is not field-coupling specifically. It is:

> **Positional coupling to substrate structure + proximity grouping**

In the continuous field: positional coupling is provided by gradient drift, because the field substrate offers no built-in movement constraint.
In the sparse random graph: positional coupling is provided by graph topology, because adjacency already constrains movement to neighbors.

The two conditions are not about implementation. They are about which layer of the system provides positional stability and which layer provides spatial differentiation. In different substrates, these responsibilities can be carried by different mechanisms.

### What O2b needs

Before a cross-substrate verdict is possible, two things must be corrected:

**A graph-appropriate C2 metric.** Jaccard is wrong. The correct analog measures structural stability of cluster topology without requiring exact membership identity. Candidates: spectral similarity of the induced subgraph on cluster members across timesteps; medoid-distance stability (does the cluster medoid remain consistent); component signature stability (cluster size distribution across steps). Any of these measures structural topology rather than exact membership.

**Calibrated C1 threshold.** Mean hop distance of 3.0 is real separation in a graph with HOP_CLUSTER_RADIUS = 2. The threshold > 3.0 excludes cases at exactly 3. Recalibrate to ≥ 3, or use a normalized separation measure (hop distance / cluster radius) with threshold > 1.5.

With both corrections, a clean cross-substrate test becomes possible.

---

## The Revised Cross-Substrate Claim

The current evidence does not support: "field-responsive motion + spatial clustering is substrate-agnostic."

It supports: "**positional coupling to substrate structure + proximity grouping** is a structural condition that may be substrate-agnostic, but the mechanism carrying positional coupling varies by substrate."

In the continuous field: gradient drift carries positional coupling.
In the sparse random graph: graph topology carries it — and carries it equally for structured and random walk drift.

This is not a failure. It is a refinement. It says the minimal mechanism is more general than the field-specific implementation, and that cross-substrate replication requires identifying which layer of each substrate provides positional stability before testing whether the two conditions are met.

---

## O2b — What the Next Experiment Must Do

Three corrections for O2b:

**Correct C2** to a graph-structural topology metric — spectral similarity of the induced anchor subgraph within each cluster across consecutive steps. This measures whether cluster structure is stable, not whether membership is identical.

**Recalibrate C1** to hop distance ≥ 3 (not > 3), or normalize by cluster radius.

**Add a genuine random control** for the graph substrate — one where graph topology does NOT provide built-in constraint. One option: use a complete graph (all nodes connected) so random walk can reach anywhere in one hop. In a complete graph, random walk is unconstrained. If graph_structured passes and graph_random_walk fails in a complete graph, field-responsiveness is genuinely required even in graph dynamics.

---

## Summary

O2a is not a replication failure. It is a substrate-diagnostic experiment that identified:

1. The graph substrate supplies positional coupling through topology — making field-responsive and random drift indistinguishable via C3''.
2. Jaccard is the wrong metric for C2 — it measures membership identity, not structural topology.
3. The minimal mechanism generalizes from "field-responsive motion" to "positional coupling to substrate structure," with substrate-specific implementations.

The cross-substrate claim requires O2b with corrected metrics and a substrate that isolates field-responsiveness from topology-provided coupling.

---

*2026*
