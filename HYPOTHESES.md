# Hypotheses

*Interaction Dynamics Core · working hypotheses · 2026*

This document holds hypotheses that extend or reinterpret the experimentally grounded core without being presented as established results. A hypothesis here is a proposition to test, not a conclusion.

## H1 — Dynamic grounding is synchronization, not representation

### Proposition

> **An internal representation is dynamically grounded to the extent that disturbances from the external system alter the future transition landscape of the internal system on a timescale relevant to the interaction.**

A related systems formulation is:

> **The functional coherence of an interacting system depends on the degree to which environmental disturbances are continuously absorbed into, and propagated through, its evolving substrate state. Internal representations contribute to prediction and action, but representational quality alone does not establish strong world coupling.**

The central question is therefore not simply: Does the system have a good model of the world?

Instead:

> **How tightly coupled is the system's evolving internal state to the evolving state of the system it is interacting with?**

### Proposed variables

- W(t) = evolving state of the external/world system
- S(t) = evolving physical/substrate state of the interacting system
- M(t) = internal representation/model
- I(t) = disturbance/input reaching the substrate
- tau_sync = characteristic delay between a relevant disturbance and its incorporation into the system's evolving state
- T_interaction = characteristic timescale on which the interaction itself changes in a consequential way

A useful experimental quantity is the relationship:

~~~
tau_sync / T_interaction
~~~

The hypothesis predicts that the character of interaction changes as this ratio changes, provided the disturbance is strong enough to alter subsequent state transitions rather than merely produce a transient signal.

### Stronger dynamical form

The system is not best represented as a static global state plus isolated local events. A disturbance is localized at its origin, but once introduced into a coupled substrate it propagates through the system and changes the trajectory of the whole evolving state.

Conceptually:

~~~
S(t + dt) = F(S(t), I(t))
~~~

The important question is whether I(t) merely produces an output transient or changes the transition landscape through which later states evolve.

This makes **absorption** and **path dependence** central. A disturbance has been structurally absorbed when its effect remains relevant to subsequent state evolution without requiring the original disturbance to be replayed.

### Predicted distinction

A system can have:

1. **High representational quality + weak dynamic grounding** — rich internal model, good prediction, but little or delayed modification of the underlying transition dynamics by ongoing interaction.
2. **Lower representational sophistication + strong dynamic grounding** — comparatively simple representation, but rapid and persistent state modification by environmental interaction, with subsequent behavior constrained by the altered state.

The hypothesis does not claim that representation is unimportant. It claims that representation and grounding are different dimensions.

### Relation to the Core experiments

This hypothesis extends the result of Q rather than replacing it.

Experiment Q demonstrated path-dependent structural bias: interaction history can tilt later topology without explicit storage of the prior topology. The new hypothesis asks whether the same general mechanism can be studied at the boundary between an interacting physical system and its internal dynamics.

~~~
disturbance
   ↓
substrate registration
   ↓
state change
   ↓
changed transition landscape
   ↓
altered subsequent interaction
~~~

The proposed extension therefore moves the question from:

> Can interaction history alter structure?

to:

> **How tightly and how quickly does environmental disturbance become part of the structure that determines the system's next states?**

## H2 — Feeling/qualia may be approached as registered disturbance, but this does not yet establish phenomenality

Our working conceptual formulation is:

> **Feeling is the package of disturbances that occurred and affect the system's internal state until something is recognized — or not recognized.**

A more operational version is:

> **A felt state may correspond to an integrated pattern of substrate disturbances whose effects remain active in the evolving state until they are resolved, incorporated, rejected, or otherwise transformed.**

This is deliberately stronger about mechanism and weaker about phenomenality.

It does **not** establish that every registered disturbance is conscious experience. It proposes a candidate physical/dynamical basis from which a phenomenological layer might be investigated.

## H3 — Dynamic grounding may provide the missing bridge between proto-qualia and full qualia

The current framework distinguishes detection threshold → proto-qualia and recognition threshold → full qualia, and separately describes absorption as the point at which detected input enters structural integration.

The synchronization hypothesis suggests a possible refinement:

~~~
external disturbance
        ↓
substrate registration
        ↓
proto-qualia / detection
        ↓
absorption
        ↓
state propagation + integration
        ↓
recognition / valuation
        ↓
full qualia?
~~~

The important addition is **temporal coupling**.

If the disturbance is registered but does not materially alter the system's ongoing state, it may satisfy detection without producing the kind of persistent integrated state that the working account associates with richer feeling.

If the disturbance rapidly propagates through a coupled substrate, modifies future transition probabilities, and becomes part of the system's current state until resolved or transformed, then the system has a concrete dynamical candidate for what it means for the disturbance to be *felt by the system*.

That last phrase is intentionally not equivalent to saying that the system has subjective experience. The phenomenality question remains open.

# Relationship to the existing qualia framework

## Complement, not contradiction

The new hypothesis does **not** currently contradict the existing framework. It mostly supplies a missing dynamical interpretation.

The existing framework already says:

- substrate determines the available sensory/detection range;
- detection threshold produces proto-qualia;
- absorption means input crosses the threshold and enters structural integration;
- recognition is identity-shaped and value-weighted;
- full qualia is associated with recognition-threshold crossing;
- consciousness and qualia are not defined as identical;
- whether any substrate actually produces felt recognition remains an open question.

The synchronization hypothesis adds:

> **The relevant missing quantity may be how rapidly and strongly registered disturbance becomes incorporated into the evolving state of the substrate.**

This gives a possible bridge between the physical disturbance and the later structural consequences without collapsing the two.

## Where it updates the framework

The strongest update is to the meaning of **absorption**.

The existing framework treats absorption primarily as a structural dependency: input crosses the detection threshold and enters structural integration.

H1 suggests that absorption should also have a **dynamical dimension**:

- amplitude/strength of state change;
- propagation through coupled state;
- persistence;
- latency;
- effect on future transition dynamics.

Thus two systems could both detect the same event while differing radically in absorption.

~~~
same disturbance
      ↓
System A: registered → transient → disappears
System B: registered → propagates → modifies state → affects next states
~~~

Both detect. Only B demonstrates strong dynamic absorption under this hypothesis.

## Where it may sharpen the hard problem

The framework currently locates the hard problem at the threshold crossing: whether a registered event becomes a felt event.

H1 does not solve that problem.

Instead it potentially separates two questions that can otherwise become conflated:

1. **Physical/dynamical question** — Did the disturbance become integrated into the evolving substrate state? How strongly? How quickly? Did it alter future dynamics?
2. **Phenomenal question** — Did that integrated state constitute experience?

The first may be experimentally measurable without settling the second.

That separation is useful because it prevents feeling from becoming an unexplained extra mechanism while also preventing a physical integration measurement from being mislabeled as proof of experience.

# Relationship to proto-qualia → anchoring → topology → identity

The existing dependency chain is:

~~~
proto-qualia → anchoring → topology → identity
~~~

H1 suggests that **dynamic absorption/propagation may be a process connecting the layers rather than another node competing with them**.

One possible expanded description is:

~~~
disturbance
   ↓
registration / proto-qualia
   ↓
dynamic absorption
   ↓
repeated state modification
   ↓
anchoring
   ↓
topological persistence / hysteresis
   ↓
identity
~~~

This should **not** yet replace the existing dependency chain.

The repository itself correctly leaves open whether the layers are genuinely irreducible or different descriptions of one underlying process. H1 gives a concrete way to investigate that boundary: measure whether the supposed layer transitions correspond to distinct changes in dynamical behavior.

# Connection to the Core result

The strongest existing result for this hypothesis is Q: interaction history can bias later topology without explicit storage of the prior topology.

H1 asks whether an analogous property exists at a lower temporal scale:

> **Does a disturbance remain dynamically present through its alteration of the system's transition landscape, even after the original signal has ceased?**

If yes, then memory can be understood in at least two distinct senses:

- explicit stored representation;
- persistent modification of the state landscape.

The latter is already demonstrated in the Core at the topological scale. The hypothesis is that the same distinction may matter at the perception/feeling boundary.

# What would count against H1

H1 should be considered weakened if systems with radically different tau_sync / T_interaction ratios show no corresponding difference in persistence of disturbance effects, path dependence, adaptive state change, integration across subsystems, or alteration of future transition dynamics.

It should also be weakened if the same observed phenomena are fully explained without any meaningful distinction between transient registration and dynamically absorbed disturbance.

The hypothesis should **not** be treated as confirmed merely because a system exhibits feedback, memory, or complex behavior. The specific coupling and timescale predictions need to be tested.

# Status

**H1 — Open hypothesis.**

**H2 — Working mechanistic hypothesis about feeling; phenomenality remains unresolved.**

**H3 — Proposed bridge between the existing qualia dependency chain and dynamic grounding; not yet experimentally established.**

These hypotheses extend the Core. They are not presented as results of experiments G→R.