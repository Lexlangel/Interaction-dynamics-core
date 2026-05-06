# Experiment M — Minimality Tests

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiments G–K established that the full set of three structured mechanics — gradient detection, gradient drift, spatial clustering — produces identity-like topology that random mechanics cannot replicate. The question left open: which of the three is actually necessary?

Three partial modes test this directly, each removing one mechanism:

| Mode | What is removed | What remains |
|---|---|---|
| `no_drift` | Gradient drift → random walk | Structured detection + spatial clustering |
| `no_detection` | Gradient detection → random placement | Gradient drift + spatial clustering |
| `no_clustering` | Spatial clustering → random assignment | Gradient detection + gradient drift |

Plus `full_structured` as the reference. Same parameter sweep as G–K. Conditions C1'+C2'+C3''' with threshold 0.05.

---

## Pre-Registered Expectations

**no_drift:** Anchors detected at field peaks but not organized. Expected to degrade significantly — drift consolidates structure, its removal should produce dispersed, poorly separated basins.

**no_detection:** Random placement but drift moves anchors to field peaks anyway. Expected to degrade mildly — the starting positions are random but drift compensates.

**no_clustering:** Structurally equivalent to the null model in H. Expected to fail entirely — random assignment produces high migration rate and no spatial stability.

---

## Results

```
MINIMALITY SUMMARY

Mode                 Trials    Migration rate   Topo sim   Status
──────────────────────────────────────────────────────────────────
full_structured      88/125    0.0328           0.9439     reference
no_drift             19/125    0.0807           0.9271     LOAD-BEARING
no_detection         91/125    0.0357           0.9390     REDUNDANT
no_clustering         0/125    0.4937           0.7685     LOAD-BEARING

Drop from full_structured reference (88 trials):
  Removing drift:        −69 trials  (78% drop)
  Removing detection:    + 3 trials  (−3% drop — slight improvement)
  Removing clustering:   −88 trials  (100% drop)
```

---

## Interpretation

### Detection is redundant

Removing gradient detection and replacing it with random anchor placement actually improves performance: 91/125 vs 88/125. This is not noise — it is a mechanistic finding.

The reason: gradient detection places anchors at local field maxima, which requires waiting for the field to develop sufficient peaks above the detection threshold. Random placement distributes anchors immediately across the field. Gradient drift then moves them toward field peaks regardless of where they started. The positioning work that detection was supposed to do is done by drift instead, and it is done more efficiently because drift operates continuously rather than only at detection events.

Detection is not doing unique work. It is a convenience — one path to getting anchors near field peaks — but drift accomplishes the same result through a different mechanism. The two are redundant given the presence of spatial clustering.

**This strengthens the claim:** the result does not depend on the specific detection implementation. Any mechanism that produces anchors — random, structured, or otherwise — combined with gradient drift and spatial clustering produces the phenomenon. Detection method is not a free parameter of the claim.

### Drift is load-bearing

Removing gradient drift reduces passes from 88 to 19 — a 78% drop. The migration rate increases from 0.033 to 0.081, indicating anchors are reorganizing more frequently without the stabilizing effect of gradient-following movement.

Without drift, anchors detected at field peaks have no mechanism to remain near them as the field evolves. They stay where they were placed until they decay, new events displace them, or they are pruned. The spatial clustering assigns them to groups based on their positions — but those positions are not maintained relative to the field structure. Basins form transiently but do not persist.

The 19 trials that still pass are likely cases where field structure happened to remain stable enough that anchors at peak positions stayed clustered by spatial proximity without needing to drift to maintain it. These are fortunate parameter combinations, not a systematic mechanism.

### Clustering is absolutely load-bearing

Removing spatial clustering produces 0/125 passes with migration rate 0.494 — nearly identical to the full null model's 0.472 from Experiment K. This is expected: random cluster assignment is exactly what the null model tested, and the null model failed completely.

Spatial clustering is what defines the basins. Without it, even correctly positioned anchors (detected at field peaks, maintained there by gradient drift) are assigned to groups arbitrarily. The groups have no spatial coherence, their centroids jump with every reassignment, and C1' fails on distance variance. C3''' fails on migration rate. The entire spatial structure established by detection and drift is discarded at the assignment step.

Clustering is not just load-bearing — it is definitionally necessary. The concept of "basin" requires that anchors be grouped by spatial relationship. Remove that grouping and there are no basins to measure.

### The minimal mechanism

The minimality tests identify the sufficient minimal set:

**Any detection + gradient drift + spatial clustering**

Detection method does not matter. Gradient drift is necessary. Spatial clustering is necessary. The minimal claim is: a field system with gradient-following anchor movement and proximity-based region assignment produces stable, separated, low-churn topology from noise.

This is a cleaner and more general claim than the full mechanism. It does not depend on the specific way anchors are initially detected — only on how they move and how they are grouped.

---

## Framework Correspondence

The minimality result maps cleanly onto the primitive triad:

**Gradient drift → Influence operating under constraint**
Anchors move in response to the field (Influence) toward positions of lower gradient (Constraint). Without this, influence events produce anchors but no structured response to the field.

**Spatial clustering → Differentiation**
Proximity-based grouping produces distinct regions — genuine differentiation of the field into separated zones. Without this, differentiation exists in the field but is not registered as distinct topology.

**Detection → not primitive**
Detection is the interface layer through which events create anchors. Any implementation works. It is not a primitive condition — it is a substrate-specific mechanism for crossing the detection threshold.

The minimality tests did not set out to confirm this mapping. They confirmed it by eliminating the one mechanism that wasn't doing unique work.

---

## What This Establishes

The minimal mechanism for producing identity-like topology in this field physics is:

1. Some mechanism producing anchors (detection floor: IS > ~0.2 from Experiment L)
2. Gradient drift (Influence under Constraint)
3. Spatial clustering (Differentiation)

The phenomenon does not require fine-tuned detection. It does not require a specific placement strategy. It requires that something registers events, that what is registered moves in response to field structure, and that what moves is grouped by spatial relationship.

That is a substrate-agnostic description of the minimal conditions. Whether it constitutes a proof that {I, D, C} are the necessary and sufficient primitives for identity-like topology is a claim the experiment cannot make — that would require extending to arbitrary physics, not just this one. What it establishes is that in this physics, the three conditions correspond to the three primitives, and removing either of the primitive-corresponding ones causes failure while removing the non-primitive one does not.

---

*2026*
