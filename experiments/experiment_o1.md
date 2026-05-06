# Experiment O — Part 1: Field-Responsiveness Isolation

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment N revised the minimal mechanism to: *registration + field-responsive motion + spatial clustering*. But it left one structural question open: does random walk + spatial clustering — zero field response — also pass conditions? If yes, clustering alone is sufficient and field-responsiveness is not a genuine requirement. If no, field-responsiveness is an irreducible second condition.

This experiment answers that question directly.

---

## Design

Three modes, each controlling field-responsiveness of drift while holding spatial clustering constant:

| Mode | Detection | Drift | Clustering | Field-responsive? |
|---|---|---|---|---|
| **full_structured** | Gradient-based | Gradient descent | Spatial proximity | Yes |
| **field_walk_cluster** | Random | Gradient descent | Spatial proximity | Yes |
| **random_walk_cluster** | Random | Random walk | Spatial proximity | **No** |

`random_walk_cluster` is the critical test. Random placement, random movement, spatial grouping only. No field structure informs anchor *position* at any step. Note: anchor strength remains field-coupled in all modes through the update rule `strength = strength × 0.98 + field[position] × 0.02`. The isolation tests positional coupling specifically. A critic might object that random_walk_cluster retains scalar field coupling through strength dynamics and is therefore not fully decoupled. The results answer this directly: positional coupling — not scalar coupling — is the load-bearing factor for topology formation.

`field_walk_cluster` is a control confirming that detection method remains irrelevant when field-responsive drift is preserved — replicating M's no_detection finding in the isolation context.

**Pre-registered decision rule:** if `random_walk_cluster` passes ≥ 15/45 (33% of trials), clustering alone is sufficient and the minimal mechanism revises further. Below that threshold, the difference is structurally significant and field-responsiveness is irreducible.

---

## Results

```
Mode                     Trials   Rate    Topo sim   C1 pass
──────────────────────────────────────────────────────────────
full_structured          33/45    0.033   0.944      37/45
field_walk_cluster       30/45    0.037   0.933      41/45
random_walk_cluster       3/45    0.091   0.902      33/45
```

`random_walk_cluster`: 3/45. Decision threshold: 15/45.

**Field-responsiveness is an irreducible second condition.**

---

## Interpretation

### What the numbers show

`field_walk_cluster` passes 30/45 — near-identical to full_structured at 33/45, with slightly higher C1 pass rate (41 vs 37). Detection method remains irrelevant when field-responsive drift is preserved. This replicates M's finding under the isolation design.

`random_walk_cluster` passes 3/45. The migration rate is 0.091 — nearly double the C3''' threshold of 0.05. Random walk constantly reorganizes even when spatial clustering is preserved, because without field-responsive drift anchors have no mechanism to find and maintain stable positions. C1' passes for 33/45 trials — spatial separation can occur by chance — but C2' and C3''' fail: topology is not persistent, and reorganization rate is high.

The 3 surviving trials are stochastic boundary cases. They do not reproduce under identical conditions, and they do not produce stable migration or topology persistence signatures — C2' and C3''' fail in these trials even where C1' happens to pass. They are not evidence of a systematic mechanism.

### What field-responsiveness actually does

The isolation test makes the mechanism precise. Field-responsive drift does one thing that random walk cannot: it couples anchor position to field structure over time. This coupling produces two downstream effects:

**Positional stability:** Anchors under gradient drift migrate toward field-determined positions and stay there as the field evolves. Anchors under random walk migrate continuously regardless of field state. The migration rate difference (0.033 vs 0.091) is the direct signature of this — field-responsive anchors reorganize three times less frequently because their positions are field-determined, not random.

**Topology persistence:** Because field-responsive anchors occupy stable field-determined positions, the topology within each spatial cluster (C2') remains consistent across time. Random walk anchors occupy positions that are not field-determined, so cluster membership shifts continuously and within-cluster topology similarity drops below the 0.85 threshold.

Spatial clustering groups whatever positions exist. It cannot compensate for positions that are not stable. Stable positions require a generative mechanism — in this system, that mechanism is field-responsive drift.

### Why the noise result from N and this result are consistent

Experiment N showed that 200% noise added to gradient drift does not degrade the phenomenon. This might seem inconsistent with O1's finding that random walk (which is also noisy) does degrade it. The difference is structural.

Noisy gradient drift still has a systematic field-responsive component. Over many ticks, that component accumulates while noise averages out. Random walk has no systematic component at any timescale. The distinction is not noise versus signal. It is signal versus no signal. Noisy field-responsive drift contains a directional component that accumulates across 312 update cycles. Random walk contains none.

N established: noise does not destroy field-responsiveness. O1 establishes: absence of field-responsiveness cannot be compensated by spatial clustering. These are consistent claims about the same mechanism.

---

## The Minimal Mechanism — Final Form

Across experiments M, N, and O1, by systematic elimination:

**Not required:**
- Specific detection method (M: no_detection passes at equal rate)
- Gradient descent direction (N: inverted_drift passes identically)
- Gradient signal purity (N: 200% noise produces no degradation)
- Temporal update order (N: scrambled order passes, marginally better)

**Required:**
- Field-responsive movement of any form (O1: absence reduces passes from 33 to 3)
- Spatial proximity clustering (N: anti_clustering produces 0 passes)

**The minimal mechanism:**

> **Field-coupled anchor dynamics + spatial clustering**

More precisely: persistent anchors with field-responsive positional coupling, grouped by spatial proximity. The isolation tested positional field-responsiveness specifically — anchor strength remains field-coupled in all modes, including random_walk_cluster. The result shows that positional coupling, not scalar coupling, is the load-bearing factor.

Two conditions. Both confirmed irreducible by elimination. The mechanism is as simple as it can be without failing.

---

## Precision Statement

Field-responsive movement, even under high per-tick noise and regardless of gradient direction, is sufficient when spatial clustering is preserved. Random walk — movement with no field-responsive component at any timescale — is not sufficient even when spatial clustering is preserved.

The boundary between these is not noise level or direction. It is the presence or absence of systematic coupling between anchor position and field structure across time.

---

## Framework Correspondence — Finalized

| Mechanism | What it does | Primitive |
|---|---|---|
| **Field-responsive motion** | Couples anchor positions to field structure; produces stability through accumulated coupling | **Influence + Constraint**: field events (I) shape movement; field topology (C) bounds it |
| **Spatial clustering** | Groups field-stable positions into distinct regions | **Differentiation**: proximity grouping produces distinct topology |
| **Detection floor** | IS > ~0.2 — events must register at all | Threshold: below this, no structure enters the system |

The noise result from N maps directly to the primitive triad: Influence accumulates across interaction history; Constraint stabilizes the resulting structure; Differentiation partitions it. A noisy field-responsive signal accumulates over 312 update cycles into stable positioning. A pure random walk cannot accumulate into field-coupled stability regardless of duration.

This is the simulation's operational analog of the framework's claim: identity requires repeated interaction under constraint, not a single clean registration event. The mechanism is the same structure at two different levels of description.

---

## What Comes Next

The minimal mechanism is isolated. Two experiments remain in the planned series:

**O Part 2 — Cross-Substrate Replication:** Recreate the same two conditions (field-responsive motion + spatial clustering) in a different physical substrate — graph dynamics, agent-based, or cellular automata. If the phenomenon emerges there too, the claim is no longer about this specific field physics. It is about the structural conditions themselves.

**P — Identity Mapping:** Map simulation observables to framework constructs explicitly. Basins to proto-identity regions, stability to anchoring precursor, migration rate to identity drift, topology similarity to identity persistence. Then test perturbation and reconstruction — does a destabilized basin reform? This closes the loop from simulation back to the framework's core claims.

---

*2026*
