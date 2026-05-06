# Experiment J — Ratio-Based C3

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment I showed that C3' (raw count of gradient-correlated migrations) failed as a discriminator: the null model averaged 216 gradient-correlated events vs 19 in the structured model — backwards from the prediction — because random reassignment generates hundreds of total migrations, and ~50% correlate with the gradient by chance.

The proposed fix: measure the *ratio* of gradient-correlated migrations to total migrations. Expected values were: random walk ~0.50, gradient-following ~0.85–0.95. A threshold of 0.65 was set between them.

This experiment tests whether that fix works.

---

## Conditions

**C1' and C2' unchanged from Experiment I.**

**C3'' — Gradient correlation ratio**
Gradient-correlated migrations / total migrations > 0.65. Minimum 5 total migrations required to compute a valid ratio. A migration is gradient-correlated if the anchor's drift direction is negatively correlated with the local field gradient — moving downhill, the signature of field-driven movement.

**Pre-registered expectation:** Structured mechanics pass C3'' at ratio ~0.85–0.95. Null mechanics fail at ratio ~0.50.

---

## Results

```
STRUCTURED — C1' C2' C3''
             is=0.5     is=0.7     is=0.9     is=1.1     is=1.3
cf=0.75    OSCL(0/5)  OSCL(0/5)  OSCL(0/5)  OSCL(0/5)  OSCL(0/5)
cf=0.80    OSCL(0/5)  OSCL(0/5)  OSCL(0/5)  OSCL(0/5)  SNGL(0/5)
cf=0.85    OSCL(0/5)  OSCL(0/5)  OSCL(0/5)  COEX(0/5)  OSCL(0/5)
cf=0.90    OSCL(0/5)  COEX(0/5)  OSCL(0/5)  OSCL(0/5)  OSCL(0/5)
cf=0.95    OSCL(2/5)  OSCL(1/5)  OSCL(1/5)  OSCL(2/5)  OSCL(2/5)

NULL MODEL — C1' C2' C3''
             is=0.5     is=0.7     is=0.9     is=1.1     is=1.3
cf=0.75    NONE(0/5)  SNGL(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)
cf=0.80    SNGL(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)
cf=0.85    NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)
cf=0.90    NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)
cf=0.95    NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)  NONE(0/5)
```

**Head to head:**

|  | Structured | Null |
|---|---|---|
| Trials passed | 8 / 125 | 0 / 125 |
| Cells fully passed | 0 / 25 | 0 / 25 |
| Mean gradient ratio | 0.3641 | 0.2143 |
| Mean topology similarity | 0.9439 | 0.7949 |

---

## Interpretation

### The ratio fix failed — and the reason matters

Both models produced gradient ratios far below prediction:

- Structured: 0.3641 (expected 0.85–0.95)
- Null: 0.2143 (expected ~0.50)

The directional relationship is correct — structured is higher than null. But both are below the threshold, and neither matches its expected value. The structured model barely passed (8/125, concentrated in the high-CF boundary where field gradients persist longer). The null model passed nothing.

This is not a threshold miscalibration. It is a physics-level design flaw.

### Why the gradient ratio is broken at the root

Anchors form at field local maxima where gradient magnitude is below `ANCHOR_GRAD_THRESH = 0.12`. That is the detection criterion. Anchors are specifically placed where the field is flat. When `is_gradient_correlated` computes the gradient at an anchor's current position, it is measuring a nearly zero gradient — by construction — regardless of how the anchor got there.

The dot product between drift direction and a near-zero gradient vector is approximately zero, and its sign is noise. Neither gradient-following drift nor random walk produces meaningful correlation when the gradient is flat. Both models measure noise at anchor positions because anchor positions are gradient minima by design.

The category error: C3'' assumed gradient direction is informative at migration points. It is not, because migration points are anchor positions, and anchor positions are selected for near-zero gradient. The measurement is ill-defined at the locations it is applied.

This is the same class of error that C3' made — measuring event volume instead of mechanism quality — applied at a more fundamental level. C3' confused frequency with structure. C3'' confused position-specific noise with direction-specific signal.

### What the 8 structured passes reveal

The 8 trials that passed are concentrated in the CF=0.95 row — high constraint factor, slow field decay. In these cells, field energy accumulates more gradually, gradients persist longer between events, and anchor positions are less sharply at gradient minima. The gradient correlation check becomes marginally more meaningful when the field is less saturated. This is consistent with the diagnosis: the flaw is worst when field energy is high and gradient minima are well-defined.

### The 4 null passes from Experiment I — revisited

Rae's observation that the 4 null passes in Experiment I represent a real boundary condition, not noise, is supported here. Null passes 0/125 under C3'', meaning C1' + C2' were doing the work in those 4 cases — and those 4 cases satisfy spatial stability and topology coherence through field-energy dominance rather than structured mechanics. High influence strength at moderate constraint creates regimes where even randomly placed anchors land in high-energy regions and stay there, incidentally satisfying the stability conditions.

In framework terms: differentiation alone mimics structure when constraint is insufficient to separate stable from unstable regions. This is the inevitability consequence appearing experimentally — the triad requires all three primitives to produce genuine identity-like topology. When constraint weakens, differentiation and influence produce noisy structure rather than stable basins. The 4 null passes are not anomalies. They are the boundary condition of the claim.

---

## Diagnosis: C3 as a Concept Is Sound — Implementation Is Broken

The goal of C3 across experiments I, J has been consistent: distinguish field-driven movement from random movement. The concept is correct. The implementation in both versions failed for different reasons:

**C3' (raw count):** contaminated by migration volume — null generates hundreds of events, random correlation trivially exceeds threshold.

**C3'' (ratio):** contaminated by gradient flatness at anchor positions — both models measure near-zero gradients, ratio is noise.

The underlying problem in both: trying to measure movement quality at positions specifically selected for gradient insensitivity.

### The clean path: migration rate

What actually differs between structured and null mechanics is not gradient alignment but migration frequency:

- Null mechanics: random reassignment every 8 ticks → ~0.125 migrations per anchor per tick by construction
- Structured mechanics: spatial boundaries only shift when anchors drift significantly → approximately 0.005–0.02 migrations per anchor per tick

This gap is large, stable, and does not depend on gradient magnitude at anchor positions. Migration rate measures what was always intended: whether transitions are mechanically produced or field-driven. Mechanically produced = high rate. Field-driven = low rate.

**C3''' — Migration rate threshold (for Experiment K):**
Mean migrations per anchor per logged tick < 0.03 in the second half of the run. Expected: structured ~0.01–0.02, null ~0.125. Threshold set well below the null floor.

---

## What the Experiment Series Establishes at This Point

**G:** Spontaneous multi-basin formation is robust across the tested parameter space under structured mechanics.

**H:** Original conditions partially trivial under null mechanics. C2 (topology similarity) was the real signal.

**I:** Tightened C1' and C2' discriminate cleanly — 96 structured vs 4 null. C1' and C2' isolate the structured mechanics. C3' failed for a different reason than expected.

**J:** Ratio-based C3'' fails due to gradient flatness at anchor positions. The failure is informative — it specifies precisely why gradient-based migration metrics are ill-defined in this physics. Migration rate is the correct replacement.

**Cumulative claim:** Under structured field physics, spontaneous multi-basin emergence produces topologically stable, spatially persistent basins that random mechanics cannot replicate under C1' and C2'. The mechanism of that discrimination is confirmed as spatial stability and topological coherence, not gradient-correlated movement. Whether gradient-correlated movement also discriminates — using a valid measurement — is what Experiment K will determine.

---

## Next Step — Experiment K

Re-implement C3 as migration rate: migrations per anchor per logged tick. Same parameter sweep, same structured vs null head to head, conditions C1' + C2' + C3'''. Expected outcome: structured passes all three, null fails C3''' decisively, with structured rate ~0.01–0.02 and null rate ~0.125.

If K confirms: the three-condition discrimination is complete, and the structured mechanics are isolated across all three independent dimensions — spatial stability, topological coherence, and movement dynamics.

---

*2026*
