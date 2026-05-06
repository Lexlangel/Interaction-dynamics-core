# The Experiment Series: G → R

*Interaction Dynamics · Operational Layer · 2026*

---

This document covers fifteen experiments as a single arc. The individual experiment files contain full design specifications, raw results, and condition definitions. This document covers what each experiment established, why the next one became necessary, and where the series ended.

The arc is the argument. No individual experiment makes it alone.

---

## I. Finding the Phenomenon (G, H)

The first experiment ran 125 trials across five constraint factors and five influence strengths. In each trial, the simulation started from a flat field with no seeding — random event injection only. The question was whether distinct attractor basins would emerge spontaneously from this initialization.

All 125 trials passed. Every parameter combination produced stable multi-basin topology. The phenomenon was robust across the full tested range.

That uniformity was the first signal that something might be wrong. A genuine result usually has edges. Passing everywhere, across every parameter combination, across every seed — that is either a very strong result or a measurement problem.

Experiment H answered the question: it was a measurement problem. Replacing all three structured mechanics — gradient detection, drift, and cluster assignment — with random equivalents, and running the same 125 trials, produced 109 passes under the original conditions. The null model was satisfying the conditions almost as often as the structured model.

The diagnosis from H was precise: two of the three conditions were too easy. C1 (mean cluster distance) was trivially satisfied by any anchor configuration with multiple groups. C3 (gradient-correlated migration count) was backwards — the null model generated hundreds more migration events than structured mechanics, and random assignment correlated with the gradient by chance at nearly the expected rate. Only C2 (topology similarity) was doing real discriminative work: 0.9439 structured vs 0.7949 null.

H did not undermine the phenomenon. It demanded conditions worthy of it.

---

## II. Building the Discriminator (I, J, K)

Experiment I introduced tightened conditions. C1' required spatial stability — mean centroid distance above a threshold with low variance. C2' raised the topology similarity bar to 0.85. C3' measured gradient-correlated migrations.

The result: 96/125 structured passed, 4/125 null passed. The discrimination was real. But C3' failed in a specific way — the null model still outperformed the structured model on gradient correlation count, because random reassignment generates hundreds of total migrations and roughly half correlate with the gradient by chance.

Experiment J attempted a fix: measure the ratio of gradient-correlated migrations to total migrations. Expected structured ratio ~0.85–0.95, expected null ratio ~0.50. What actually happened: both models produced ratios around 0.35, both well below any reasonable threshold.

The reason was a physics-level error. Anchors are detected at field local maxima where gradient magnitude is below a detection threshold. Anchors form, by construction, at positions where the gradient is near zero. Measuring gradient direction at anchor positions is measuring noise in a flat field. The metric was ill-defined at the measurement site, not just miscalibrated.

The lesson from J was categorical: stop trying to measure gradient alignment. Measure something that doesn't depend on gradient magnitude at anchor positions.

Experiment K established **SYS_MIGRATION_RATE** as the correct discriminator: migrations per anchor per update in the second half of the run.

<details>
<summary><b>SYS_MIGRATION_RATE</b> — drift rate as structural discriminator</summary>

Migration rate measures how often an anchor changes cluster membership under ongoing interaction.
Null mechanics reassign anchors every 8 ticks by random selection — producing a high, stable migration rate by construction.
Structured mechanics allow membership change only when spatial relationships genuinely shift — a much rarer event.
Useful identity-like dynamics sit between frozen rigidity and chaotic movement. Persistence alone is insufficient; migration rate is what separates structured from random reorganization.

</details>

K produced: 42/125 structured passed, 0/125 null passed, with a 14× migration rate gap (0.033 vs 0.472). The null model produced zero passes across the full parameter space. The three conditions now discriminated cleanly.

More importantly, the three conditions mapped to the primitive triad. C1' measured spatial stability — Constraint operating. C2' measured topology persistence — Differentiation maintaining coherence. C3''' (SYS_MIGRATION_RATE) measured reorganization resistance — Influence operating through accumulated event history rather than single events.

---

## III. The Minimal Mechanism (L, M)

Experiment L asked what parameter range the phenomenon required. The sweep extended from CF=0.40 to CF=0.99 and IS=0.10 to IS=3.00.

The pre-registered predictions were wrong in a consistent direction: the phenomenon was more robust than expected. High CF (0.99) was predicted to saturate and collapse spatial differentiation. It didn't — slow decay produces more stable topology, not less, because anchors have more time to find field-stable positions before the field reshapes. Low CF (0.40) was predicted to collapse because aggressive decay would prevent anchor persistence. Many cells still passed. High IS was predicted to oversaturate gradient structure. It didn't — stronger events produce stronger gradient signals.

The only failure boundary found: IS below ~0.2, where events don't generate enough field energy to reach the anchor detection threshold. Below this, no anchors form. Above it, the phenomenon is essentially floor-insensitive across the tested range.

Experiment M removed one mechanism at a time to find which were load-bearing. The results:

Detection (replaced with random placement): passes improved from 88 to 91. Detection is redundant — gradient drift positions anchors near field peaks regardless of where they start, so initial placement method doesn't matter.

Drift (replaced with random walk): passes fell from 88 to 19. Drift is load-bearing. Without it, anchors drift from field-stable positions and topology degrades.

Clustering (replaced with random assignment): passes fell from 88 to 0. Clustering is absolutely load-bearing. Random assignment destroys spatial coherence entirely — exactly the null model's behavior.

The minimal mechanism from M: any detection + gradient drift + spatial clustering. Detection method irrelevant.

---

## IV. Adversarial Pressure (N, O1)

Experiment M left an implicit assumption: gradient drift meant gradient descent specifically. Experiment N tested this and three other structural assumptions with adversarial inversions.

Inverted drift — anchors climb the gradient instead of descending: 33/45 passes, identical to full_structured at 33/45. Gradient direction is not load-bearing.

Anti-clustering — anchors assigned to maximize spatial separation: 0/45 passes. Spatial proximity grouping is irreducibly necessary.

Temporal scramble — anchor update order randomized: 37/45 passes, marginal improvement over full_structured. Update order is not load-bearing.

Noise injection at 200% amplitude — noise standard deviation twice the gradient magnitude: 40/45 passes. No degradation at any noise level tested.

The noise result carries a specific structural meaning. At any individual tick, drift direction under 200% noise is dominated by the noise component. Over 312 update cycles, the systematic field-responsive component accumulates while noise averages toward zero. The long-run spatial organization is driven by the systematic component regardless of per-tick noise amplitude. This is the simulation's analog of the framework's claim that Influence operates through accumulated event history, not through single clean events.

The claim revision from N: not "gradient drift + spatial clustering" but "field-responsive movement in any form + spatial clustering." Direction, noise, and update order are implementation details. The irreducible conditions are field-responsiveness (any) and proximity grouping.

One question remained open after N: does random walk combined with spatial clustering — zero field response — also pass? If yes, clustering alone would be sufficient.

Experiment O1 answered this with three modes: full_structured (33/45 reference), field_walk_cluster (random detection + gradient drift, 30/45), random_walk_cluster (random detection + random walk + spatial clustering, 3/45). Decision threshold was 15/45.

3/45 is well below the threshold. The 3 survivors are stochastic boundary cases — they don't produce stable topology persistence signatures (C2'), and their migration rates remain elevated above the C3''' threshold. Field-responsiveness is an irreducible second condition.

A critic could note that random_walk_cluster retains scalar field coupling through anchor strength dynamics. The result addresses this: positional coupling — not scalar coupling — is the load-bearing factor. The strength update rule is identical across conditions. What differs is whether anchor position responds to field structure. When it doesn't, the phenomenon fails.

The minimal mechanism in final form: field-coupled anchor dynamics + spatial clustering. Two irreducible conditions, both confirmed by elimination across three experiments.

---

## V. Crossing Substrates (O2a, O2b, O2c)

The evidence through O1 came entirely from one physical substrate: a continuous 2D field with Gaussian propagation and Euclidean distance clustering. A skeptic could correctly observe this. The cross-substrate experiments tested whether the mechanism or just the implementation was real.

Experiment O2a attempted replication in an Erdős–Rényi random graph: N=200 nodes, activation spreading along edges, anchors as local activation maxima in the graph, drift as hop-to-highest-neighbor, clustering as connected components within 2 hops. The initial conditions metrics were: C1'' as mean medoid hop distance, C2'' as Jaccard membership similarity, C3'' as migration rate.

The result was 0/125 for both structured and random modes — but the failure was diagnostic, not terminal.

C3'' produced identical migration rates for structured and random drift: 0.0076 for both, both well below threshold. In the continuous field, C3''' discriminated structured from random by 14×. In the sparse random graph, the discrimination collapsed to zero.

The mechanism: in a sparse random graph with ~16 neighbors per node, even random hop movement is constrained to adjacent nodes. Anchors cannot drift far per update regardless of whether drift is field-responsive or random. Graph topology was providing positional constraint natively — making explicit field-responsiveness invisible.

C2'' (Jaccard) was the wrong metric. Jaccard measures whether exactly the same nodes are in the same clusters across consecutive steps. In hop-distance clustering, a single-hop drift by one anchor can cascade into complete cluster reassignment. The field model's Laplacian comparison measured structural topology similarity, not membership identity. These are different questions.

Experiment O2b corrected both: C2'' became medoid stability (fraction of steps where cluster centers are unchanged), and C1'' became inclusive at ≥3 hops. It also added the complete graph control, intended to remove topology-provided constraint by connecting all 200 nodes.

The complete graph control failed by design: HOP_CLUSTER_RADIUS=2 in K₂₀₀ means every node is within 2 hops of every other. All anchors collapsed into a single cluster permanently. The control was uninformative.

But the sparse graph results with corrected metrics revealed real discrimination: structured drift produced C1 passes at 90/125 (random: 8/125) and medoid stability of 0.544 (random: 0.049) — an 11× gap on both separation and structural stability.

The complete graph is not "high density." It is **SYS_FIELD_LOCALITY** deletion.

<details>
<summary><b>SYS_FIELD_LOCALITY</b> — substrate locality as prerequisite for proximity grouping</summary>

Locality means that some positions in the substrate are meaningfully closer to some other positions than to others.
Proximity-based grouping (clustering) requires locality to produce distinct regions.
A complete graph eliminates locality entirely — every node is within the same hop count of every other — making proximity-based grouping undefined.
Locality is a substrate condition, not a mechanism condition: the clustering mechanism is sound, but the substrate must support it.

</details>

Proximity-based grouping requires that some nodes be meaningfully closer to some other nodes. A complete graph eliminates locality entirely and makes proximity-based grouping undefined.

Experiment O2c swept densities — p=0.08, 0.20, 0.40, 0.70 — to find where locality degrades enough that the mechanism fails. The result had two parts.

The C2 stability discrimination held at approximately 10× across all densities:

| Density | Structured stability | Random stability | Ratio |
|---|---|---|---|
| p=0.08 | 0.544 | 0.049 | 11× |
| p=0.20 | 0.452 | 0.045 | 10× |
| p=0.40 | 0.458 | 0.040 | 11× |
| p=0.70 | 0.491 | 0.042 | 12× |

Structured drift produces consistently more stable topology than random walk at every density. The mechanism persists.

The C1 separation failed at p=0.20, because denser graphs have shorter average path lengths and cannot maintain ≥2 hop separation between cluster centers. The spatial separation condition — distinct regions — requires locality in the substrate. Without it, all clusters are adjacent and "separated" becomes meaningless.

The cross-substrate arc produced a mechanism revision establishing **SYS_CROSS_SUBSTRATE_GENERALIZATION**. The minimal mechanism is not specifically "field-responsive motion + clustering." It is:

<details>
<summary><b>SYS_CROSS_SUBSTRATE_GENERALIZATION</b> — mechanism transfer across physical substrates</summary>

The core mechanism (persistent positional constraint + proximity-based grouping + substrate locality) is substrate-agnostic.
Positional constraint can come from gradient drift (continuous field), graph adjacency (sparse graph), or activation coupling (denser graphs).
Proximity grouping is irreducible across all substrates tested.
Substrate locality is a prerequisite — not a mechanism property — required for grouping to produce distinct regions.
Discrimination held at 10–12× on structural stability across all tested graph densities (p=0.08 to p=0.70).

</details>

> **Persistent positional constraint + proximity-based grouping + substrate locality**

Positional constraint can come from gradient drift (continuous field), graph adjacency (sparse graph), or activation coupling (denser graphs — to be tested). Proximity grouping is irreducible. Substrate locality is a prerequisite for grouping to produce distinct regions. The three conditions correspond directly to the primitive triad: Influence propagates activation through the substrate, Constraint limits positional movement (intrinsically or dynamically), Differentiation requires a substrate that can register distinct positions.

---

## VI. Framework Contact (P, Q)

Experiment P was the first to test a framework claim rather than establish structural conditions. Three claims about identity reconstruction were tested against simulation data.

Claim 1: reconstruction from field traces. Removing all anchors while keeping the field intact — anchors reform, topology reconstructs. Supported: all 10 seeds reconstructed, topology similarity 0.557 in late recovery. The reconstruction is real.

Claim 2: field traces accelerate reconstruction compared to complete reset. Not supported — and the reason matters. Anchor pruning (field intact, anchors removed) and full reset (field and anchors zeroed) produced identical results: 0.557 topology similarity, 200-tick first recovery, same migration rates.

What Experiment P established was **SYS_RECONSTRUCTION_WITHOUT_MEMORY**: reconstruction belongs to the anchoring layer, not the identity layer.

<details>
<summary><b>SYS_RECONSTRUCTION_WITHOUT_MEMORY</b> — identity reconstructs from field topology, not stored state</summary>

The framework separates identity (distributed topology) from memory (substrate retention of past states).
When anchors are removed but the field remains intact, anchors reform and topology reconstructs — without any stored record of prior configuration.
Reconstruction belongs to the anchoring mechanism, not to identity-as-topology.
Identity can persist without influencing future instantiation. Memory and anchoring mechanisms carry reconstruction responsibility.
This confirms the separation the framework claims, not a contradiction of it.

</details>

Identity can persist without influencing future instantiation. P confirmed the separation the framework claims, not a contradiction of it.

Claim 3: reconstruction path visible as transient migration elevation. Inverted — migration rate rose late, not early, because reconstruction requires anchors to first form and then reorganize. The metric tracked population dynamics rather than reconstruction sequence.

With the framework's separation clarified, a harder question became available: can history be made to matter without crossing into explicit storage?

Experiment Q introduced a memory field — a slow reinforcement layer running alongside the normal field. Stable anchors leave a weak Gaussian residue that decays at 0.9995 per tick, compared to the normal field's 0.85 decay. This residue contributes 15% to the combined field that anchors respond to. Critically, this is not storage. It records no labels, no cluster assignments, no topology. It only makes regions where stable interaction has occurred slightly more energetically favorable.

The test: three phases. Phase A (1000 ticks) establishes neutral topology. Phase B (1000 ticks) injects biased events concentrated in the right portion of the field, pushing the system toward topology B. Phase C (1000 ticks) restores neutral events and observes whether the system returns to A or carries forward something of B.

Two conditions: with_memory (memory field active throughout) and without_memory (standard simulation).

The result:

```
                    sim(A,C)   sim(B,C)   sep A→B→C
with_memory          0.748      0.720      0.43→0.64→0.42
without_memory       0.748      0.647      0.43→0.62→0.42
```

Both conditions recover spatially. The separation fraction returns to 0.42 in Phase C. Mean anchor x-position returns from ~95 (rightward) to ~75 (original) in both modes. The spatial layer is fully reversible.

The topological layer is not equally reversible. Without memory: sim(B,C) = 0.647. With memory: sim(B,C) = 0.720. The memory field makes Phase C topology 11% more similar to Phase B — a gap of 0.072 across 5 seeds.

The system returns to where it is spatially. It does not return to what it is structurally.

Position converges. Topology retains bias.

This is **SYS_HYSTERESIS**.

<details>
<summary><b>SYS_HYSTERESIS</b> — path-dependent structural bias without storage</summary>

Hysteresis: the system's structural state at time C depends on the path through B, not just on current field conditions.
The spatial layer is fully reversible — position converges to prior configuration.
The topological layer is not equally reversible — topology retains a bias toward prior configurations.
Position converges. Topology retains path.
This is not memory (no labels, no stored topology) and not deterministic recall (the system recovers, it doesn't replay).
It is a structural lean: interaction history tilts the topology without determining it.

</details>

The hysteresis score gap of 0.072 is not noise — it is Δstructure ≠ 0 under identical final conditions (identical physics, identical Phase C event distribution). The structural state at the end of Phase C depends on the path through Phase B, not just on the current field.

The precise formulation: the system exhibits path-dependent structural bias. Interaction history tilts the topology without determining it. Not full persistence. Not deterministic recall. A tilt. The with_memory system does not stay in Phase B's configuration — it recovers toward A while carrying a structural lean toward B.

What the memory field actually did: accumulated interaction weighting without storage. It required no labels, no clusters, no recorded topology — only that stable interaction leaves an energetic residue that integrates slowly over time. The mechanism:

> stable anchor → slight field bias accumulates → influences where new anchors form → reinforces the bias

A positive feedback with very weak coupling (0.002 reinforcement per step, 0.15 field weight). Over 3000 ticks, measurable but not dominant.

---

## VII. Structural Relevance (R)

Experiment R asked whether relevance can be generated structurally before semantics enter. The answer is yes — and the mechanism is simpler than expected.

Three Gaussian pillars were embedded at fixed positions in the substrate. They maintain constant energy that does not decay. No labels, no attraction mechanism, no semantic assignment. The normal interaction field still runs around them; they simply make certain regions persistently more energized.

The result: anchors within 20 units of a pillar are stable at 97.9%. Anchors beyond 40 units sit at 18% — identical to the control condition with no fixed structures. The gradient is steep, systematic, and drops to background level at exactly the distance where pillar influence fades.

Stable anchors averaged 16.4 units from their nearest pillar. All anchors averaged 27.5 units. The 11.1-unit proximity gap is the fingerprint of structural selection: the system progressively concentrated toward pillar-proximate positions through differential survival, without any mechanism that explicitly favors them.

The memory field amplification is the compounding effect: the structured condition accumulated 3.3× more memory energy than the uniform control. Stable anchors reinforce the memory field. Near-pillar anchors are disproportionately stable. The memory field therefore organizes itself around the fixed structures — a second-order structural effect.

The system does not know pillars matter. Pillars matter because they alter the stability landscape. The system selects them by surviving there.

This is **SYS_PROTO_VALUATION** without semantics: structural position determines load-bearingness.

<details>
<summary><b>SYS_PROTO_VALUATION</b> — structural relevance before semantic assignment</summary>

Proto-valuation: some positions in the substrate support stable anchor occupation better than others, and the system organizes around those positions through differential survival — not through any evaluation mechanism.
Fixed substrate features (pillars) alter the stability landscape. Anchors near them are disproportionately stable (97.9% vs 18% background).
The system does not know the fixed features matter. They matter because they change the survival probability of anchors nearby.
This is not preference, not meaning, not concern — only structural fact operating through differential survival.
Proto-valuation is the precursor condition to semantic relevance; it does not require semantic assignment to operate.

</details>

Not preference, not meaning, not concern — only the structural fact that some positions support stable anchor occupation better than others, and that the system, through differential survival, organizes around those positions.

---

## What the Series Establishes

Across fifteen experiments (G through R), the series establishes this hierarchy:

**Level 0 — Pattern formation** (G, H): structured field mechanics produce spontaneous multi-basin topology from random initialization. Original conditions were partially trivial; genuine discrimination required tightened conditions.

**Level 1 — Discriminator** (I, J, K): three attempts to isolate the mechanism through measurable conditions. The correct observable — migration rate — was found after two failed approaches diagnosed their own errors. Three conditions map to the primitive triad: Constraint (spatial stability), Differentiation (topology persistence), Influence (reorganization resistance).

**Level 2 — Minimal mechanism** (L, M, N, O1): boundaries mapped (IS > ~0.2), mechanism isolated by elimination (detection redundant, drift and clustering load-bearing), adversarial pressure applied (direction, noise, and update order not load-bearing, proximity grouping irreducible, field-responsiveness confirmed necessary by isolation).

**Level 3 — Substrate generalization** (O2a, O2b, O2c): mechanism transfers to sparse graph dynamics with 10–12× discrimination on structural stability across all tested densities. Locality identified as a substrate condition — not a mechanism condition — required for proximity grouping to produce distinct regions. Mechanism revised: persistent positional constraint + proximity grouping + substrate locality.

**Level 4 — Identity ≠ memory** (P): reconstruction belongs to anchoring mechanisms, not identity-as-topology. The same basin structure reforms from any starting state. Identity is structure, not storage.

**Level 5 — Path-dependent structural bias** (Q): when accumulated interaction weighting is present, topology carries forward where the system has been without encoding what was there. Spatial recovery is complete; topological recovery is partial. Structure carries its path without storing it.

**Level 6 — Proto-valuation** (R): fixed environmental structures create differential structural relevance without semantic assignment. Anchors near fixed substrate features are 5.4× more stable than background anchors (97.9% vs 18%), accumulate 3.3× more memory reinforcement, and are selected by differential survival — not by any evaluation mechanism. Structural position determines load-bearingness. The system does not know the fixed features matter. They matter because they alter the stability landscape.

---

## A Further Limit: Irreducibility Not Yet Established

The framework maintains a functional separation between lower-level differentiation processes (proto-qualia, detection-level activity) and higher-order identity-like organization (topology, clustering, hysteresis). This separation is operationally supported by the simulation results, which demonstrate that:

- detection-level processes can exist without producing persistent structure,
- identity-like topology requires additional conditions — field-responsive coupling, spatial grouping, stability,
- intermediate constructs (memory bias, hysteresis, structural valuation) can be introduced without collapsing these layers.

However, this separation has not yet been proven irreducible.

The dependency relation the series demonstrates:

```
proto-qualia → anchoring → topology → identity
```

has been shown as *constructible* — each layer builds on the previous, and the simulation instantiates the chain step by step. What has not been shown is that this chain is *strictly non-collapsible* — that the layers represent genuinely distinct structural levels rather than different descriptions of a single underlying process.

Two open questions follow precisely from this:

First, can proto-qualia exist independently of any form of structural participation? The simulation shows that detection-level processes (anchor formation at field minima) do not automatically produce persistent topology — additional conditions are required. But it does not test whether detection-level activity is possible in a substrate that provides no scaffolding for structural organization at all.

Second, can identity-like organization arise without an underlying differentiation layer? The minimality tests (M) show that clustering is absolutely load-bearing and detection is redundant — but this is a finding about the mechanism, not about whether topology can emerge from something other than a differentiation process.

These are testable questions, not philosophical assumptions. The test for the first: construct a detection-level process that demonstrably operates without any structural participation and verify that no topology forms. The test for the second: construct topology through a mechanism that does not involve differentiation at any level and verify that the result satisfies the identity-like conditions established in G through R.

Until those tests are run, the layered construction is demonstrated, not proven irreducible.

> The current results support a layered construction of identity-like behavior. Whether these layers represent genuinely distinct structural levels or different descriptions of a single underlying process remains a testable question rather than a settled assumption.

---

## What the Series Does Not Establish

The simulation operates at this level: anchors → positions → clustering → topology. This maps to: features → spatial relations → grouping → structure. That is structural abstraction, not lived identity.

Three gaps separate the simulation from identity in any real system:

**Anchors are not real signals.** In the simulation, an anchor is a local field maximum. In real identity systems, anchors would need to be behaviorally relevant — perceptual features, decisions, learned associations, sensorimotor loops. The simulation has no semantic or functional relevance.

**There is no action loop.** The simulation runs field → anchors move. Real identity systems run perception → action → feedback → update. Without a closed loop, the system cannot choose, adapt intentionally, or actively bias future interaction. The memory field adds accumulated weighting but not agency.

**There is no selective valuation.** The memory field adds weighting based on stability. Real identity requires valuation — this matters more than that. Stabilization and significance are different conditions.

The correct framing:

> This work does not model identity directly. It isolates the minimal dynamical conditions under which identity-like structural persistence and path-dependent bias can arise. Mapping these conditions to real identity systems requires additional layers: perception, action, and valuation.

What the work establishes is identity without semantics, without memory, without agency — the stripped-down structural core that any richer model of identity would need to instantiate. That is why the mechanism is isolable. Real identity systems are not stripped down. The simulation is. And what survives stripping is what the series is actually about.

---

*2026*
