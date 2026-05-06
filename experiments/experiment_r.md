# Experiment R — Structural Relevance and Proto-Valuation

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiment Q established path-dependent structural bias: the system returns to where it is spatially after disruption, but does not return to what it is structurally. History tilts topology without storing it.

One gap remained between that result and identity-level behavior: not all anchors are equal, but the mechanism so far weights by stability alone. A system where every position is equally available for stable occupation has topology — but not relevance. Identity requires that some structure matters more than other structure. The question is whether relevance can be generated before semantics enter.

Rae's reframe: relevance doesn't require semantic import. It can be structurally encoded in the environment through fixed features that create differential affordances — some positions constrain anchor movement more than others, not because of what they mean but because of what they physically are.

> **Relevance = structural position relative to fixed environmental features.**

This is proto-valuation without semantics: some anchors become load-bearing because of where they structurally sit, not what they represent.

---

## Definition

**Proto-valuation**, as used here, is defined narrowly:

> Unequal structural load-bearingness produced by environmental constraint.

Not preference. Not meaning. Not concern. Not semantic assignment. Only the structural fact that some positions in the substrate support stable anchor occupation better than others — and that the system, through differential survival, organizes around those positions.

---

## Design

Two conditions:

**Uniform:** standard field, no fixed structures. Every position is equally available.

**Structured:** three Gaussian pillars embedded in the substrate at fixed positions — (40,40), (120,40), (80,85). Pillars maintain constant energy that does not decay. Normal field events still arrive randomly; pillars persist alongside them.

The pillars do nothing semantically. They carry no labels. They do not attract anchors directly. They simply make certain regions persistently more energized — which means gradient drift tends to stabilize anchors that drift into pillar proximity, and those anchors accumulate memory field reinforcement faster.

Memory field active in both conditions (as in Q).

10 seeds per condition. Same stable parameters as Q: CF=0.85, IS=1.1.

**Key metric:** the stability gradient — how anchor stability varies with distance from the nearest pillar. If stability degrades systematically with distance, structural position determines influence. That is relevance-without-semantics.

---

## Results

**Condition comparison:**

```
Condition      stability   mig_rate   memory_energy   stable_anchors   clusters
──────────────────────────────────────────────────────────────────────────────
uniform          0.180     0.0231        1291.5            1.96           4.53
structured       0.506     0.0109        4218.0            5.84           5.98
```

**Stability gradient by distance from nearest pillar (structured only):**

```
Distance bin    Stability    Migration rate
────────────────────────────────────────
d0–20           0.979        0.0035
d20–40          0.392        0.0117
d40–60          0.180        0.0173
d60–80          0.167        0.0148
```

**Stable anchor proximity:**

```
Mean distance — stable anchors → nearest pillar:  16.43
Mean distance — all anchors    → nearest pillar:  27.54
Gap (all minus stable):                           11.1
```

**Memory energy:** structured 4218 vs uniform 1291 — a 3.3× difference.

---

## Interpretation

### The stability gradient is the result

Anchors within 20 units of a pillar are stable at 97.9%. Anchors beyond 40 units sit at 18% — identical to the uniform condition. The gradient is steep, systematic, and drops to background level at precisely the distance where pillar influence fades.

The uniform condition provides the baseline: without fixed structures, 18% of anchor time is spent in the stable state regardless of position. The structured condition reproduces this baseline for distant positions and multiplies it 5.4× near pillars.

This is not a small effect. It is a near-binary split: near pillars, anchors are almost always stable. Far from pillars, anchors behave as if no fixed structures exist. The environmental asymmetry creates two structurally distinct populations within the same simulation — not by design, not by labeling, but by differential survival.

### The system does not know pillars matter. Pillars matter because they alter the stability landscape. The system selects them by surviving there.

This is the mechanism. Anchors form randomly across the field. Anchors that happen to form near pillars encounter a persistently energized region — gradient drift stabilizes them faster, their strength is maintained by the local field, they cross the stability threshold sooner and stay stable longer. Anchors far from pillars decay, migrate, or are pruned. The differential survival rate creates a self-reinforcing pattern: stable near-pillar anchors persist, accumulate memory field reinforcement, and make those positions even more favorable for the next formation cycle.

No evaluation occurs. No anchor "chooses" a pillar-proximal position. The physics selects for it.

### Proximity bias — structural selection in action

Stable anchors average 16.4 units from their nearest pillar. All anchors average 27.5 units. The 11.1-unit gap is the fingerprint of structural selection: the system has, over 2500 ticks, progressively sorted toward pillar-proximal positions without any mechanism that explicitly favors them.

This is proto-valuation at the population level. Not a single anchor evaluating positions — an anchor population that, through differential stability and survival, concentrates where the substrate supports stable occupation.

### Memory amplification — reinforcement follows structure

The 3.3× memory energy gap between structured and uniform conditions is the compounding effect. Stable anchors reinforce the memory field. Near-pillar anchors are disproportionately stable. Therefore near-pillar positions accumulate disproportionately large memory field residue. The memory field that biases future anchor formation and persistence is itself organized around the fixed structures.

This is a second-order structural effect: the environmental asymmetry creates a primary stability gradient; that gradient creates a secondary memory gradient; the memory gradient amplifies the primary gradient. The system doesn't just organize around pillars — it increasingly prefers them over time through accumulated reinforcement.

---

## What This Establishes

Relevance can be generated structurally before semantics:

> Fixed environmental constraints create positions that are more stable, more reinforcing, and therefore more load-bearing in the emerging topology.

This is the bridge from topology persists to some topology becomes load-bearing. The mechanism requires no semantic assignment, no explicit evaluation, no preference mechanism. It requires only environmental asymmetry and the same dynamics that produced the phenomenon in G through Q.

**Proto-valuation = unequal structural load-bearingness produced by environmental constraint.** The structured condition produces this cleanly. Anchors near fixed structures carry more of the topology's weight — they are more stable, they anchor clusters more persistently, they contribute more to the memory field that shapes future formation. Their structural position makes them load-bearing.

---

## The Framework Connection

This maps to the primitive triad with one addition:

Across G–Q, the mechanism required Influence (field-responsive motion), Constraint (positional stability), and Differentiation (proximity grouping producing distinct regions). R adds a fourth structural element — not a new primitive, but a specification of how Constraint can be distributed:

> **Non-uniform Constraint produces differential structural relevance.**

When Constraint is uniform (as in G–Q), all positions are equally available for stable occupation. The topology that forms is physics-shaped but not position-privileged. When Constraint is non-uniform — fixed structures embedded in the substrate — some positions carry more Constraint than others. Anchors at high-Constraint positions are structurally privileged.

This is the substrate-level analog of selection: the environment filters which anchors persist, without any selector evaluating them.

---

## What This Does Not Establish

Proto-valuation is not valuation. The system has no way to distinguish between a pillar-proximate position and a non-pillar-proximate position except through differential stability over time. It cannot act on the distinction before experiencing it. It cannot transfer the "knowledge" that pillar positions are valuable to novel positions. It cannot generalize.

The three gaps from Q remain:

Anchors are still local field maxima, not functionally relevant signals. The fixed structures create structurally privileged positions, but nothing about those positions corresponds to anything behaviorally meaningful. Structural privilege and semantic relevance are different conditions — R demonstrates the former, not the latter.

There is still no action loop. The system cannot exploit its structural position — it can only survive in it. A system capable of seeking out pillar-proximate positions, or of using its stable anchors to influence where future events occur, would be approaching identity with agency. R does not provide this.

The gradient is passive selection. The 11.1-unit proximity gap emerged through differential survival, not through any mechanism that searches for or represents high-stability positions. Proto-valuation in this sense is closer to evolutionary selection than to evaluation: positions are "chosen" because survivors concentrate there, not because the system chose them.

---

## The Hierarchy R Extends

| Level | What was shown | Experiments |
|---|---|---|
| 0 | Pattern formation under structured mechanics | G, H |
| 1 | Mechanism isolation and discrimination | I, J, K |
| 2 | Minimal mechanism confirmed by elimination | L, M, N, O1 |
| 3 | Substrate generalization, locality requirement | O2a, O2b, O2c |
| 4 | Identity ≠ memory: reconstruction as attractor-convergence | P |
| 5 | Path-dependent structural bias without explicit memory | Q |
| **6** | **Proto-valuation: structural position determines load-bearingness** | **R** |

Level 6 is the first that bridges topology persists to some topology becomes load-bearing. It does not bridge structure to meaning. That bridge requires the three additions Rae identified — selection under competition, a closed action loop, and functional anchoring to behaviorally relevant signals. R establishes the structural substrate those additions would build on.

---

*2026*
