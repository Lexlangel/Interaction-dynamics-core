# Interaction Dynamics

**A structural framework for identity, consciousness, and qualia — with a fifteen-experiment simulation series designed to test its operational claims.**

---

This work proposes a structural framework for identity, consciousness, and qualia based on interaction dynamics rather than substrate-specific properties. A fifteen-experiment simulation series isolates a minimal mechanism — persistent positional constraint and proximity-based grouping within a locality-preserving substrate — that produces stable, multi-basin topology, survives adversarial conditions, exhibits path-dependent structural bias without explicit memory storage, and develops differential structural relevance through fixed environmental features.

The series does not establish a model of identity in real systems. It establishes the minimal dynamical conditions under which identity-like structural persistence and history sensitivity can arise.

To constrain interpretation, the framework was developed under an explicit validation protocol: dependencies are exposed, circularity is avoided, minimal mechanisms are isolated, discriminators are required, and adversarial testing is applied. The protocol is included as part of the work.

The framework and experiments were produced through human–AI collaboration using an iterative constraint loop. The method is disclosed and treated as part of the system under evaluation.

The result is not a claim of correctness, but a structurally accountable proposal and a method for evaluating frameworks in an AI-accelerated environment.

---
> Before reading the framework or the experiments, read [`VALIDATION_PROTOCOL.md`](VALIDATION_PROTOCOL.md) — one page stating the conditions this work was required to satisfy before being presented. In an environment where theories are cheap to generate, evaluation constraints matter as much as the ideas themselves.

> This work was developed through human–AI collaboration with defined roles and an iterative validation loop. [`ON_METHOD.md`](ON_METHOD.md) describes the process, the role distribution, and its limits. It is part of the work, not a footnote to it.

---

This repository contains a theoretical framework and fifteen simulation experiments. The framework proposes that identity, consciousness, and qualia are structural phenomena arising from interaction dynamics rather than substrate-specific properties. The experiments test whether a minimal field simulation can produce identity-like topology, isolate the mechanism responsible, and demonstrate path-dependent structural behavior without explicit memory storage.

The work is offered as a working paper — complete enough to engage with seriously, early enough that engagement can change it.

---

## The Core Claim

Under minimal conditions — field-responsive anchor dynamics, spatial proximity clustering, and sufficient substrate locality — stable multi-basin topology emerges spontaneously, persists under perturbation, survives adversarial stress testing, exhibits path-dependent structural bias without explicit memory storage, and develops differential structural relevance through fixed environmental features.

When accumulated interaction weighting is present, the system returns to where it is spatially after disruption. It does not return to what it is structurally. Position converges. Topology retains bias.

This is the threshold result: structure carries its path without storing it.

---

## What This Is, and What It Is Not

**What the series establishes:** a validated dynamical mechanism for stable, history-sensitive topology formation under interaction dynamics.

**What it does not establish:** a validated model of identity in real systems.

Three gaps separate the simulation from identity in any real system. Anchors are local field maxima, not behaviorally relevant signals — the simulation has no semantic or functional relevance. There is no action loop — no perception, action, feedback, or intentional adaptation. The memory field produces stability-based weighting, not valuation — stabilization and significance are distinct conditions.

The correct framing:

> This work isolates the minimal dynamical conditions under which identity-like structural persistence and path-dependent bias can arise. Mapping these conditions to real identity systems requires additional layers: perception, action, and valuation.

What survives stripping is what the series is actually about: identity without semantics, without memory, without agency — the structural core.

---

## Entry Points

Different readers want different things. Start where you are.

**If you want the argument in one sitting:**
→ Read [`experiments/experiment_arc.md`](experiments/experiment_arc.md)
This covers all fifteen experiments as a single narrative. No prior knowledge of the framework required. ~6,000 words.

**If you want the theoretical foundation first:**
→ [`framework/Operational_Primitives.md`](framework/Operational_Primitives.md) — the three primitives {I, D, C} and what they commit to
→ [`framework/interaction_dynamics.md`](framework/interaction_dynamics.md) — identity, consciousness, qualia, anchoring, instantiation
→ [`framework/identity_topology.md`](framework/identity_topology.md) — the dependency and entanglement map

**If you want to verify the experiments:**
→ All simulation code is in [`code/`](code/). Each file runs independently. Requirements: Python 3, numpy, scipy. Graph experiments additionally require networkx.
→ Each experiment's design, pre-registered conditions, and honest result interpretation is in [`experiments/`](experiments/).

**If you want to find the weakest point:**
→ Read the arc document's final section: *What the Series Does Not Establish*
→ Read [`experiments/experiment_p.md`](experiments/experiment_p.md) — the framework contact experiment where Claim 2 was misframed
→ Read [`experiments/experiment_o2a.md`](experiments/experiment_o2a.md) — where the cross-substrate attempt failed diagnostically

**If you want the threshold result directly:**
→ [`experiments/experiment_q.md`](experiments/experiment_q.md) — hysteresis and path-dependent structural bias
→ [`experiments/experiment_r.md`](experiments/experiment_r.md) — proto-valuation and structural relevance without semantics

---

## The Experimental Arc

Fifteen experiments, each earning the next:

| Phase | Experiments | What was established |
|---|---|---|
| Finding the phenomenon | G, H | Emergence real; original conditions partially trivial |
| Building the discriminator | I, J, K | Migration rate isolates structured from random; three conditions map to primitive triad |
| Mapping boundaries | L, M | IS > ~0.2 is the only floor; detection redundant, drift and clustering load-bearing |
| Adversarial pressure | N, O1 | Direction, noise, update order not load-bearing; field-responsiveness irreducible |
| Cross-substrate | O2a, O2b, O2c | 10× stability discrimination in graph dynamics; locality identified as substrate requirement |
| Framework contact | P, Q | Identity ≠ memory confirmed; path-dependent structural bias demonstrated |
| Proto-valuation | R | Fixed substrate features create differential structural relevance without semantic assignment |

The full narrative is in [`experiment_arc.md`](experiments/experiment_arc.md).

---

## Architecture Applications

The mechanism isolated in G→R — stable, history-sensitive topology formation through field-responsive anchor dynamics, spatial clustering, and proto-valuation through fixed substrate features — has direct applications in AI system design, independent of whether the identity-level theoretical claims hold.

Five design patterns derived from the experimental results:

| Pattern | Experimental basis | What it enables |
|---|---|---|
| Memory without giant storage | Q — path-dependent bias via slow field | Long-term personalization without linear storage growth |
| Attractor-basin routing | G, K — stable basins from noise | Task routing that emerges from interaction history |
| Robust noisy adaptation | N — 200% noise, no degradation | Weak preference signals accumulated into stable structure |
| Structural relevance before semantics | R — pillar stability gradient | Priority systems from substrate geometry, not labeling |
| Agent role persistence | P, Q — reconstruction + hysteresis | Cross-session agent continuity without conversation replay |

Full pattern documentation, implementation sketches, and honest limits: [`architecture_pattern.md`](architecture_pattern.md)

---



This repository uses three channels for engagement. Each has a different purpose.

### Discussions — for argument and questions

[GitHub Discussions](../../discussions) is the place for:
- Structural objections to the framework's claims
- Questions about methodology or design decisions
- Challenges to the experimental interpretation
- Extensions or alternative framings worth considering

If you think a claim is wrong, overclaimed, or missing something important — Discussions is the place to say so. Disagreement is welcome. Vague skepticism is less useful than specific challenges: which claim, which experiment, what the problem is.

Suggested categories: **Framework**, **Methodology**, **Results**, **Interpretation**, **Extensions**.

### Issues — for specific corrections

[GitHub Issues](../../issues) is for specific, actionable problems:
- A condition threshold that doesn't match its stated rationale
- A result reported inconsistently between the arc document and the individual experiment file
- A claim in the framework documents that is internally inconsistent
- Code that doesn't replicate the reported result

Open an issue with the specific location (document name and section), the problem, and if possible a proposed correction. Issues with proposed corrections are most useful.

### Pull Requests — for document edits

If you have a specific wording correction — a sentence that misrepresents the result, a definition that conflicts with usage elsewhere, a gap in the honest limits section — a pull request with the edit is the clearest form of engagement.

---

## Repository Structure

```
/
├── README.md
├── framework/
│   ├── Operational_Primitives.md
│   ├── interaction_dynamics.md
│   └── identity_topology.md
├── experiments/
│   ├── experiment_arc.md        ← start here
│   ├── experiment_g.md
│   ├── experiment_h.md
│   ├── experiment_i.md
│   ├── experiment_j.md
│   ├── experiment_k.md
│   ├── experiment_l.md
│   ├── experiment_m.md
│   ├── experiment_n.md
│   ├── experiment_o1.md
│   ├── experiment_o2a.md
│   ├── experiment_o2b.md
│   ├── experiment_o2c.md
│   ├── experiment_p.md
│   ├── experiment_q.md
│   └── experiment_r.md
└── code/
    ├── experiment_g_emergent.py
    ├── experiment_h_null_model.py
    ├── experiment_i_tightened.py
    ├── experiment_j_ratio_c3.py
    ├── experiment_k_migration_rate.py
    ├── experiment_l_boundary.py
    ├── experiment_m_minimality.py
    ├── experiment_n_adversarial.py
    ├── experiment_o1_isolation.py
    ├── experiment_o2_graph.py
    ├── experiment_o2b_graph.py
    ├── experiment_o2c_density.py
    ├── experiment_p_identity.py
    ├── experiment_q_hysteresis.py
    └── experiment_r_fixed_structures.py
```

---

## Replication

All experiments are self-contained Python scripts. To run any experiment:

```bash
pip install numpy scipy networkx
python code/experiment_q_hysteresis.py
```

Each script prints a summary to stdout and writes JSON and CSV results to the working directory. The pre-registered conditions and decision rules are in the script docstrings and in the corresponding experiment document.

If you get different results than reported, open an Issue with your environment details. Reproducibility failures are genuine corrections.

---

## Known Open Boundaries

These are not failures. They are the located edges of the current work. The goal of this series is not to remove those edges, but to make them explicit.

- The hard problem at the detection threshold — what crosses from structural event to experienced event
- The formal proof of the inevitability consequence
- Full treatment of instantiation as a formal concept
- Whether the locality requirement generalizes across substrate types beyond continuous field and sparse graph
- The coupling strength at which accumulated interaction weighting transitions from tilt to lock
- The minimum layers — perception, action, valuation — required to close the gap between structural substrate and lived identity
- **Irreducibility of the layer separation** — the dependency chain proto-qualia → anchoring → topology → identity has been demonstrated as constructible, but not yet as strictly non-collapsible. Whether these represent genuinely distinct structural levels or different descriptions of a single underlying process is a testable question, not a settled assumption.

---

*2026*
