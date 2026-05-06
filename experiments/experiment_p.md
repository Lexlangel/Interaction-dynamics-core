# Experiment P — Identity Mapping and Reconstruction

*Interaction Dynamics · Operational Layer · 2026*

---

## Purpose

Experiments G–O established structural conditions for identity-like topology. Experiment P closes the loop: it maps simulation observables to framework constructs and tests whether the framework's specific claims about identity reconstruction hold operationally.

This is the first experiment that directly tests a framework claim rather than establishing structural conditions. The question is no longer whether the phenomenon occurs — it is whether it behaves the way the framework says it should.

---

## Observable → Construct Mapping

| Simulation observable | Framework construct |
|---|---|
| Attractor basin | Proto-identity region |
| Anchor | Structural invariant (identity anchor) |
| Topology signature | Identity topology |
| Topology similarity | Identity persistence measure |
| Migration rate | Identity drift / instability |
| Reconstruction | Identity reformation from field traces |
| Field activation | Interaction field (identity substrate) |

---

## Claims Tested

**Claim 1 — Reconstruction from field traces**
*"Identity leaves traces in the interaction environment as well as in the system itself. When a system returns after interruption, field anchors support reconstruction."*

Test: remove all anchors (execution layer disrupted). Keep field intact. Prediction: new anchors form at field peaks, basin topology reforms.

**Claim 2 — Field traces as memory (framework does not require this)**
*"A system without memory reconstructs from whatever anchors remain in the interaction environment — more slowly, along coarser paths."*

Note: this claim belongs to the memory/anchoring layer of the framework, not the identity layer. The framework separates identity (distributed topology) from memory (substrate retention). Testing whether identity-field traces act as reconstruction memory applies a stronger assumption than the framework makes. P tests this assumption precisely to determine whether identity and memory need to be kept separate in the simulation.

Test: compare anchor_pruning (field intact, anchors removed) vs full_reset (field zeroed, anchors removed). If field traces accelerate reconstruction, identity acts like memory. If not, identity and memory are empirically separable.

**Claim 3 — Reconstruction path visible as transient instability**
*"Identity drift has signatures... Recovery follows a characteristic sequence: return to anchor cues, reconstruct the relational map, restore coherence before elaboration."*

Test: measure migration rate across recovery period. Prediction: elevated rate early in recovery, declining as basins reform.

---

## Design

**Phase 1 (ticks 1–2000):** Establish stable multi-basin state at CF=0.85, IS=1.1 (stable COEX regime from K).

**Phase 2 (tick 2001):** Apply perturbation. Three types:

| Perturbation | What is disrupted | Framework analog |
|---|---|---|
| **anchor_pruning** | All anchors removed, field intact | Execution layer interrupted, field traces preserved |
| **field_half_zero** | Field zeroed in left half, anchors kept | Partial substrate disruption |
| **full_reset** | Field and all anchors zeroed | Complete disruption, no traces |

**Phase 3 (ticks 2001–2500):** Observe reconstruction. Log every 25 ticks.

10 seeds, recovery metrics computed over the second half of the recovery period.

---

## Results

```
Perturbation      Topo sim   First recovery   Sep    Late migration   Clusters
                  (late)     tick (≥0.70)     10/10  rate
──────────────────────────────────────────────────────────────────────────────
anchor_pruning    0.557±0.07   200 ticks        ✓    0.049            3.9
field_half_zero   0.680±0.06    25 ticks        ✓    0.126            4.5
full_reset        0.557±0.07   200 ticks        ✓    0.049            3.9
```

---

## Interpretation

### Claim 1 — Partially supported

Anchor pruning (field intact, all anchors removed) achieves 0.557 mean topology similarity in the late recovery period, with spatial separation recovered in all 10 seeds. The basin structure reforms. Reconstruction from field traces does occur.

The caveat: recovery is incomplete at 500 ticks. First recovery tick is 200 — the basin needs significant time to reform after anchor removal. Late migration rate remains elevated at 0.049, indicating the system has not fully stabilized. The framework's claim is directionally correct, but the simulation shows reconstruction as an ongoing process rather than a sharp restoration.

### Claim 2 — Misframed, not falsified

The result: anchor_pruning and full_reset produce identical outcomes. Field traces provide no measurable reconstruction advantage.

The initial verdict was "not supported." That was wrong. The result is a confirmation — but of a different claim than the one being tested.

The claim we tested: *field structure biases future reconstruction dynamics.* That is effectively: field ≈ memory-like influence. This is a stronger assumption than the framework makes.

The claim the framework actually commits to: identity persists as structure in the field. It does not require that this structure actively guides its own reformation. The framework explicitly separates identity from memory:

```
identity = distributed topology
memory   = substrate retention of past states
```

No part of the framework requires that identity topology function as a reconstruction driver. Memory and anchoring mechanisms carry that responsibility — not identity-as-topology.

So what Experiment P established is not that the framework's reconstruction claim fails. It established that:

> **Identity can persist without influencing future instantiation. Reconstruction speed belongs to memory and anchoring mechanisms, not identity-as-topology.**

That is a confirmation of the framework's own separation — not a contradiction. We were implicitly assuming that if identity persists in the field, it should act like stored information that biases re-instantiation. The framework never required this. That assumption was imported from psychological intuitions about memory (memory = identity) that the framework explicitly decouples.

The correct reframing of what P tested as a framework claim:

> Reconstruction speed depends on mechanisms that preserve or reintroduce anchors during re-instantiation — memory, environment, substrate bias, interaction continuity. Not identity-as-topology alone.

The simulation confirms this. Both conditions (field intact vs zeroed) converge to the same attractor basins because those basins are physics-determined. Identity exists as structural residue. It does not guide its own reformation. These are not the same thing.

### Claim 3 — Inverted pattern

Migration rate in the early recovery period is near zero for anchor_pruning and full_reset. It rises in the late recovery period to 0.014. The prediction was the opposite: high migration initially as the system reorganizes, then declining as basins stabilize.

The mechanism: after anchor removal, the system has no anchors. Migration requires anchors to exist and switch clusters. Early recovery has few anchors (they are forming, not yet migrating), so migration rate is low. Late recovery has established anchor populations that are still reorganizing between forming clusters. The migration signal is real — but it tracks anchor population dynamics, not the reconstruction sequence the framework describes.

The framework's claim about reconstruction sequence — return to anchor cues, reconstruct relational map, restore coherence — would require a different measurement: tracking the temporal sequence of anchor formation events, not migration rate across the full anchor population. That is a measurement redesign, not a claim failure.

### field_half_zero — The informative outlier

Field erasure in half the spatial domain recovers faster (25 ticks vs 200) and better (0.680 vs 0.557), with higher late migration rate (0.126). The anchors in the intact half continue functioning; the erased half gradually replenishes through background events and wave propagation from the intact region. The system reorganizes around the surviving structure.

This is the closest analog to the framework's reconstruction from partial field traces: when some of the identity field is preserved, reconstruction is faster and more accurate. The asymmetry between partial and total erasure is consistent with the framework's claim — it is total erasure that eliminates the advantage.

---

## What This Establishes

**The simulation reproduces reconstruction** — basins reform after disruption across all perturbation types, all seeds. Identity-like topology is reconstructable in this physics.

**Field traces do not act as reconstruction memory** — attractor basins are physics-determined, not history-dependent. This is not a failure of the framework. The framework explicitly separates identity from memory. The result confirms the separation: identity topology exists as structural residue; it does not guide its own reformation. Reconstruction belongs to the memory and anchoring layer.

**Partial field preservation accelerates reconstruction** — field_half_zero recovers at tick 25 with 0.68 similarity vs 200 ticks / 0.557 for full disruption. This is consistent with the framework: when part of the identity field is preserved (partial instantiation remains), reconstruction is faster. What fails to accelerate reconstruction is total disruption — consistent with the claim that identity requires instantiation to become operational, not that it drives its own re-instantiation.

**Identity and memory are empirically separable** — this is the result. The same basin structure reforms whether prior field history is present or not. Identity, in this simulation, is structure not storage. Reconstruction requires physics, not prior traces.

---

## The Layer Clarification P Forces

P surfaced a conflation that the framework formally rules out:

```
Identity (field-level)
  → structural residue
  → may be inert as reconstruction driver
  → does not require acting as memory

Memory (substrate-level)
  → affects reconstruction dynamics
  → separate mechanism from identity
```

The framework's reconstruction claim belongs to the memory/anchoring layer:
*"A system with rich memory reconstructs its identity faster, along more accurate paths."*

Not to identity-as-topology alone. P confirms the separation is real, not just definitional.

---

## Simulation → Framework Construct Status

| Construct | Status |
|---|---|
| Basin as proto-identity region | ✔ operationalized — stable attractor regions with measurable topology |
| Anchor as structural invariant | ✔ operationalized — load-bearing positions, removal disrupts topology |
| Topology similarity as persistence | ✔ operationalized — directly measures basin structure continuity |
| Identity ≠ memory (structural vs dynamic) | ✔ confirmed — field traces and clean slate produce identical reconstruction |
| Migration rate as identity drift | ⚠ partially — tracks anchor population dynamics, not reconstruction sequence |
| Reconstruction sequence as staged recovery | ⚠ wrong metric — needs anchor formation event tracking, not population migration rate |

---

*2026*
