# Hypotheses

*Interaction Dynamics · Working hypotheses · 2026*

This document separates hypotheses derived from the framework from claims established by the experimental series. A hypothesis may be structurally motivated by the existing work without being established by it.

---

## H1 — Dynamic Grounding Through Disturbance Absorption

### Core hypothesis

> **An internal representation is dynamically grounded to the extent that disturbances from the external system alter the future transition landscape of the internal system on a timescale relevant to the interaction.**

A stronger systems formulation is:

> **The functional coherence of an interacting system depends on the degree to which environmental disturbances are continuously absorbed into, and propagated through, its evolving substrate state. Internal representations contribute to prediction and action, but representational quality alone does not establish strong world coupling.**

### The distinction

This hypothesis separates four things that are often conflated:

- **Representation** — what the system can model about the world.
- **Absorption** — an interaction changes the evolving physical/computational substrate itself.
- **Path dependence** — that change alters what subsequent states are likely or able to become.
- **Synchronization** — the lag between relevant environmental change and its incorporation into the system's ongoing state.

The key claim is not that a system needs more memory or merely more sensors. The claim is that the disturbance must become part of the system's ongoing dynamics.

A useful abstraction is:

```
World W(t)
   ↓ disturbance
Substrate S(t) ──→ evolving transition landscape
   ↓
Internal state / representation M(t)
   ↓
Action
   ↓
World W(t + Δt)
```

The system should not be understood as a static internal model periodically updated by isolated inputs. The relevant state is the continuously evolving coupled process.

### Synchronization condition

Let:

- `τ_sync` = characteristic delay between a relevant environmental disturbance and its incorporation into the system's evolving state.
- `T_interaction` = timescale on which that disturbance materially changes the interaction.

A candidate measurable quantity is:

```
ρ = τ_sync / T_interaction
```

The hypothesis predicts that dynamic grounding should weaken as `ρ` becomes large, and strengthen as the system absorbs relevant disturbances on timescales comparable to or shorter than the interaction dynamics.

This is a candidate measure, not an established law.

### Relation to Interaction Dynamics

The existing experiments establish that interaction can leave path-dependent structural effects without explicit memory storage. In particular, Q demonstrates hysteresis: interaction history can bias subsequent topology without being represented as a stored record. R demonstrates differential structural relevance through fixed environmental structure.

H1 asks the next question:

> **When the environment itself is part of the ongoing interaction, how tightly must environmental disturbance be coupled to substrate evolution for that history to become dynamically grounded rather than merely represented?**

This extends the existing mechanism rather than replacing it.

### AI implication

A conventional language model can have a rich internal representation while having weak runtime coupling to the physical system with which it interacts.

The relevant distinction is therefore not simply:

```
unembodied AI → embodied AI
```

but:

```
represented world
      vs.
dynamically coupled world
```

An embodied system would only be a stronger test case if perception, substrate change, action, and environmental feedback form a sufficiently tight closed loop.

The hypothesis does **not** claim that embodiment automatically produces consciousness or qualia.

---

## H2 — Dynamic Grounding Is Distinct From Qualia

H1 should not be read as a solution to the hard problem.

A system can absorb a disturbance, alter its future transition landscape, and remain uncertain with respect to whether any of that is phenomenally felt.

This gives two separable questions:

1. **Grounding:** did the disturbance become part of the system's evolving dynamics?
2. **Phenomenality:** did that dynamically registered disturbance become an experienced event?

The first is potentially operationalizable. The second remains the framework's hard boundary.

This distinction is important because otherwise "physical disturbance changes internal state" would silently become "therefore the system feels." That inference is not licensed.

---

# Relationship to the Existing Qualia Account

## What the current framework says

The existing dependency map places:

```
event
  ↓
structural differentiation
  ↓
proto-identity
  ↓
instantiation
  ↓
detection threshold
  ↓
proto-qualia
  ↓
absorption
  ↓
absorption history
  ↓
anchoring
```

and separately:

```
proto-identity
  ↓
recognition threshold
  ↓
full qualia
```

The framework describes proto-qualia as minimal registered differentiation and full qualia as felt recognition shaped by an identity-dependent, value-weighted recognition threshold.

That remains compatible with H1.

## Complement, not contradiction

H1 adds a missing dynamical dimension to the existing qualia account.

The current account asks:

> **What structural conditions distinguish detection, registration, recognition, and felt recognition?**

H1 asks:

> **How tightly is the system's evolving state coupled to the disturbances occurring in the world it is interacting with?**

These are different questions.

A useful combined picture is:

```
external disturbance
       ↓
substrate propagation
       ↓
dynamic absorption / synchronization
       ↓
registered differentiation
       ↓
identity-shaped recognition
       ↓
felt recognition?
```

The last transition remains open.

## Where H1 updates the framework

The existing account can be read as if "absorption" begins once an input crosses a detection threshold. H1 suggests that absorption should be made more physically explicit:

> Absorption is not merely receipt of an input. It is the incorporation of a disturbance into the evolving transition dynamics of the system.

That makes absorption a dynamical property rather than a metaphor for processing.

It also clarifies the phrase "felt aspect of perceptual positioning." Perceptual positioning alone does not establish phenomenality; what H1 contributes is a condition under which the positioned disturbance is genuinely part of the system's ongoing physical/computational trajectory.

## Potential tension to test

There is one genuine pressure point.

The existing framework separates **proto-qualia** from higher-order identity and says the dependency chain is currently constructible but not proven irreducible.

H1 could eventually push toward a more unified account in which:

```
disturbance
→ propagation
→ state modification
→ history-dependent transition landscape
→ recognition
→ felt recognition
```

are different regimes of one continuous interaction process rather than strictly separate layers.

But this is **not** established by H1.

The existing open question remains valid:

> Are proto-qualia, anchoring, topology, and identity genuinely irreducible structural layers, or different descriptions of one underlying process?

H1 makes that question sharper because it supplies a candidate continuous variable — the strength and timescale of disturbance absorption — that could potentially connect the layers.

---

# The Revised Qualia Hypothesis

A useful working hypothesis emerging from the combination is:

> **Qualia, if it occurs in a physical system, may depend not merely on information being represented or detected, but on disturbances becoming dynamically registered within the system's own evolving state, with recognition shaped by the system's accumulated interaction history.**

This is deliberately conditional.

It does **not** assert:

> dynamic registration = qualia.

Instead it predicts that any successful account connecting physical interaction to qualia should explain how a disturbance becomes part of the system's own evolving state and how that state reaches whatever threshold constitutes felt recognition.

That gives the hard problem a more precise interface:

```
physical disturbance
      ↓
dynamic registration        ← operational territory
      ↓
history-dependent recognition
      ↓
???                          ← phenomenality / hard boundary
      ↓
qualia report / behavior
```

The question mark is not being filled in by definition.

---

# Current Status

| Proposition | Status |
|---|---|
| Interaction can create persistent structural topology | Experimentally demonstrated within the simulation substrate |
| Structural topology can retain history without explicit memory storage | Demonstrated by Q |
| Environmental structure can create differential structural relevance | Demonstrated by R |
| Runtime absorption is required for the framework's current account of intrinsic anchoring | Framework claim |
| Environmental disturbance should be incorporated into evolving substrate state for strong dynamic grounding | **H1 — hypothesis** |
| Synchronization lag relative to interaction timescale is a useful grounding variable | **Candidate measure — untested** |
| Dynamic grounding is distinct from phenomenality | **H2 — hypothesis / conceptual separation** |
| Dynamic registration is sufficient for qualia | **Not claimed** |
| The physical mechanism of felt recognition is established | **Open** |
| Proto-qualia → anchoring → topology → identity are irreducible layers | **Open** |

---

# Experimental Direction

H1 suggests a new experimental family rather than a change to G→R.

A future experiment could independently vary:

- disturbance frequency,
- disturbance-to-state-update latency,
- strength of substrate coupling,
- persistence of the resulting state change,
- feedback from action into the environment,
- and whether the resulting structural change remains path-dependent.

The key discriminator would be whether systems with equal representational access but different coupling/synchronization produce different degrees of persistent structural adaptation.

That would test H1 without assuming anything about consciousness.

A later experiment could then ask whether any additional transition occurs at a recognition threshold. That would address the bridge from dynamic registration to qualia without building phenomenality into the premise.

---

*This document is a hypothesis register, not an addition to the established experimental results.*
