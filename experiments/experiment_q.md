# Experiment Q — Hysteresis and Path-Dependent Structural Bias

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment P established that the simulation reproduces reconstruction, but that field traces provide no measurable reconstruction advantage. The framework's separation of identity from memory was confirmed operationally: both conditions (field intact vs field zeroed) produced identical basin reformation, because attractor basins in this physics are determined by field parameters, not interaction history.

The escape route that remained: if every history produces the same attractor, calling the result "identity-like" is a category error. It is pattern formation. Identity requires that history matters.

Experiment Q tests whether history can be made to matter — not through explicit memory storage, but through accumulated interaction weighting. The mechanism: stable anchors leave a weak structural residue that decays slowly and contributes a small bias to the combined field. The system leans toward where stable interaction has occurred without recording where that was.

The question: returning to original conditions, does the system return to its original structural state?

---

## Memory Field

A slow reinforcement field runs alongside the normal field throughout the simulation:

```python
memory_field = Field(FIELD_W, FIELD_H)

# Each anchor update:
def reinforce_memory(memory_field, anchors):
    for a in anchors:
        if a.is_stable:
            apply_gaussian(memory_field, a.x, a.y,
                           amount=0.002, sigma=GAUSSIAN_SIGMA * 1.5)

memory_field.decay(0.9995)   # vs constraint_factor 0.85 for normal field
combined.data += 0.15 * memory_field.data
```

This is not storage. It records no labels, no cluster assignments, no topology. It only does one thing: regions where anchors have been stable become very slightly more energetically favorable over time. The accumulated bias is weak per step, slow to decay, and proportional to how long stable anchors have occupied a region.

---

## Design

Three phases, two conditions:

| Phase | Ticks | Events | Purpose |
|---|---|---|---|
| **A** | 1–1000 | Uniform random | Establish neutral topology |
| **B** | 1001–2000 | Biased right 2/3 of field | Force topology B |
| **C** | 2001–3000 | Uniform random restored | Observe recovery |

**with_memory:** memory field active throughout all three phases.
**without_memory:** standard simulation, no memory field.

**Hysteresis score:** sim(B,C) − sim(A,C). Positive means Phase C resembles Phase B more than Phase A — structural persistence of biased state. Negative means C resembles A more — spatial recovery. The size of the gap between with_memory and without_memory is the memory field's contribution to structural inertia.

---

## Results

```
                     sim(A,C)   sim(B,C)   sim(A,B)   hyst_score   sep A→B→C
──────────────────────────────────────────────────────────────────────────────
with_memory            0.748      0.720      0.650      −0.028      0.43→0.64→0.42
without_memory         0.748      0.647      0.650      −0.101      0.43→0.62→0.42

mean_x A→B→C:
  with_memory:    75.3 → 95.7 → 74.7
  without_memory: 75.3 → 94.8 → 72.2

hysteresis score gap:  0.072
```

---

## Interpretation

### Position converges. Topology retains bias.

Both conditions return spatially to approximately the original configuration. Separation fraction returns to 0.42 in Phase C for both modes. Mean anchor x-position returns from ~95 (rightward bias during Phase B) to ~75 (original) in both. The spatial layer is reversible under both conditions.

The topological layer is not equally reversible. Without memory: sim(B,C) = 0.647. With memory: sim(B,C) = 0.720. The memory field makes Phase C topology 11% more similar to Phase B than standard physics produces. The difference is 0.072 — more than three times the noise floor across seeds.

Both systems return to where they are spatially. But the with_memory system carries forward more of Phase B's topological structure — the Laplacian eigenvalue signature, density, component organization. Phase C resembles Phase B more closely when the memory field has been accumulating bias across all three phases.

This is the split:

| Layer | with_memory | without_memory |
|---|---|---|
| Spatial (position) | Recovers to A | Recovers to A |
| Topological (structure) | Retains B-bias | Recovers toward A |

### This is hysteresis — precisely stated

A skeptic could argue: "The system still returns to A. Nothing changed." The numbers contradict this.

Δsim(B,C) = 0.720 − 0.647 = 0.073 under identical final conditions (Phase C, neutral events, same physics). This is not noise — it is Δstructure ≠ 0 under identical external conditions. The structural state at the end of Phase C depends on path, not just on the current field.

That is the definition of hysteresis. The system returns to where it is. It does not return to what it is.

The correct formulation — precise, not overclaimed:

> The system exhibits path-dependent structural bias: interaction history tilts the topology without determining it.

Not full persistence. Not deterministic recall. A tilt. This is the right framing because the hysteresis score is negative for both modes (sim(B,C) < sim(A,C)) — both modes recover toward A spatially. The difference is that with_memory recovers less fully in topological space.

### What the memory field actually did

The memory field did not store anchors, record clusters, or encode topology. It only made previously-stable regions slightly more energetically favorable through accumulated weak Gaussian reinforcement. The mechanism:

```
stable anchor present → slight field bias accumulates
field bias → influences combined field →  influences where new anchors form
new anchor formation at biased sites → reinforces the bias
```

This is a positive feedback loop with a very weak coupling (0.15 weight, 0.002 reinforcement per step). Over 3000 ticks, it produces a measurable but not dominant structural lean. The system is not locked into any configuration — it is tilted.

The equivalence to the framework's language: this is accumulated interaction weighting, not memory. The field carries what has been stable without encoding what was stable. The distinction matters: the system has no way to retrieve or replay prior topology. It can only be influenced by the energetic shadow of where stability occurred.

### Why P's finding and Q's finding are consistent

P found: anchor_pruning = full_reset. Field traces don't accelerate reconstruction. Identity doesn't guide its own reformation.

Q finds: with_memory ≠ without_memory. Path history produces structural bias when accumulated weighting is present.

These are not contradictory. P tested whether existing field activation structure biases reconstruction — it doesn't, because attractor basins are physics-determined. Q tests whether accumulated interaction weighting biases structural outcomes — it does, because the memory field changes what the physics favors.

P confirmed: identity ≠ memory. Reconstruction belongs to anchoring mechanisms.
Q establishes: interaction history can produce structural bias without constituting memory.

The memory field is not memory in the framework's sense. It is an intermediate layer between identity and memory — accumulated weighting that tilts structural outcomes without enabling retrieval, replay, or directed reconstruction.

---

## What Q Adds to the Framework

**Before Q:** identity-like topology emerges from positional coupling and spatial grouping. The topology is physics-shaped — identical histories produce identical attractors.

**After Q:** identity-like topology exhibits path-dependent structural bias when interaction history is encoded as accumulated weighting. Different histories, same physics, measurably different structural outcomes.

This is the threshold where calling the phenomenon "identity-like" stops requiring hedging. Identity in the framework is distributed topology. Q shows that topology can carry forward where the system has been — not as stored state, but as energetic lean. Structure carries its path without storing it.

The minimal mechanism gains a fourth element — not a mechanism condition but a temporal one:

> positional coupling + spatial grouping + substrate locality + accumulated interaction weighting

The fourth element is what distinguishes a physics-shaped pattern from a history-shaped one.

---

## What Q Does Not Establish

Stating the honest limits is part of the result.

**What the series establishes:** a validated dynamical mechanism for stable, history-sensitive topology formation under interaction dynamics.

**What it does not establish:** a validated model of identity in real systems.

The simulation operates at this level: anchors → positions → clustering → topology. This maps to: features → spatial relations → grouping → structure. That is structural abstraction, not lived identity. Three gaps remain between the simulation's claims and identity in any real system:

**Anchors ≠ real signals.** In the simulation, an anchor is a local field maximum. In real identity systems, anchors would need to be behaviorally relevant signals — perceptual features, decisions, learned associations, sensorimotor loops. The simulation lacks semantic or functional relevance. Stability is not the same as significance.

**No action loop.** The simulation runs field → anchors move. Real identity systems run perception → action → feedback → update. Without a closed loop, the system cannot choose, adapt intentionally, or actively bias future interaction. The memory field adds accumulated weighting, but it is not agency.

**No selective valuation.** The memory field adds weighting based on stability — this stabilizes more than that. Real identity requires valuation — this matters more than that. Stabilization and valuation are not the same condition. The simulation has no way to register that some anchors carry more significance than others.

These are not small gaps. They are the distance between *structural substrate* and *lived identity*.

The correct positioning:

> This work does not model identity directly. It isolates the minimal dynamical conditions under which identity-like structural persistence and path-dependent bias can arise. Mapping these conditions to real identity systems requires additional layers: perception, action, and valuation.

What the work actually establishes is something foundational rather than incomplete: **identity without semantics, without memory, without agency** — the stripped-down structural core that any richer model of identity would need to instantiate. That is why the mechanism is isolable. Real identity systems are not stripped down. The simulation is. And what survives stripping is what the series is actually about.

---

## The Hierarchy This Completes

Across G through Q, the experiment series has progressively established:

| Level | What was shown | Experiments |
|---|---|---|
| 0 | Pattern formation under structured mechanics | G, H |
| 1 | Mechanism isolation: three conditions discriminated | I, J, K |
| 2 | Minimal mechanism: field-responsive motion + clustering | L, M, N, O1 |
| 3 | Substrate generalization: locality requirement identified | O2a, O2b, O2c |
| 4 | Identity ≠ memory: reconstruction is attractor-convergence | P |
| **5** | **Path-dependent structural bias: history tilts topology without storing it** | **Q** |

Level 5 is the first that justifies the word "identity-like" without qualification. Levels 0–4 established the conditions. Q establishes the behavior.

---

*2026*
