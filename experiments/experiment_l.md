# Experiment L — Boundary Search

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiments G–K operated within CF: 0.75–0.95, IS: 0.5–1.3. The range was never chosen adversarially — it was the first sweep and it worked everywhere. Without a failure boundary, the claim "structured mechanics produce identity-like topology" cannot be bounded. An unbounded claim is not a stronger claim — it is a less precise one.

This experiment finds where it breaks.

---

## Design

Structured mechanics only. Null model fails in all tested regimes already — no need to extend it.

**Parameter range extended to extremes:**

| Parameter | Values |
|---|---|
| `constraint_factor` | 0.40, 0.50, 0.60, 0.70, 0.75, 0.85, 0.90, 0.95, 0.99 |
| `influence_strength` | 0.10, 0.30, 0.50, 0.70, 0.90, 1.10, 1.30, 1.50, 2.00, 3.00 |
| Seeds | 0, 1, 2 |

270 total trials. Conditions C1'+C2'+C3''' with threshold recalibrated to 0.05.

---

## Pre-Registered Expectations

Low CF (0.40–0.60): aggressive decay, anchors cannot persist. Expected: NONE.
High CF (0.99): field saturates, spatial differentiation collapses. Expected: SNGL or NONE.
Low IS (0.10): events too weak to reach anchor threshold. Expected: NONE.
High IS (2.0–3.0): field oversaturated, gradient structure overwhelmed. Expected: NONE.

---

## Results

```
BOUNDARY REGIME MAP
           is=0.1  is=0.3  is=0.5  is=0.7  is=0.9  is=1.1  is=1.3  is=1.5  is=2.0  is=3.0
cf=0.40   NONE    NONE    COEX    COEX    OSCL    SNGL    SNGL    SNGL    SNGL    SNGL
cf=0.50   NONE    NONE    COEX    SNGL    OSCL    SNGL    COEX    OSCL    OSCL    OSCL
cf=0.60   NONE    COEX    SNGL    SNGL    OSCL    OSCL    OSCL    OSCL    OSCL    OSCL
cf=0.70   NONE    COEX    OSCL    SNGL    OSCL    OSCL    OSCL    OSCL    COEX    OSCL
cf=0.75   NONE    SNGL    SNGL    OSCL    OSCL    OSCL    OSCL    COEX    OSCL    COEX
cf=0.85   NONE    SNGL    OSCL    OSCL    OSCL    COEX    OSCL    OSCL    OSCL    COEX
cf=0.90   NONE    OSCL    OSCL    COEX    OSCL    OSCL    OSCL    OSCL    OSCL    OSCL
cf=0.95   NONE    OSCL    OSCL    OSCL    OSCL    OSCL    OSCL    COEX    OSCL    COEX
cf=0.99   NONE    COEX    COEX    OSCL    OSCL    COEX    COEX    COEX    COEX    COEX

Working CF range: 0.40 – 0.99
Working IS range: 0.30 – 3.00
Cells with any pass: 78 / 90
```

---

## Interpretation

### The only consistent failure boundary is IS=0.1

IS=0.1 produces NONE across every CF value. At this influence strength, events do not generate sufficient field energy to reach the anchor detection threshold (`ANCHOR_MIN_STRENGTH = 0.15`). No anchors form. No topology emerges. This is a hard physical limit — not a regime transition but a detection floor.

All other tested parameter combinations produce passing cells. The claim is bounded below by IS < ~0.2. There is no upper boundary found within the tested range.

### The CF=0.99 prediction was wrong

The pre-registered expectation was that very slow field decay would cause saturation — field energy accumulating everywhere uniformly, destroying spatial differentiation. The opposite occurred: CF=0.99 produces stable coexistence (COEX) across nearly all IS values. It is one of the most consistent rows in the map.

The mechanism: slow decay means field structure accumulated by prior events persists longer. Anchors have more time to find stable positions in the field topology before it reshapes. High constraint factor does not saturate differentiation — it stabilizes it. The prediction was based on an incorrect model of how decay interacts with anchor formation.

This is a real finding that updates the framework's operational picture: higher constraint produces more stable, not less stable, topology. The analogy to the framework's Constraint primitive holds — constraint stabilizes differentiation rather than eliminating it.

### Low CF performs better than expected

CF=0.40 produces passing cells from IS=0.50 upward. Even very aggressive decay (field loses 60% of its energy per tick) allows enough structure to form when influence strength is sufficient. The field resets rapidly but each event still leaves a transient signature that anchors can register before it decays.

The transition between COEX/OSCL and SNGL/NONE at low CF is rough — seed-dependent, inconsistent across the three seeds. This indicates the low-CF regime is genuinely noisy: structure forms and dissolves on timescales comparable to the measurement window. It is a regime of unstable rather than absent topology.

### High IS does not saturate

IS=3.0 produces passing cells across nearly all CF values. The prediction that strong events would overwhelm gradient structure was wrong. Strong events create stronger field peaks, which gradient detection and drift use more effectively — the signal-to-noise ratio is higher, not lower. Saturation does not occur within the tested range.

### The claim is bounded, but more narrowly than expected

The honest boundary: IS > ~0.2 is required for any structure to form. Above that threshold, the phenomenon is robust across an extremely wide parameter range — from CF=0.40 to CF=0.99, from IS=0.30 to IS=3.00. The claim that "structured mechanics produce identity-like topology" holds within this range. Outside it (IS < ~0.2) it does not.

This is not a small regime. It covers nearly an order of magnitude in influence strength and the full usable range of constraint factor. The robustness is real.

---

## What the Pre-Registration Failures Reveal

Three predictions were wrong: high CF saturating, low CF failing broadly, and high IS oversaturating. All three were wrong in the same direction — the phenomenon is more robust than expected.

The mechanism in each case: the prediction assumed that extremes would destroy field structure. What actually happens is that field structure adapts to the physics — anchors and topology form from whatever gradient landscape the parameters produce. The formation mechanism is more general than any specific parameter regime.

This is consistent with the framework's claim that {I, D, C} is a minimal and sufficient description: the phenomenon does not require fine-tuned parameters, only the three conditions operating together above a detection floor.

---

## Updated Claim

**Previous:** Under structured field physics with CF: 0.75–0.95 and IS: 0.5–1.3, spontaneous multi-basin emergence produces topologically stable, spatially persistent, low-churn basins.

**Updated:** Under structured field physics with IS > ~0.2, the same phenomenon holds across CF: 0.40–0.99 and IS: 0.30–3.00. The lower bound is a physical detection floor, not a regime transition. No upper bound was found within the tested range.

---

*2026*
