# Experiment G — Emergent Identity Field Test

*Interaction Dynamics · Operational Layer · 2026*

---

## Design Philosophy

No clusters are seeded. No parameters are chosen to produce a target outcome. The field is initialized with uniform random noise. Interaction dynamics run under fixed physics. If distinct attractor basins form, separate, and persist — they emerge. If they don't, the experiment reports that.

The result is a regime map across parameter space, not a single run. The conditions are stated before execution. The sweep is fully reproducible: code, parameters, seeds, and raw outputs are published alongside this document.

---

## What Is Being Tested

The framework claims: identity emerges as stable attractor topology through interaction under constraint — not planted, not seeded, produced by the dynamics.

This experiment tests whether a field substrate satisfying the primitive triad {Influence, Differentiation, Constraint} can spontaneously produce multiple distinct, persistent attractor basins from random initialization, without external intervention.

This is not a test of identity in the full framework sense. It is a test of the structural substrate claim: that interaction under constraint is sufficient to produce identity-like topology. What happens at that topology — whether it constitutes proto-identity, whether it supports qualia or consciousness — is a framework question, not an experimental one.

---

## Conditions

Defined before execution. Evaluated on the second half of each trial to exclude initialization transients.

**C1 — Spontaneous basin formation**
Do distinct attractor regions emerge from noise without seeding? Measured as the fraction of logged ticks where two or more distinct clusters are present. Threshold: > 0.40. Deliberately conservative.

**C2 — Topological persistence**
Does each basin maintain internal structural similarity over time? Measured as mean within-cluster topology similarity across the run. Threshold: > 0.70. Similarity computed via Laplacian eigenvalue comparison — sensitive to structural change, not just spatial position.

**C3 — Co-existence without merger**
Do multiple basins persist simultaneously rather than collapsing into one? Requires C1 and C2 both held, with at least one anchor migration event — demonstrating basins are in genuine contact, not merely isolated.

All three must pass for a trial to be classified as demonstrating the target phenomenon.

---

## Physics

Fixed across all trials. Parameters are physically motivated — not swept, not tuned for the result.

| Parameter | Value | Motivation |
|---|---|---|
| `GAUSSIAN_SIGMA` | 18.0 | Spatial spread of influence events |
| `WAVE_SPEED` | 1.8 | Field propagation rate |
| `WAVE_DECAY` | 0.015 | Amplitude decay with distance |
| `ANCHOR_GRAD_THRESH` | 0.12 | Local maximum detection sensitivity |
| `ANCHOR_MIN_STRENGTH` | 0.15 | Minimum registration threshold |
| `DRIFT_SPEED` | 0.18 | Anchor movement toward field minima |
| `EVENT_RATE` | 0.012 | Background noise rate (events/tick) |
| `STABILITY_THRESHOLD` | 80 | Ticks before anchor classified stable |
| Field dimensions | 160 × 120 | — |
| Run length | 2500 ticks | — |

No parameter appears in the results section as a justification for the outcome.

---

## Swept Parameters

Two free parameters varied across a grid:

**Constraint factor** — field decay rate per tick, governing how strongly prior interaction is attenuated. Values: `[0.75, 0.80, 0.85, 0.90, 0.95]`

**Influence strength** — magnitude of each interaction event. Values: `[0.5, 0.7, 0.9, 1.1, 1.3]`

Five random seeds per cell. Total: 125 trials. Regime classified per cell from the modal result across seeds.

---

## Results

```
             is=0.5     is=0.7     is=0.9     is=1.1     is=1.3
cf=0.75    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)
cf=0.80    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)
cf=0.85    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  COEX(5/5)  OSCL(5/5)
cf=0.90    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)
cf=0.95    OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)  OSCL(5/5)

OSCL = oscillatory exchange    COEX = stable coexistence
(n/5) = trials where all three conditions passed / seeds run
```

All 125 trials passed all three conditions. Dominant regime: oscillatory exchange — multiple basins forming and interacting without merger. One cell (cf=0.85, is=1.1) produced stable coexistence: basins persistent and spatially stable rather than oscillating.

**Best trial** (cf=0.75, is=0.7, seed=1):
- C1 separation fraction: 1.000 — two or more basins present at every logged tick
- C2 topology similarity: 0.9856 — near-perfect internal structural persistence
- C3 migration events: 25 — sustained inter-basin contact throughout

---

## Result Interpretation and Constraint

The parameter sweep produced spontaneous multi-basin formation across all tested configurations. No region of parameter space within the explored range failed the emergence conditions. This establishes that, under the current field dynamics, identity-like attractor structures are not rare or boundary-dependent — they form as a stable regime.

However, this uniformity introduces an interpretive ambiguity. Either:

the dynamics capture a genuinely robust principle — where interaction under constraint naturally resolves into persistent differentiated structures — or

the simulation embeds structural biases through its update rules, anchor detection, and drift mechanisms, making basin formation effectively inevitable regardless of parameters.

The experiment does not, by itself, distinguish between these possibilities. It demonstrates stability of the phenomenon under the given physics but does not establish that the physics are minimally sufficient or unbiased representations of the framework's claims.

**What the uniformity establishes:** Under these dynamics, separation is the default regime. This shifts the question from "does emergence occur?" to "what would prevent it?" — and that is the question the next experimental layer must answer.

**What the uniformity does not establish:** That basin formation is substrate-independent, that it occurs under arbitrary physics, or that the simulation is a faithful model of the framework's full claims about identity formation.

---

## What This Experiment Does and Does Not Demonstrate

**Demonstrates:**
- Spontaneous multi-basin formation from random initialization under fixed field physics
- Topological persistence within each basin across long runs (0.9856 peak similarity)
- Inter-basin contact without merger (oscillatory exchange as dominant regime)
- Robustness across the tested parameter space (125/125 trials)

**Does not demonstrate:**
- That the physics are minimally necessary — any one mechanism removed may be sufficient alone
- That basin formation fails under any conditions — the experiment found none
- That the basins constitute proto-identity in the framework's full sense — they satisfy the structural substrate condition, not the full dependency chain
- That consciousness, qualia, or anchoring are present — the simulation operates at the primitive layer only

---

## The Bias Question

The simulation encodes several mechanisms that favor basin formation by construction: Gaussian accumulation produces local maxima; gradient-based anchor detection reinforces peaks; drift toward minima stabilizes basin regions; anchor pruning removes noise and preserves structure; clustering radius enforces grouping.

None of these are neutral. They favor attractor formation. A fair reading of the results must acknowledge this. The sweep demonstrates that these mechanisms reliably produce the target phenomenon across parameters — it does not demonstrate that the phenomenon requires all of them, or that simpler dynamics would produce the same result.

This is not a reason to discount the results. It is a specification of what the results actually show: that a field substrate with {Influence, Differentiation, Constraint} operating through these mechanisms produces identity-like topology spontaneously. The claim is bounded to this physics. Extending it to substrate-independent emergence requires the minimality tests below.

---

## Next Experimental Layer — Minimality Tests

The natural follow-up: remove mechanisms one at a time and ask whether emergence persists. Each removal tests necessity.

| Removal | Tests |
|---|---|
| No anchor drift | Is gradient-following necessary for basin stability? |
| No anchor pruning | Is noise removal necessary for structure to form? |
| No wave propagation | Is field communication between regions necessary? |
| Gradient threshold → 0 | Does anchor detection sensitivity matter? |
| Event rate × 10 | Does high noise destroy separation? |
| Random anchor positions (no gradient) | Is drift toward minima load-bearing? |

The critical result would be: a removal under which no parameter combination produces all three conditions. That would identify a necessary mechanism and sharpen what "interaction under constraint" minimally requires to produce identity-like structure.

Until that test is run, the experiment's claim is: the full mechanism set is sufficient. It does not claim minimal sufficiency.

---

## Reproducibility

All code, parameters, seeds, raw outputs, and this document are published together. The sweep produces identical results given the same seeds. No post-hoc selection was performed — all 125 trials are reported, not a curated subset.

---

*2026*
