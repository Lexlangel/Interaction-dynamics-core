# Experiment N — Adversarial Stress Test and Minimal Mechanism Revision

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment M identified a minimal mechanism: any detection + gradient drift + spatial clustering. The claim was well-supported but not stress-tested. Experiment N applies adversarial pressure to each structural assumption and asks whether the claim holds or requires revision.

This is not a confirmation experiment. It is a deliberate attempt to break the mechanism — and the result is a genuine revision, not a vindication.

---

## Adversarial Conditions

Four targeted inversions, each attacking one structural assumption:

| Mode | What is inverted | Assumption attacked |
|---|---|---|
| **inverted_drift** | Anchors move UP the gradient | Gradient descent is necessary |
| **anti_clustering** | Anchors assigned to maximize spatial separation | Proximity grouping is necessary |
| **temporal_scramble** | Anchor update order randomized each tick | Temporal coherence is necessary |
| **noise_injection** | White noise added to gradient at 0.25× to 2.0× signal amplitude | Signal purity is necessary |

Reference: `full_structured` with all mechanics intact.

---

## Pre-Registered Expectations

**inverted_drift:** Partial degradation — different spatial organization, fewer passes.
**anti_clustering:** Complete failure — centroid instability destroys C1'.
**temporal_scramble:** Minimal effect — spatial structure should dominate temporal order.
**noise_injection:** Gradual degradation — threshold somewhere between 50% and 150% noise.

---

## Results

```
Mode                Trials    Rate     Topo sim   vs reference
──────────────────────────────────────────────────────────────
full_structured     33/45     0.0328   0.9439     reference
inverted_drift      33/45     0.0319   0.9440     identical
anti_clustering      0/45     0.0580   0.9163     complete failure
temporal_scramble   37/45     0.0353   0.9456     marginal improvement

Noise injection — no degradation at any level:
  noise × 0.25:  40/45
  noise × 0.50:  40/45
  noise × 1.00:  40/45
  noise × 1.50:  40/45
  noise × 2.00:  40/45
```

---

## What the Results Require

### Spatial clustering is the irreducible mechanism

Anti-clustering is the only adversarial condition that causes complete failure. It produces 0/45 passes — centroid instability destroys C1', and migration rate rises above C3''' threshold.

This is categorical. Every other adversarial condition passes. This one does not.

**Spatial clustering is the load-bearing mechanism. Everything else is an implementation detail.**

### Drift direction is not load-bearing

Inverted drift produces 33/45 passes — identical to full_structured — with topology similarity 0.944 and migration rate 0.032, statistically indistinguishable from the reference.

Anchors climbing the gradient organize near field peaks. Anchors descending organize near valleys. Both produce stable spatial configurations. Clustering captures either. The topology formed is structurally equivalent under both directions because clustering groups whatever stable positions exist, not specifically gradient-minimum positions.

Gradient descent was the implementation choice in G–M. It is not a structural requirement.

### Gradient signal purity is not load-bearing

Noise injection at 200% amplitude — where noise standard deviation is twice the gradient magnitude — produces 40/45 passes, more than the full_structured reference of 33/45. No noise level tested causes degradation.

The mechanism: per-tick drift direction is dominated by noise when noise is high. But over 312 anchor update cycles, the systematic gradient component accumulates while random noise averages toward zero. Temporal integration recovers the signal. Long-run spatial organization is driven by the systematic component regardless of per-tick noise amplitude.

This result connects directly to the framework:

> Single-interaction noise does not destroy topology if systematic field response persists across time.

The analogy to anchoring is structural: anchors form through *repeated* interaction under constraint, not through single clean events. The simulation's noise-tolerance and the framework's claim about structural persistence through accumulated interaction are the same claim at different levels of description.

### Temporal order is not load-bearing

Temporal scramble produces 37/45 — marginally better than full_structured. The spatial positions anchors occupy determine topology, not the sequence in which they are updated.

---

## The Revised Minimal Mechanism

Experiment M concluded:

> **any detection + gradient drift + spatial clustering**

Experiment N revises this to:

> **registration + field-responsive motion + proximity grouping**

Three things that are **not** load-bearing, previously assumed to be:
- Gradient direction (descent vs ascent — both produce topology)
- Gradient signal purity (200% noise — still produces topology)
- Temporal update order (scrambled — still produces topology)

One thing that **is** irreducibly load-bearing:
- Spatial proximity grouping — removing this destroys the phenomenon completely

One thing that **remains necessary but is more general than M stated:**
- Field-responsive movement of any form. Not gradient descent specifically. Field-responsive movement, even under high per-tick noise and regardless of gradient direction, appears sufficient when spatial clustering is preserved. This is deliberately softer than "any movement" — Experiment M showed that random walk with no field response reduces passes significantly (88 → 19). Field-responsiveness remains required; its specific implementation does not.

---

## The Conceptual Update

Experiment M's minimal mechanism implied: identity-like topology requires descent toward field minima. N's revision states something more general:

> Identity-like topology does not require descent toward field minima. It requires stable spatial differentiation produced by field-coupled motion and preserved by proximity grouping.

The field coupling can be in any direction. It can be noisy. It can be temporally disordered. What it cannot be is absent — and what the resulting positions cannot be assigned to is spatially incoherent groups.

This is a stronger claim because it is more general. A mechanism that only works for gradient descent is tied to a specific implementation. A mechanism that works for any field-coupled motion is a structural claim about a class of dynamics.

---

## Mapping to the Framework

The revised mechanism maps to the primitive triad more cleanly than M's version:

| Mechanism | Primitive | What it does |
|---|---|---|
| **Registration** | Detection floor (IS > ~0.2 from L) | Events must register at all |
| **Field-responsive motion** | **Influence + Constraint** | Field events (I) drive movement; field topology (C) shapes it |
| **Spatial clustering** | **Differentiation** | Proximity grouping produces distinct regions |

The noise result is particularly clean in framework terms. Influence operates through accumulated event history — the framework's claim that identity forms through repeated interaction under constraint is the same structural claim as the simulation's noise-tolerance. Single noisy events don't matter. What the field systematically does across time does.

---

## The Remaining Gap

N answered three of four adversarial questions. One remains:

**Does random walk + spatial clustering — no field response whatsoever — also pass?**

Experiment M showed that removing drift entirely reduced passes from 88 to 19. Those 19 survivors suggest spatial clustering alone may occasionally produce passing topology through chance spatial organization. If random walk + spatial clustering consistently passes, the minimal mechanism reduces to clustering alone. If it fails systematically, field-responsiveness is the irreducible second condition.

That is the remaining structural question. Until it is run, field-responsiveness remains required but its precise necessity relative to clustering alone is not fully bounded.

---

## Core Verdict

> Drift direction is not load-bearing. Drift purity is not load-bearing. Temporal order is not load-bearing. Spatial clustering is load-bearing.

> The phenomenon survives adversarial perturbations except when spatial grouping is destroyed. Therefore spatial clustering is the irreducible mechanism; drift direction, detection strategy, update order, and local noise are implementation details of the field-responsive motion requirement.

The minimal mechanism is simpler than M concluded, more general, and more robust under adversarial pressure. It is also closer to the framework's structural claims about what is necessary for identity-like topology to form.

---

*2026*
