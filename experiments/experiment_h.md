# Experiment H — Null Model Control

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment G found spontaneous multi-basin emergence across all 125 parameter combinations. The uniformity raised a specific concern: are the structured mechanics doing real work, or is the measurement finding structure it built in?

This experiment replaces three structured mechanics with random equivalents while holding everything else identical. If the conditions still pass, the result is a measurement artifact. If they fail, the structured mechanics are necessary.

---

## What Was Replaced

Three mechanisms from Experiment G, each substituted with a random equivalent:

| Mechanism | Experiment G | Experiment H (null) |
|---|---|---|
| **Anchor detection** | Gradient-based local maxima — anchors form at field peaks | Random placement — anchors placed anywhere regardless of field structure |
| **Anchor drift** | Gradient-following — movement toward field minima | Random walk — no directional bias |
| **Cluster assignment** | Spatial proximity — connected components by distance | Random assignment — anchors assigned to one of K clusters regardless of position |

All other parameters, conditions, sweep ranges, and seeds are identical to Experiment G.

---

## Conditions

Identical to Experiment G. Defined before execution.

**C1** — Separation fraction > 0.40 (second half of run)
**C2** — Mean within-cluster topology similarity > 0.70
**C3** — C1 + C2 + at least one migration event

---

## Results

```
NULL MODEL REGIME MAP
             is=0.5     is=0.7     is=0.9     is=1.1     is=1.3
cf=0.75    OSCL(3/5)  SNGL(2/5)  OSCL(3/5)  OSCL(5/5)  OSCL(5/5)
cf=0.80    OSCL(3/5)  OSCL(4/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)
cf=0.85    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)
cf=0.90    OSCL(5/5)  OSCL(5/5)  OSCL(4/5)  OSCL(5/5)  OSCL(5/5)
cf=0.95    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(3/5)  TRNS(2/5)
```

**Direct comparison with Experiment G:**

|  | G (structured) | H (null model) | Δ |
|---|---|---|---|
| Trials passed | 125 / 125 | 109 / 125 | −16 |
| Cells fully passed (5/5 seeds) | 25 / 25 | 17 / 25 | −8 |
| Mean topology similarity | 0.9439 | 0.7949 | −0.149 |
| Seed consistency | Uniform across all cells | Variable — 2/5, 3/5 failures at boundaries |

---

## Interpretation

### The partial replication problem

The null model passed 109 out of 125 trials — 87% of Experiment G's pass rate. The automated comparison flagged this as "likely measurement artifact." That interpretation is too strong. The correct reading requires separating what the null model contaminated by construction from what it genuinely tested.

### C1 and C3 are partially trivial under null mechanics

**C1** counts ticks where two or more clusters are present. With random cluster assignment to K=2 clusters, anchors are always split into two groups. C1 is therefore nearly guaranteed to pass regardless of field structure. This condition cannot discriminate structured from random mechanics in this design.

**C3** counts migration events — anchors switching cluster assignment. With random reassignment occurring every 8 ticks, migrations are generated mechanically at every update. C3 is contaminated for the same reason: it counts something the null model produces by definition, not by field dynamics.

These are not failures of the null model. They are failures of C1 and C3 as discriminating metrics when cluster assignment itself is the variable being randomized.

### C2 is the real discriminator — and it shows a real difference

**C2** measures topological similarity within clusters across time — whether each cluster maintains internal structural consistency. This metric does not depend on how clusters are assigned. It tests whether the anchors within a given group behave in a structurally coherent way.

Experiment G: 0.9439 mean within-cluster topology similarity.
Experiment H: 0.7949 — a drop of 0.149 points, 15.8% lower.

Both are above the 0.70 threshold, which is why H still passes technically. But the magnitude of the difference is real: structured mechanics produce meaningfully higher topological coherence within basins than random placement and drift. The physics are doing something. The something is not large enough to produce categorical failure, but it is large enough to be measured.

### Seed consistency as a secondary signal

Experiment G produced uniform 5/5 results across all 25 cells. Experiment H shows 8 cells where not all seeds passed — 2/5 and 3/5 failures appearing at the parameter boundaries. This seed-dependent variance is absent from G. It suggests the null mechanics are more sensitive to random initialization than the structured mechanics, which is consistent with the structured mechanics providing stabilizing constraint that the null model removes.

### The honest finding

The structured mechanics are not fully necessary for the conditions as written to pass — because two of the three conditions are partially trivial under random cluster assignment. But they are necessary for consistent, high-quality topological coherence. The 0.149 point drop in C2 and the 8-cell consistency gap are the signal. The 87% pass rate is an artifact of condition design, not evidence that the mechanics don't matter.

---

## What This Reveals About Experiment G's Conditions

The null model did exactly what it was designed to do: it found a weakness in the measurement design. C1 and C3 need to be tightened before they can serve as discriminating evidence.

**C1 — Required fix:** Spatial stability should be required, not just cluster presence. Two randomly assigned groups always exist; two spatially stable, structurally distinct regions do not. C1 should measure whether cluster centroids maintain consistent spatial separation, not just whether two clusters are counted.

**C3 — Required fix:** Migration events should be correlated with field structure changes, not simply counted. A migration that corresponds to a field gradient shift is evidence of interaction dynamics. A migration that occurs because of random reassignment is noise.

**C2 — Adequate, but threshold may need raising:** The 0.70 threshold allowed the null model to technically pass. Raising to 0.85 would have excluded H entirely while preserving all of G's results. This should be the threshold for future experiments.

---

## Revised Condition Proposal for Experiment I

Three conditions, tightened:

**C1'** — Spatial separation stability: mean inter-cluster centroid distance > 30 field units across the second half of the run, with variance < 15. Requires clusters to be genuinely spatially distinct and stable, not just numerically present.

**C2'** — Topological persistence threshold raised: mean within-cluster similarity > 0.85.

**C3'** — Structured migration: at least 3 migration events where the migrating anchor moves in the direction of the field gradient at the time of migration. Filters out random reassignment noise.

Under these conditions, Experiment G's best results would still pass. Experiment H's null model would not.

---

## What the Experiments Together Establish So Far

**Experiment G established:** Under structured field mechanics, spontaneous multi-basin emergence occurs robustly across the tested parameter space. The phenomenon is not rare or boundary-dependent.

**Experiment H established:** The conditions as written are partially trivial under random mechanics. The structured mechanics produce meaningfully higher topological quality (C2: 0.94 vs 0.79) and greater seed consistency. The mechanics are contributing — but the contribution was not fully isolated by the original condition design.

**What neither has established:** That the phenomenon is independent of the specific physics, that it holds under minimal mechanics, or that it constitutes the structural substrate the framework claims. Those remain open.

---

## Next Steps

**Experiment I** — Re-run with tightened conditions (C1', C2', C3') against both structured and null mechanics. Expected outcome: structured mechanics pass, null model fails. If that holds, the contribution of the structured mechanics is isolated.

**Boundary search** — Extend parameter range to extremes (CF=0.50, CF=0.99, IS=0.1, IS=3.0) to find the failure boundary. Experiment G found no failures in the tested range. The boundary is the honest edge of the claim.

**Minimality tests** — Remove mechanisms one at a time from the structured model. Identifies which mechanics are necessary versus jointly sufficient.

---

*2026*
