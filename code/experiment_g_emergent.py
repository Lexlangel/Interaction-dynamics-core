"""
experiment_g_emergent.py
─────────────────────────────────────────────────────────────────────────────
Interaction Dynamics · Experiment G — Emergent Identity Field Test
2026

DESIGN PHILOSOPHY
─────────────────
No clusters are seeded. No parameters are chosen to produce a target outcome.
The field is initialized with uniform random noise. Interaction dynamics run
under a fixed physics. If distinct attractor basins form, separate, and persist
— they emerge. If they don't, the experiment reports that.

The result is the regime map across parameter space, not a single run.

WHAT IS BEING TESTED
─────────────────────
Framework claim: identity emerges as stable attractor topology from interaction
under constraint. Not planted, not seeded — produced by the dynamics.

Three conditions, defined before results:
  C1 — Spontaneous basin formation: do distinct attractor regions emerge
        from noise without seeding?
  C2 — Topological persistence: does each basin maintain internal similarity
        over time (threshold: 0.70)?
  C3 — Co-existence without merger: do multiple basins persist simultaneously
        rather than collapsing into one?

PARAMETER SWEEP
───────────────
Two free parameters varied across a grid:
  constraint_factor : [0.75, 0.80, 0.85, 0.90, 0.95]  (field decay per tick)
  influence_strength: [0.5, 0.7, 0.9, 1.1, 1.3]       (event magnitude)

All other parameters are physically motivated and held constant.
Seeds 0–4 run per cell. Regime classified per cell. Map exported.

OUTPUT
──────
  exp_g_regime_map.json   — full results per parameter cell
  exp_g_regime_map.csv    — regime classification grid (human-readable)
  exp_g_best_run.json     — detailed log of the run with strongest C1+C2+C3
"""

import math, random, json, csv, time
import numpy as np
from dataclasses import dataclass
from scipy.spatial.distance import cdist
from collections import defaultdict

# ─── Physics constants (fixed, not swept) ─────────────────────────────────────
# Motivated by continuous field theory: wave propagation, decay, edge effects.

GAUSSIAN_SIGMA      = 18.0    # spatial spread of each influence event
WAVE_SPEED          = 1.8     # propagation speed (field units / tick)
WAVE_DECAY          = 0.015   # amplitude decay with distance
WAVE_FIELD_DECAY    = 0.995   # global wave field decay per tick
ANCHOR_GRAD_THRESH  = 0.12    # gradient below which a local max is anchor-eligible
ANCHOR_MIN_STRENGTH = 0.15    # minimum field value to register as anchor
ANCHOR_COLLAPSE     = 0.05    # strength below which anchor is pruned
DRIFT_SPEED         = 0.18    # anchor drift toward local field minima
EDGE_REPEL          = 8       # edge exclusion zone (field units)
MAX_ANCHORS         = 32
STABILITY_THRESHOLD = 80      # ticks before anchor is 'stable'
CLUSTER_RADIUS      = 30.0    # spatial radius for connected-component clustering
TOPOLOGY_EDGE_DIST  = 55.0    # max distance for topology graph edge
EVENT_RATE          = 0.012   # background noise rate (events per tick)
FIELD_W, FIELD_H    = 160, 120
TICKS               = 2500    # run length per trial
LOG_INTERVAL        = 50


# ─── Field ────────────────────────────────────────────────────────────────────

class Field:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.data = np.zeros(w * h, dtype=np.float32)

    def _idx(self, x, y):
        return int(max(0, min(self.h-1, int(y)))) * self.w + int(max(0, min(self.w-1, int(x))))

    def __getitem__(self, pos):       return float(self.data[self._idx(*pos)])
    def decay(self, k):               self.data *= k
    def reset(self):                  self.data[:] = 0
    def add_field(self, other):       self.data += other.data
    def copy_from(self, other):       self.data = other.data.copy()
    def total_energy(self):           return float(np.sum(self.data))

    def gradient(self, x, y):
        xi = max(1, min(self.w-2, int(x)))
        yi = max(1, min(self.h-2, int(y)))
        gx = (self.data[yi*self.w+xi+1] - self.data[yi*self.w+xi-1]) * 0.5
        gy = (self.data[(yi+1)*self.w+xi] - self.data[(yi-1)*self.w+xi]) * 0.5
        return float(gx), float(gy)

    def gradient_magnitude(self, x, y):
        gx, gy = self.gradient(x, y)
        return math.sqrt(gx*gx + gy*gy)


def apply_gaussian(field, ex, ey, strength, sigma=GAUSSIAN_SIGMA):
    cx, cy = int(ex), int(ey)
    r = int(sigma * 3)
    ys = np.arange(max(0, cy-r), min(field.h, cy+r))
    xs = np.arange(max(0, cx-r), min(field.w, cx+r))
    if not len(xs) or not len(ys): return
    yy, xx = np.meshgrid(ys, xs, indexing="ij")
    vals = strength * np.exp(
        -((xx-cx)**2 + (yy-cy)**2).astype(np.float32) / (2*sigma**2))
    np.add.at(field.data, (yy*field.w+xx).ravel(), vals.ravel())


# ─── Anchor ───────────────────────────────────────────────────────────────────

@dataclass
class Anchor:
    x: float; y: float; strength: float
    age: int = 0
    cluster_id: int = -1
    drift_vx: float = 0.0
    drift_vy: float = 0.0

    @property
    def is_stable(self): return self.age >= STABILITY_THRESHOLD and self.strength > 0.1

    def distance_to(self, o):
        return math.sqrt((self.x-o.x)**2 + (self.y-o.y)**2)


# ─── Anchor detection ─────────────────────────────────────────────────────────

def detect_anchor_candidates(field, stride=6):
    candidates = []
    for j in range(stride, field.h-stride, stride):
        for i in range(stride, field.w-stride, stride):
            v = field[i, j]
            if v < ANCHOR_MIN_STRENGTH: continue
            if field.gradient_magnitude(i, j) >= ANCHOR_GRAD_THRESH: continue
            is_max = all(
                field[i+di, j+dj] <= v+0.01
                for di in range(-stride, stride+1, stride)
                for dj in range(-stride, stride+1, stride)
                if (di, dj) != (0, 0) and 0<=i+di<field.w and 0<=j+dj<field.h)
            if is_max:
                candidates.append({"x": float(i), "y": float(j), "strength": v})
    return candidates


# ─── Clustering ───────────────────────────────────────────────────────────────

def cluster_anchors(anchors, radius=CLUSTER_RADIUS):
    n = len(anchors)
    if not n: return []
    assignments = [-1] * n
    cid = 0
    for i in range(n):
        if assignments[i] != -1: continue
        assignments[i] = cid
        queue = [i]
        while queue:
            curr = queue.pop()
            for j in range(n):
                if assignments[j] != -1: continue
                if anchors[curr].distance_to(anchors[j]) <= radius:
                    assignments[j] = cid; queue.append(j)
        cid += 1
    for i, a in enumerate(anchors):
        a.cluster_id = assignments[i]
    centroids = []
    for c in range(cid):
        members = [anchors[i] for i in range(n) if assignments[i] == c]
        if not members: continue
        centroids.append({
            "id": c,
            "cx": round(sum(a.x for a in members)/len(members), 2),
            "cy": round(sum(a.y for a in members)/len(members), 2),
            "size": len(members),
            "stable": sum(1 for a in members if a.is_stable),
            "mean_strength": round(sum(a.strength for a in members)/len(members), 4),
        })
    return centroids


# ─── Topology signature ───────────────────────────────────────────────────────

def topology_signature(anchors, max_dist=TOPOLOGY_EDGE_DIST):
    n = len(anchors)
    if not n:
        return {"nodes": 0, "edges": 0, "density": 0.0, "components": 0,
                "laplacian_eigenvalues": [], "mean_strength": 0.0, "stable_count": 0}
    positions = np.array([[a.x, a.y] for a in anchors])
    dists = cdist(positions, positions)
    adj = ((dists < max_dist) & (dists > 0)).astype(float)
    weights = np.where(adj > 0, 1.0 - dists/max_dist, 0.0)
    edge_count = int(np.sum(adj)//2)
    max_edges = n*(n-1)/2
    density = edge_count/max_edges if max_edges > 0 else 0.0
    D = np.diag(np.sum(weights, axis=1)); L = D - weights
    try:
        lap_eigs = sorted([round(float(e), 6) for e in np.linalg.eigvalsh(L)])
    except:
        lap_eigs = []
    parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b): parent[find(a)] = find(b)
    for i in range(n):
        for j in range(i+1, n):
            if adj[i, j]: union(i, j)
    components = len(set(find(i) for i in range(n)))
    return {
        "nodes": n, "edges": edge_count,
        "density": round(density, 4), "components": components,
        "laplacian_eigenvalues": lap_eigs,
        "mean_strength": round(float(np.mean([a.strength for a in anchors])), 4),
        "stable_count": sum(1 for a in anchors if a.is_stable)
    }


def compare_topology(s1, s2):
    if s1["nodes"] == 0 and s2["nodes"] == 0: return 1.0
    if s1["nodes"] == 0 or s2["nodes"] == 0: return 0.0
    e1 = s1["laplacian_eigenvalues"]; e2 = s2["laplacian_eigenvalues"]
    ml = max(len(e1), len(e2))
    e1p = np.array(e1 + [0.0]*(ml-len(e1))); e2p = np.array(e2 + [0.0]*(ml-len(e2)))
    eig_score = math.exp(-float(np.linalg.norm(e1p-e2p)) * 0.15)
    c1, c2 = s1["components"], s2["components"]
    cluster_score = 1.0 - abs(c1-c2)/max(c1, c2, 1)
    density_score = 1.0 - abs(s1["density"]-s2["density"])
    node_score = min(s1["nodes"], s2["nodes"])/max(s1["nodes"], s2["nodes"])
    return round(0.50*eig_score + 0.20*cluster_score + 0.15*density_score + 0.15*node_score, 4)


# ─── Single trial ─────────────────────────────────────────────────────────────

def run_trial(constraint_factor, influence_strength, seed, ticks=TICKS, log_interval=LOG_INTERVAL):
    """
    One trial: random noise initialization, no seeding, fixed physics.
    Returns condition results and log.
    """
    random.seed(seed); np.random.seed(seed)

    gauss_field = Field(FIELD_W, FIELD_H)
    wave_field  = Field(FIELD_W, FIELD_H)
    combined    = Field(FIELD_W, FIELD_H)
    anchors = []
    waves = []
    log = []
    prev_cluster_sigs = {}
    migrations = []
    prev_assignments = {}

    for tick in range(1, ticks+1):
        # Background noise — purely random spatial events, no targeting
        if random.random() < EVENT_RATE:
            ex = EDGE_REPEL + random.random()*(FIELD_W - EDGE_REPEL*2)
            ey = EDGE_REPEL + random.random()*(FIELD_H - EDGE_REPEL*2)
            apply_gaussian(gauss_field, ex, ey, influence_strength)

        # Wave propagation
        wave_field.reset()
        live = []
        for w in waves:
            age = tick - w["born"]
            if age < 300:
                cx, cy = int(w["x"]), int(w["y"])
                r = WAVE_SPEED * age
                scan = int(r + WAVE_SPEED*10)
                ys = np.arange(max(0, cy-scan), min(FIELD_H, cy+scan))
                xs = np.arange(max(0, cx-scan), min(FIELD_W, cx+scan))
                if len(xs) and len(ys):
                    yy, xx = np.meshgrid(ys, xs, indexing="ij")
                    dist = np.sqrt(((xx-cx)**2 + (yy-cy)**2).astype(np.float32))
                    phase = dist - r
                    mask = np.abs(phase) < WAVE_SPEED*8
                    amp = np.where(mask,
                        0.3*np.cos(phase*0.25)*np.exp(-WAVE_DECAY*dist)*np.exp(-age*0.008), 0.0)
                    np.add.at(wave_field.data, (yy*FIELD_W+xx).ravel(), amp.ravel().astype(np.float32))
                live.append(w)
        waves = live

        gauss_field.decay(constraint_factor)
        wave_field.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss_field)
        combined.add_field(wave_field)

        # Anchor update every 8 ticks
        if tick % 8 == 0:
            candidates = detect_anchor_candidates(combined)
            for c in candidates:
                nearby = next(
                    (a for a in anchors if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2) < 18),
                    None)
                if nearby:
                    nearby.strength = nearby.strength*0.85 + c["strength"]*0.15
                    nearby.x = nearby.x*0.95 + c["x"]*0.05
                    nearby.y = nearby.y*0.95 + c["y"]*0.05
                elif len(anchors) < MAX_ANCHORS:
                    anchors.append(Anchor(c["x"], c["y"], c["strength"]))

            for a in anchors:
                gx, gy = combined.gradient(int(a.x), int(a.y))
                fx = -gx*DRIFT_SPEED*8; fy = -gy*DRIFT_SPEED*8
                if a.x < EDGE_REPEL:          fx += (EDGE_REPEL - a.x)*0.1
                if a.x > FIELD_W-EDGE_REPEL:  fx -= (a.x - (FIELD_W-EDGE_REPEL))*0.1
                if a.y < EDGE_REPEL:           fy += (EDGE_REPEL - a.y)*0.1
                if a.y > FIELD_H-EDGE_REPEL:  fy -= (a.y - (FIELD_H-EDGE_REPEL))*0.1
                a.drift_vx = fx; a.drift_vy = fy
                a.x = max(5, min(FIELD_W-5, a.x+fx))
                a.y = max(5, min(FIELD_H-5, a.y+fy))
                a.age += 1
                fv = combined[int(a.x), int(a.y)]
                a.strength = a.strength*0.98 + fv*0.02

            anchors = [a for a in anchors if a.strength > ANCHOR_COLLAPSE or a.age < 30]
            centroids = cluster_anchors(anchors)

            # Track migrations
            current_assignments = {id(a): a.cluster_id for a in anchors}
            for a in anchors:
                aid = id(a)
                prev = prev_assignments.get(aid, a.cluster_id)
                if prev != a.cluster_id and prev != -1:
                    migrations.append({"tick": tick, "from": prev, "to": a.cluster_id})
            prev_assignments = current_assignments

        # Logging
        if tick % log_interval == 0:
            centroids = cluster_anchors(anchors)
            n_clusters = len(centroids)
            cluster_distances = []
            within_sims = []

            if len(centroids) >= 2:
                for i in range(len(centroids)):
                    for j in range(i+1, len(centroids)):
                        ci, cj = centroids[i], centroids[j]
                        d = math.sqrt((ci["cx"]-cj["cx"])**2 + (ci["cy"]-cj["cy"])**2)
                        cluster_distances.append(round(d, 2))

            for c in centroids:
                members = [a for a in anchors if a.cluster_id == c["id"]]
                sig = topology_signature(members)
                key = f"c{c['id']}"
                prev_sig = prev_cluster_sigs.get(key)
                if prev_sig:
                    within_sims.append(compare_topology(prev_sig, sig))
                prev_cluster_sigs[key] = sig

            log.append({
                "tick": tick,
                "anchor_count": len(anchors),
                "stable_count": sum(1 for a in anchors if a.is_stable),
                "cluster_count": n_clusters,
                "mean_cluster_distance": round(sum(cluster_distances)/len(cluster_distances), 2)
                                         if cluster_distances else None,
                "distance_variance": round(float(np.std(cluster_distances)), 2)
                                     if len(cluster_distances) > 1 else None,
                "mean_within_similarity": round(sum(within_sims)/len(within_sims), 4)
                                          if within_sims else None,
                "field_energy": round(combined.total_energy(), 4),
                "migrations_total": len(migrations),
            })

    # ── Condition evaluation (second half of run only) ─────────────────────────
    half = len(log)//2
    late = log[half:]

    # C1 — Spontaneous basin formation: fraction of ticks with >= 2 clusters
    multi_ticks = sum(1 for e in late if e["cluster_count"] >= 2)
    separation_fraction = multi_ticks / len(late) if late else 0.0
    distances = [e["mean_cluster_distance"] for e in late if e["mean_cluster_distance"]]
    mean_dist = round(sum(distances)/len(distances), 2) if distances else None
    dist_var = round(float(np.std(distances)), 2) if len(distances) > 1 else None
    c1 = separation_fraction > 0.4  # deliberately conservative threshold

    # C2 — Topological persistence within basins
    sims = [e["mean_within_similarity"] for e in late if e["mean_within_similarity"]]
    mean_sim = round(sum(sims)/len(sims), 4) if sims else None
    c2 = mean_sim is not None and mean_sim > 0.70

    # C3 — Co-existence: C1 and C2 both held, migration present
    n_migrations = len(migrations)
    c3 = c1 and c2 and n_migrations > 0

    # Regime classification
    if c1 and c2 and dist_var is not None and dist_var < 6.0:
        regime = "stable_coexistence"
    elif c1 and c2 and dist_var is not None and dist_var >= 6.0:
        regime = "oscillatory_exchange"
    elif c1 and not c2:
        regime = "transient_separation"
    elif not c1 and c2:
        regime = "single_stable_basin"
    else:
        regime = "no_separation"

    return {
        "params": {
            "constraint_factor": constraint_factor,
            "influence_strength": influence_strength,
            "seed": seed,
        },
        "conditions": {
            "C1_spontaneous_formation": {"passed": c1, "separation_fraction": round(separation_fraction, 3),
                                          "mean_inter_cluster_distance": mean_dist, "distance_variance": dist_var},
            "C2_topological_persistence": {"passed": c2, "mean_within_similarity": mean_sim, "threshold": 0.70},
            "C3_coexistence_without_merger": {"passed": c3, "migration_events": n_migrations},
        },
        "regime": regime,
        "all_passed": c1 and c2 and c3,
        "log": log,
        "migrations": migrations,
    }


# ─── Parameter sweep ──────────────────────────────────────────────────────────

def run_sweep():
    constraint_factors  = [0.75, 0.80, 0.85, 0.90, 0.95]
    influence_strengths = [0.5,  0.7,  0.9,  1.1,  1.3]
    seeds               = [0, 1, 2, 3, 4]

    total = len(constraint_factors) * len(influence_strengths) * len(seeds)
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT G — Emergent Identity Field Test")
    print(f"  Parameter sweep: {total} trials")
    print(f"  Conditions defined prior to execution — no post-hoc tuning")
    print(f"{'='*60}\n")

    regime_map = []        # one entry per (cf, is) cell
    all_trials = []
    best_trial = None
    best_score = -1

    t0 = time.time()
    trial_n = 0

    for cf in constraint_factors:
        for ist in influence_strengths:
            cell_results = []
            for seed in seeds:
                trial_n += 1
                elapsed = time.time() - t0
                print(f"  [{trial_n:3d}/{total}] cf={cf}  is={ist}  seed={seed}  "
                      f"elapsed={elapsed:.0f}s", end="\r", flush=True)

                result = run_trial(cf, ist, seed)
                cell_results.append(result)
                all_trials.append(result)

                # Track best (C1+C2+C3 score)
                score = (result["conditions"]["C1_spontaneous_formation"]["separation_fraction"] +
                         (result["conditions"]["C2_topological_persistence"]["mean_within_similarity"] or 0) +
                         (1.0 if result["conditions"]["C3_coexistence_without_merger"]["passed"] else 0))
                if score > best_score:
                    best_score = score
                    best_trial = result

            # Aggregate cell
            regimes = [r["regime"] for r in cell_results]
            regime_counts = defaultdict(int)
            for r in regimes: regime_counts[r] += 1
            dominant_regime = max(regime_counts, key=regime_counts.get)
            all_passed_count = sum(1 for r in cell_results if r["all_passed"])
            mean_sep = round(np.mean([
                r["conditions"]["C1_spontaneous_formation"]["separation_fraction"]
                for r in cell_results]), 3)
            sims = [r["conditions"]["C2_topological_persistence"]["mean_within_similarity"]
                    for r in cell_results
                    if r["conditions"]["C2_topological_persistence"]["mean_within_similarity"]]
            mean_topo = round(np.mean(sims), 4) if sims else None

            regime_map.append({
                "constraint_factor": cf,
                "influence_strength": ist,
                "dominant_regime": dominant_regime,
                "regime_counts": dict(regime_counts),
                "all_conditions_passed": all_passed_count,
                "trials": len(seeds),
                "mean_separation_fraction": mean_sep,
                "mean_topology_similarity": mean_topo,
            })

    print(f"\n\n  Sweep complete. {total} trials in {time.time()-t0:.1f}s")

    # ── Save regime map ────────────────────────────────────────────────────────
    with open("exp_g_regime_map.json", "w") as f:
        json.dump({
            "experiment": "G_emergent_identity",
            "design": "no_seeding_no_tuning",
            "conditions_defined_prior_to_execution": True,
            "fixed_physics": {
                "gaussian_sigma": GAUSSIAN_SIGMA, "wave_speed": WAVE_SPEED,
                "wave_decay": WAVE_DECAY, "anchor_grad_thresh": ANCHOR_GRAD_THRESH,
                "anchor_min_strength": ANCHOR_MIN_STRENGTH, "drift_speed": DRIFT_SPEED,
                "ticks": TICKS, "field_w": FIELD_W, "field_h": FIELD_H,
                "event_rate": EVENT_RATE, "stability_threshold": STABILITY_THRESHOLD,
            },
            "swept_parameters": {
                "constraint_factors": constraint_factors,
                "influence_strengths": influence_strengths,
                "seeds_per_cell": seeds,
            },
            "regime_map": regime_map,
        }, f, indent=2)
    print("  JSON → exp_g_regime_map.json")

    # ── Save CSV regime grid ───────────────────────────────────────────────────
    with open("exp_g_regime_map.csv", "w", newline="") as f:
        w = csv.writer(f)
        # Header row
        w.writerow([""] + [f"is={ist}" for ist in influence_strengths])
        # Grid
        for cf in constraint_factors:
            row = [f"cf={cf}"]
            for ist in influence_strengths:
                cell = next(c for c in regime_map
                            if c["constraint_factor"]==cf and c["influence_strength"]==ist)
                row.append(f"{cell['dominant_regime']} ({cell['all_conditions_passed']}/{cell['trials']})")
            w.writerow(row)
    print("  CSV  → exp_g_regime_map.csv")

    # ── Save best trial ────────────────────────────────────────────────────────
    if best_trial:
        # Strip log to keep file manageable
        best_out = {k: v for k, v in best_trial.items() if k != "log"}
        best_out["log_summary"] = {
            "total_entries": len(best_trial["log"]),
            "first": best_trial["log"][0] if best_trial["log"] else None,
            "last":  best_trial["log"][-1] if best_trial["log"] else None,
        }
        with open("exp_g_best_run.json", "w") as f:
            json.dump(best_out, f, indent=2)
        print("  JSON → exp_g_best_run.json")

    # ── Print summary table ────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("REGIME MAP SUMMARY")
    print(f"{'─'*60}")
    print(f"{'':12} " + "  ".join(f"is={ist:<4}" for ist in influence_strengths))
    for cf in constraint_factors:
        row_parts = []
        for ist in influence_strengths:
            cell = next(c for c in regime_map
                        if c["constraint_factor"]==cf and c["influence_strength"]==ist)
            n = cell["all_conditions_passed"]
            total_t = cell["trials"]
            label = {
                "stable_coexistence":   "COEX",
                "oscillatory_exchange": "OSCL",
                "transient_separation": "TRNS",
                "single_stable_basin":  "SNGL",
                "no_separation":        "NONE",
            }.get(cell["dominant_regime"], "????")
            row_parts.append(f"{label}({n}/{total_t})")
        print(f"cf={cf}    " + "  ".join(row_parts))

    print(f"\nLegend: COEX=stable coexistence  OSCL=oscillatory exchange")
    print(f"        TRNS=transient separation  SNGL=single basin  NONE=no separation")
    print(f"        (n/5) = trials where all 3 conditions passed out of 5 seeds")

    if best_trial:
        bc = best_trial["conditions"]
        bp = best_trial["params"]
        print(f"\nBest trial: cf={bp['constraint_factor']}  is={bp['influence_strength']}  seed={bp['seed']}")
        print(f"  C1 sep_fraction={bc['C1_spontaneous_formation']['separation_fraction']}")
        print(f"  C2 topo_sim    ={bc['C2_topological_persistence']['mean_within_similarity']}")
        print(f"  C3 passed      ={bc['C3_coexistence_without_merger']['passed']}  "
              f"migrations={bc['C3_coexistence_without_merger']['migration_events']}")

    print(f"\n{'='*60}")
    return regime_map


if __name__ == "__main__":
    run_sweep()
