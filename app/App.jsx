/**
 * Interaction Dynamics — Experiment Explorer
 * src/App.jsx — drop into a Vite React project
 *
 * Setup:
 *   npm create vite@latest id-explorer -- --template react
 *   cd id-explorer && npm install && npm run dev
 *   Replace src/App.jsx with this file
 *
 * src/index.css — replace with:
 *   *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 *   body { background: #080c14; overflow: hidden; }
 *   ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #0d1117; }
 *   ::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 2px; }
 */

import { useState, useEffect, useRef, useReducer, useCallback } from "react";

// ══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════════════════════════════════════════

const FW = 110, FH = 82, CELL = 5;
const CW = FW * CELL, CH = FH * CELL;
const EDGE = 5;
const ANCHOR_MIN = 0.14, ANCHOR_GRAD = 0.10, ANCHOR_COLLAPSE = 0.04;
const DRIFT_SPEED = 0.20, MAX_ANCHORS = 28, STABLE_AGE = 55, CLUSTER_R = 20;
const PILLAR_POS = [[33, 26], [77, 26], [55, 56]];
const CLUSTER_COLS = ["#38bdf8","#34d399","#fb923c","#a78bfa","#f472b6","#facc15","#60a5fa","#4ade80"];
const HIST_LEN = 250;

// ══════════════════════════════════════════════════════════════════════════════
// FIELD MATH — pure functions, no React
// ══════════════════════════════════════════════════════════════════════════════

const mkField = () => new Float32Array(FW * FH);
const fidx = (x, y) => Math.max(0, Math.min(FH-1, Math.floor(y))) * FW + Math.max(0, Math.min(FW-1, Math.floor(x)));

function applyGauss(field, cx, cy, str, sig) {
  const r = Math.ceil(sig * 2.8), cx0 = Math.floor(cx), cy0 = Math.floor(cy);
  for (let dy = -r; dy <= r; dy++) {
    const y = cy0 + dy; if (y < 0 || y >= FH) continue;
    for (let dx = -r; dx <= r; dx++) {
      const x = cx0 + dx; if (x < 0 || x >= FW) continue;
      field[y*FW+x] = Math.min(2.5, field[y*FW+x] + str * Math.exp(-(dx*dx+dy*dy)/(2*sig*sig)));
    }
  }
}

function fieldGrad(field, x, y) {
  const xi = Math.max(1, Math.min(FW-2, Math.floor(x)));
  const yi = Math.max(1, Math.min(FH-2, Math.floor(y)));
  return [(field[yi*FW+xi+1]-field[yi*FW+xi-1])*0.5, (field[(yi+1)*FW+xi]-field[(yi-1)*FW+xi])*0.5];
}

function detectAnchors(field, stride) {
  const out = [];
  for (let j = stride; j < FH-stride; j += stride) {
    for (let i = stride; i < FW-stride; i += stride) {
      const v = field[j*FW+i];
      if (v < ANCHOR_MIN) continue;
      const [gx, gy] = fieldGrad(field, i, j);
      if (Math.sqrt(gx*gx+gy*gy) >= ANCHOR_GRAD) continue;
      let ok = true;
      for (let dj = -stride; dj <= stride && ok; dj += stride)
        for (let di = -stride; di <= stride && ok; di += stride) {
          if (!di && !dj) continue;
          const ni = i+di, nj = j+dj;
          if (ni<0||ni>=FW||nj<0||nj>=FH) continue;
          if (field[nj*FW+ni] > v+0.01) ok = false;
        }
      if (ok) out.push({ x: i, y: j, s: v });
    }
  }
  return out;
}

// ══════════════════════════════════════════════════════════════════════════════
// SIMULATION ENGINE
// ══════════════════════════════════════════════════════════════════════════════

class Simulation {
  constructor(cfg) {
    this.cfg = cfg;
    this.reset();
  }

  reset() {
    this.field = mkField();
    this.mem   = mkField();
    this.pillar = mkField();
    this.anchors = [];
    this.tick = 0;
    this.phase = "A";
    this.lastMig = 0;
    this.prev = new Map();
    this.nearStable = 0; this.nearTotal = 0;
    this.farStable  = 0; this.farTotal  = 0;

    if (this.cfg.pillars)
      for (const [px, py] of PILLAR_POS) applyGauss(this.pillar, px, py, 0.45, 8);
  }

  step(n = 1) { for (let i = 0; i < n; i++) this._tick(); }

  _tick() {
    const c = this.cfg;
    this.tick++;

    // Phase tracking (Q hysteresis)
    if (c.hysteresis)
      this.phase = this.tick <= 400 ? "A" : this.tick <= 800 ? "B" : "C";

    // Events
    if (Math.random() < (c.eventRate ?? 0.012)) {
      let ex = EDGE + Math.random() * (FW - EDGE*2);
      let ey = EDGE + Math.random() * (FH - EDGE*2);
      if (c.hysteresis && this.phase === "B") ex = FW/3 + Math.random() * (FW * 0.6 - EDGE);
      applyGauss(this.field, ex, ey, c.is ?? 1.1, 10);
    }

    // Decay
    const cf = c.cf ?? 0.85;
    for (let i = 0; i < this.field.length; i++) this.field[i] *= cf;

    // Pillars (persistent — not decayed)
    if (c.pillars) for (let i = 0; i < this.field.length; i++) this.field[i] += this.pillar[i];

    // Memory field
    if (c.memory || c.pillars) {
      for (let i = 0; i < this.mem.length; i++) this.mem[i] *= 0.9995;
      for (let i = 0; i < this.field.length; i++) this.field[i] += 0.15 * this.mem[i];
    }

    if (this.tick % 8 !== 0) return;
    this._updateAnchors();
  }

  _updateAnchors() {
    const c = this.cfg;

    // Detection
    const cands = c.noDetect
      ? Array.from({ length: 4 }, () => {
          const x = EDGE + Math.random()*(FW-EDGE*2), y = EDGE + Math.random()*(FH-EDGE*2);
          return { x, y, s: this.field[fidx(x,y)] };
        })
      : detectAnchors(this.field, 6);

    // Merge / add anchors
    for (const c_ of cands) {
      const nb = this.anchors.find(a => Math.sqrt((a.x-c_.x)**2+(a.y-c_.y)**2) < 14);
      if (nb) { nb.s = nb.s*0.85+c_.s*0.15; nb.x = nb.x*0.95+c_.x*0.05; nb.y = nb.y*0.95+c_.y*0.05; }
      else if (this.anchors.length < MAX_ANCHORS) this.anchors.push({ x:c_.x, y:c_.y, s:c_.s, age:0, cid:-1 });
    }

    // Drift
    for (const a of this.anchors) {
      if (c.noDrift) {
        a.x = Math.max(EDGE, Math.min(FW-EDGE, a.x+(Math.random()-.5)*3));
        a.y = Math.max(EDGE, Math.min(FH-EDGE, a.y+(Math.random()-.5)*3));
        a.age++; a.s = a.s*0.98 + this.field[fidx(a.x,a.y)]*0.02;
        continue;
      }
      let [gx, gy] = fieldGrad(this.field, Math.floor(a.x), Math.floor(a.y));
      if (c.noisy) { gx += (Math.random()-.5)*Math.abs(gx)*4; gy += (Math.random()-.5)*Math.abs(gy)*4; }
      const dir = c.invert ? 1 : -1;
      let fx = dir * (-gx) * DRIFT_SPEED * 8, fy = dir * (-gy) * DRIFT_SPEED * 8;
      if (a.x < EDGE) fx += (EDGE-a.x)*0.1; if (a.x > FW-EDGE) fx -= (a.x-(FW-EDGE))*0.1;
      if (a.y < EDGE) fy += (EDGE-a.y)*0.1; if (a.y > FH-EDGE) fy -= (a.y-(FH-EDGE))*0.1;
      a.x = Math.max(EDGE, Math.min(FW-EDGE, a.x+fx));
      a.y = Math.max(EDGE, Math.min(FH-EDGE, a.y+fy));
      a.age++; a.s = a.s*0.98 + this.field[fidx(a.x,a.y)]*0.02;
    }

    // Prune
    this.anchors = this.anchors.filter(a => a.s > ANCHOR_COLLAPSE || a.age < 18);

    // Cluster
    if (c.antiCluster) {
      const sorted = [...this.anchors].sort((a,b) => a.x+a.y*FW-(b.x+b.y*FW));
      sorted.forEach((a, i) => a.cid = i % 3);
    } else if (!c.noCluster) {
      const n = this.anchors.length;
      const ass = new Array(n).fill(-1); let cid = 0;
      for (let i = 0; i < n; i++) {
        if (ass[i] !== -1) continue;
        ass[i] = cid; const q = [i];
        while (q.length) {
          const cur = q.pop();
          for (let j = 0; j < n; j++) {
            if (ass[j] !== -1) continue;
            const a = this.anchors[cur], b = this.anchors[j];
            if (Math.sqrt((a.x-b.x)**2+(a.y-b.y)**2) <= CLUSTER_R) { ass[j] = cid; q.push(j); }
          }
        }
        cid++;
      }
      this.anchors.forEach((a, i) => a.cid = ass[i]);
    } else {
      this.anchors.forEach(a => a.cid = Math.floor(Math.random()*3));
    }

    // Memory reinforcement
    if (c.memory || c.pillars)
      for (const a of this.anchors)
        if (a.age >= STABLE_AGE && a.s > 0.1) applyGauss(this.mem, a.x, a.y, 0.002, 14);

    // Migration tracking
    this.lastMig = 0;
    for (const a of this.anchors) {
      const prev = this.prev.get(a) ?? a.cid;
      if (prev !== a.cid && prev !== -1) this.lastMig++;
      this.prev.set(a, a.cid);
    }

    // Pillar proximity stats (R)
    if (c.pillars) {
      this.nearStable = 0; this.nearTotal = 0;
      this.farStable  = 0; this.farTotal  = 0;
      for (const a of this.anchors) {
        const d = Math.min(...PILLAR_POS.map(([px,py]) => Math.sqrt((a.x-px)**2+(a.y-py)**2)));
        const stable = a.age >= STABLE_AGE && a.s > 0.1;
        if (d < 24) { this.nearTotal++; if (stable) this.nearStable++; }
        else         { this.farTotal++;  if (stable) this.farStable++;  }
      }
    }
  }

  getStats() {
    const stable = this.anchors.filter(a => a.age >= STABLE_AGE && a.s > 0.1).length;
    const clusters = new Set(this.anchors.map(a=>a.cid).filter(c=>c>=0)).size;
    const n = Math.max(this.anchors.length, 1);
    return {
      tick: this.tick, n: this.anchors.length, stable, clusters,
      migRate: this.lastMig / n,
      phase: this.phase,
      nearPct: this.nearTotal > 0 ? Math.round(this.nearStable/this.nearTotal*100) : 0,
      farPct:  this.farTotal  > 0 ? Math.round(this.farStable/this.farTotal*100)   : 0,
    };
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// RENDERER — pure canvas, no React
// ══════════════════════════════════════════════════════════════════════════════

function renderField(canvas, sim) {
  const ctx = canvas.getContext("2d");
  const img = ctx.createImageData(CW, CH);
  const d   = img.data;
  const max = Math.max(0.3, ...sim.field);

  for (let fy = 0; fy < FH; fy++) for (let fx = 0; fx < FW; fx++) {
    const v = Math.min(1, sim.field[fy*FW+fx] / max);
    const m = Math.min(1, sim.mem[fy*FW+fx] * 3);
    const p = sim.pillar[fy*FW+fx] > 0.05 ? 0.7 : 0;
    for (let dy = 0; dy < CELL; dy++) for (let dx = 0; dx < CELL; dx++) {
      const pi = ((fy*CELL+dy)*CW + (fx*CELL+dx)) * 4;
      d[pi]   = Math.min(255, Math.floor(v*35  + m*20  + p*210));
      d[pi+1] = Math.min(255, Math.floor(v*110 + m*70  + p*175));
      d[pi+2] = Math.min(255, Math.floor(25    + v*185 + m*130 + p*35));
      d[pi+3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);

  // Phase overlay (Q)
  if (sim.cfg.hysteresis && sim.phase === "B") {
    ctx.fillStyle = "rgba(251,146,60,0.10)";
    ctx.fillRect(Math.floor(FW/3)*CELL, 0, (FW - Math.floor(FW/3))*CELL, CH);
  }

  // Pillar rings
  if (sim.cfg.pillars) {
    for (const [px, py] of PILLAR_POS) {
      const ax = px*CELL+CELL/2, ay = py*CELL+CELL/2;
      ctx.beginPath(); ctx.arc(ax, ay, 14, 0, Math.PI*2);
      const g = ctx.createRadialGradient(ax, ay, 3, ax, ay, 14);
      g.addColorStop(0, "rgba(253,230,138,0.35)"); g.addColorStop(1, "rgba(253,230,138,0)");
      ctx.fillStyle = g; ctx.fill();
      ctx.beginPath(); ctx.arc(ax, ay, 14, 0, Math.PI*2);
      ctx.strokeStyle = "#fde68a88"; ctx.lineWidth = 1.5; ctx.stroke();
    }
  }

  // Anchors
  for (const a of sim.anchors) {
    const ax = a.x*CELL+CELL/2, ay = a.y*CELL+CELL/2;
    const stable = a.age >= STABLE_AGE && a.s > 0.1;
    const col = CLUSTER_COLS[Math.max(0, a.cid) % CLUSTER_COLS.length];
    if (stable) {
      ctx.beginPath(); ctx.arc(ax, ay, 10, 0, Math.PI*2);
      ctx.fillStyle = col+"1a"; ctx.fill();
    }
    ctx.beginPath(); ctx.arc(ax, ay, stable ? 5.5 : 3, 0, Math.PI*2);
    ctx.fillStyle = stable ? col : "#64748b"; ctx.fill();
    if (stable) { ctx.beginPath(); ctx.arc(ax, ay, 5.5, 0, Math.PI*2); ctx.strokeStyle = col+"cc"; ctx.lineWidth = 1.5; ctx.stroke(); }
  }
}

function renderSparkline(canvas, history, keys) {
  if (!canvas || history.length < 3) return;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#0d1117"; ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (const { key, col, label } of keys) {
    const vals = history.map(h => h[key]);
    const max = Math.max(...vals, 0.001);
    ctx.strokeStyle = col; ctx.lineWidth = 1.5; ctx.beginPath();
    vals.forEach((v, i) => {
      const x = (i/(vals.length-1)) * canvas.width;
      const y = canvas.height - (v/max) * (canvas.height - 4) - 2;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// EXPERIMENT DEFINITIONS
// ══════════════════════════════════════════════════════════════════════════════

const EXPS = {
  G: {
    id:"G", label:"G — Emergence", phase:"Finding the Phenomenon",
    what:"125/125 trials passed. Every parameter combination produced stable multi-basin topology from random initialization.",
    demonstrates:"Structured field mechanics produce spontaneous multi-basin topology from noise. No seeding, no tuning — just events, drift, and clustering.",
    result:"The uniformity is suspicious. Passing everywhere suggests either very robust physics or trivially-satisfied conditions. Experiment H tests which.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[],
    code:`# Gradient-based local maxima detection
def s_detect(field, stride=6):
    for j in range(stride, field.h-stride, stride):
        for i in range(stride, field.w-stride, stride):
            v = field[i, j]
            if v < ANCHOR_MIN_STRENGTH: continue
            if field.gradient_magnitude(i,j) >= ANCHOR_GRAD_THRESH: continue
            if is_local_max(field, i, j, stride):
                candidates.append({"x": i, "y": j, "strength": v})

# Gradient drift — anchors move downhill
def s_drift(anchor, field):
    gx, gy = field.gradient(anchor.x, anchor.y)
    anchor.x += -gx * DRIFT_SPEED * 8
    anchor.y += -gy * DRIFT_SPEED * 8

# Result: 125/125 passed — suspicious uniformity`,
  },

  H: {
    id:"H", label:"H — Null Control", phase:"Finding the Phenomenon",
    what:"Null mechanics passed 109/125 trials. C2 (topology similarity) was the only real discriminator: 0.9439 structured vs 0.7949 null.",
    demonstrates:"Replacing all three mechanisms with random equivalents shows which conditions were trivially satisfied. C1 and C3 were too weak. Only Laplacian topology similarity carried discriminative weight.",
    result:"The original conditions measured proximity, not structure. Tighter conditions required — see Experiment I.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[{label:"Mechanics",key:"mode",options:[{v:"structured",l:"Structured"},{v:"null",l:"Null (random)"}]}],
    code:`# Null model — all three mechanics replaced:
def null_detect(field, n=4):       # random placement
    return [random_position() for _ in range(n)]

def null_drift(anchor, step=1.5):  # random walk
    anchor.x += random.uniform(-step, step)
    anchor.y += random.uniform(-step, step)

def null_cluster(anchors, k=2):    # random assignment
    for a in anchors:
        a.cluster_id = random.randint(0, k-1)

# Result: null passed 109/125 — original conditions were trivial`,
  },

  K: {
    id:"K", label:"K — Migration Rate", phase:"Building the Discriminator",
    what:"Migration rate C3''' discriminates 42:0 with a 14× gap (0.033 vs 0.472). Null passes 0/125.",
    demonstrates:"After two failed C3 attempts (raw count, gradient ratio), migration rate is the correct observable. Three conditions now map to the primitive triad.",
    result:"C1'→Constraint · C2'→Differentiation · C3'''→Influence. Watch the migration rate counter — it separates structured from null instantly.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[{label:"Mode",key:"mode",options:[{v:"structured",l:"Structured (rate ~0.03)"},{v:"null",l:"Null (rate ~0.47)"}]}],
    code:`# Migration rate — the correct discriminator
# Null: random reassignment every 8 ticks → rate ~0.125+
# Structured: only shifts when spatial layout actually changes → rate ~0.005-0.03

late_updates = (TICKS // 2) // 8
weighted_migrations = sum(1.0/n for _, n in migration_log)
rate = weighted_migrations / late_updates

C3_triple_prime = rate < 0.05   # threshold between structured and null floors

# Result:  structured 42/125 passed · null 0/125 · gap: 14×`,
  },

  M: {
    id:"M", label:"M — Minimality", phase:"Mapping Boundaries",
    what:"Detection redundant (+3 trials). Drift load-bearing (−78%). Clustering absolutely load-bearing (−100%).",
    demonstrates:"Remove one mechanism at a time. Detection is redundant — drift compensates for random placement. Drift and clustering are irreducible.",
    result:"Minimal mechanism: any detection + gradient drift + spatial clustering. Detection method does not matter.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[{label:"Remove",key:"remove",options:[{v:"none",l:"Full structured"},{v:"detect",l:"No detection"},{v:"drift",l:"No drift"},{v:"cluster",l:"No clustering"}]}],
    code:`# Three partial modes — one mechanism replaced per run

# no_detection: random placement instead of gradient detection
# → passes 91/125 (slightly more than full — drift compensates)

# no_drift: random walk replaces gradient drift
# → passes 19/125 (−78%)  LOAD-BEARING

# no_clustering: random assignment replaces spatial clustering
# → passes  0/125 (−100%) ABSOLUTELY LOAD-BEARING

results = {
    "full_structured":  88,  # reference
    "no_detection":     91,  # REDUNDANT
    "no_drift":         19,  # LOAD-BEARING
    "no_clustering":     0,  # ABSOLUTELY LOAD-BEARING
}`,
  },

  N: {
    id:"N", label:"N — Adversarial", phase:"Adversarial Pressure",
    what:"Inverted drift: 33/45 (identical to full). Anti-clustering: 0/45. Noise 200%: 40/45. Temporal scramble: 37/45.",
    demonstrates:"Deliberately break the mechanism. Direction, noise, and update order are not load-bearing. Spatial clustering is the only condition that causes complete failure.",
    result:"Minimal mechanism revised: field-responsive motion (any form, any direction, any noise) + spatial clustering. Gradient descent is not the structural requirement.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[{label:"Adversarial mode",key:"adversarial",options:[{v:"none",l:"Full structured"},{v:"invert",l:"Inverted drift ↑"},{v:"anti",l:"Anti-clustering"},{v:"noisy",l:"200% noise"}]}],
    code:`# Four adversarial inversions:

# inverted_drift:     anchors climb gradient → 33/45 (identical to full)
# anti_clustering:    assign to maximize separation → 0/45  ← FAILS
# temporal_scramble:  randomize update order → 37/45
# noise_injection:    200% noise on gradient → 40/45, no degradation

# Why noise doesn't destroy topology:
# Per-tick direction = dominated by noise
# Over 312 update cycles: systematic component accumulates,
# noise averages to zero. Not noise vs signal — signal vs no signal.

# The irreducible condition: spatial proximity grouping.
# Everything else is implementation detail.`,
  },

  O1: {
    id:"O1", label:"O1 — Field Isolation", phase:"Adversarial Pressure",
    what:"Random walk + spatial clustering: 3/45 (below 15/45 threshold). Field-responsiveness is the irreducible second condition.",
    demonstrates:"Final elimination test: does random walk + spatial clustering alone pass? 3/45 — well below threshold. Positional coupling to field structure is necessary.",
    result:"Minimal mechanism confirmed: field-coupled anchor dynamics + spatial clustering. Positional coupling (not scalar coupling) is the load-bearing factor.",
    simCfg:{cf:0.85,is_:1.1},
    controls:[{label:"Mode",key:"mode",options:[{v:"structured",l:"Full structured (33/45)"},{v:"field_walk",l:"Random detect + field drift (30/45)"},{v:"random_walk",l:"Random walk + clustering (3/45)"}]}],
    code:`# Three-way isolation test

results = {
    "full_structured":      33/45,  # reference
    "field_walk_cluster":   30/45,  # random detect, gradient drift
    "random_walk_cluster":   3/45,  # no field response ← BELOW THRESHOLD
}

# Decision rule: if random_walk_cluster >= 15/45 → clustering alone sufficient
# Result: 3/45 — field-responsiveness is the irreducible second condition

# Note: anchor strength remains field-coupled in all modes (strength update).
# Positional coupling — not scalar coupling — is what matters.`,
  },

  Q: {
    id:"Q", label:"Q — Hysteresis", phase:"Framework Contact",
    what:"sim(B,C) with memory: 0.720 vs without: 0.647. Gap: 0.072. Position converges. Topology retains bias.",
    demonstrates:"Three phases: establish → perturb (biased events right) → restore. Memory field produces path-dependent topology — structure carries its path without storing it.",
    result:"The system returns to where it is spatially. It does not return to what it is structurally. This is the threshold result for identity-level behavior.",
    simCfg:{cf:0.85,is_:1.1,memory:true,hysteresis:true},
    controls:[{label:"Memory field",key:"memory",options:[{v:true,l:"With memory (shows hysteresis)"},{v:false,l:"Without memory (symmetric recovery)"}]}],
    code:`# Memory field — accumulated interaction weighting
memory_field = Field(FIELD_W, FIELD_H)

def reinforce_memory(memory_field, anchors, amount=0.002):
    for a in anchors:
        if a.age >= STABILITY_THRESHOLD and a.strength > 0.1:
            apply_gaussian(memory_field, a.x, a.y, amount, sigma=27)

memory_field.decay(0.9995)      # much slower than constraint_factor 0.85
combined.data += 0.15 * memory_field.data

# Three-phase design:
# Phase A (ticks 1-1000):    neutral events → establish topology A
# Phase B (ticks 1001-2000): biased events right → topology B
# Phase C (ticks 2001-3000): neutral restored → observe recovery

# Result: sim(B,C) with_memory=0.720, without=0.647, gap=0.072`,
  },

  R: {
    id:"R", label:"R — Proto-Valuation", phase:"Proto-Valuation",
    what:"Near-pillar stability: 97.9%. Background (d>40): 18%. Stable anchor mean distance to pillar: 16.4 vs all anchors: 27.5. Gap: 11.1.",
    demonstrates:"Fixed environmental structures create differential stability without semantic assignment. Anchors near pillars are structurally privileged — more stable, lower migration, more memory reinforcement.",
    result:"Proto-valuation without semantics: structural position determines load-bearingness. The system does not know pillars matter. Pillars matter because they alter the stability landscape.",
    simCfg:{cf:0.85,is_:1.1,memory:true,pillars:true},
    controls:[{label:"Environment",key:"pillars",options:[{v:true,l:"Fixed structures (pillars)"},{v:false,l:"Uniform (no pillars)"}]}],
    code:`# Fixed environmental structures — persistent energy pillars
PILLAR_POSITIONS = [(40,40), (120,40), (80,85)]

def build_pillar_field(w, h):
    pillar = Field(w, h)
    for px, py in PILLAR_POSITIONS:
        apply_gaussian(pillar, px, py, 0.35, sigma=12)
    return pillar

# Pillars re-added every tick — they don't decay
combined.data += pillar_field.data

# Stability gradient by distance from nearest pillar:
# d0–20:  0.979   (near pillar)
# d20–40: 0.392
# d40–60: 0.180   (background = same as uniform condition)
# d60–80: 0.167`,
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// CONFIG RESOLVER — clean, explicit, no hacks
// ══════════════════════════════════════════════════════════════════════════════

function resolveConfig(exp, overrides) {
  const base = { ...exp.simCfg };
  const ov = overrides[exp.id] || {};

  // Mode-based (H, K, O1)
  if (ov.mode === "null")        { base.noDetect = true; base.noDrift = true; base.noCluster = true; }
  else if (ov.mode === "random_walk") { base.noDetect = true; base.noDrift = true; }
  else if (ov.mode === "field_walk")  { base.noDetect = true; }
  // "structured" = defaults

  // Mechanism removal (M)
  if (ov.remove === "drift")   base.noDrift = true;
  if (ov.remove === "detect")  base.noDetect = true;
  if (ov.remove === "cluster") base.noCluster = true;

  // Adversarial (N)
  if (ov.adversarial === "invert") base.invert = true;
  if (ov.adversarial === "anti")   base.antiCluster = true;
  if (ov.adversarial === "noisy")  base.noisy = true;

  // Direct overrides (Q, R)
  if (ov.memory  !== undefined) base.memory  = ov.memory;
  if (ov.pillars !== undefined) base.pillars = ov.pillars;

  return base;
}

function getControlDefault(ctrl, simCfg) {
  if (ctrl.key === "mode")       return simCfg.mode || "structured";
  if (ctrl.key === "remove")     return "none";
  if (ctrl.key === "adversarial") return "none";
  if (ctrl.key === "memory")     return simCfg.memory ?? false;
  if (ctrl.key === "pillars")    return simCfg.pillars ?? false;
  return null;
}

// ══════════════════════════════════════════════════════════════════════════════
// STATE MANAGEMENT
// ══════════════════════════════════════════════════════════════════════════════

const PHASES = ["Finding the Phenomenon","Building the Discriminator","Mapping Boundaries","Adversarial Pressure","Cross-Substrate","Framework Contact","Proto-Valuation"];

const initState = {
  expId: "G", tab: "description", running: false, speed: 3,
  overrides: {}, note: "", savedNotes: {},
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_EXP":    return { ...state, expId: action.id, tab: "description", running: false, note: "" };
    case "SET_TAB":    return { ...state, tab: action.tab };
    case "TOGGLE_RUN": return { ...state, running: !state.running };
    case "SET_SPEED":  return { ...state, speed: action.speed };
    case "SET_OVERRIDE": return { ...state, overrides: { ...state.overrides, [state.expId]: { ...(state.overrides[state.expId]||{}), [action.key]: action.val } } };
    case "SET_NOTE":   return { ...state, note: action.note };
    case "LOAD_NOTES": return { ...state, savedNotes: action.notes };
    case "SAVE_NOTE": {
      const entry = { text: state.note.trim(), exp: state.expId, ts: new Date().toISOString() };
      const updated = { ...state.savedNotes, [state.expId]: [...(state.savedNotes[state.expId]||[]), entry] };
      return { ...state, savedNotes: updated, note: "" };
    }
    case "DELETE_NOTE": {
      const arr = (state.savedNotes[action.expId]||[]).filter((_,i)=>i!==action.idx);
      return { ...state, savedNotes: { ...state.savedNotes, [action.expId]: arr } };
    }
    default: return state;
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// APP
// ══════════════════════════════════════════════════════════════════════════════

export default function App() {
  const [state, dispatch] = useReducer(reducer, initState);
  const { expId, tab, running, speed, overrides, note, savedNotes } = state;
  const exp = EXPS[expId];

  const canvasRef   = useRef(null);
  const sparkRef    = useRef(null);
  const simRef      = useRef(null);
  const rafRef      = useRef(null);
  const runningRef  = useRef(false);
  const histRef     = useRef([]); // ring buffer for sparkline
  const [stats, setStats] = useState(null);

  // ── Persist notes ──────────────────────────────────────────────────────────
  useEffect(() => {
    try { const s = localStorage.getItem("id_notes"); if (s) dispatch({ type:"LOAD_NOTES", notes:JSON.parse(s) }); } catch {}
  }, []);

  useEffect(() => {
    try { localStorage.setItem("id_notes", JSON.stringify(savedNotes)); } catch {}
  }, [savedNotes]);

  // ── Build + reset sim when experiment or overrides change ──────────────────
  const buildSim = useCallback(() => {
    const cfg = resolveConfig(exp, overrides);
    simRef.current = new Simulation(cfg);
    histRef.current = [];
    const s = simRef.current.getStats();
    setStats(s);
    if (canvasRef.current) renderField(canvasRef.current, simRef.current);
  }, [expId, overrides, exp]);

  useEffect(() => { buildSim(); }, [buildSim]);

  // ── Animation loop ─────────────────────────────────────────────────────────
  useEffect(() => {
    runningRef.current = running;
    if (!running) return;
    let last = 0;
    const loop = (ts) => {
      if (!runningRef.current) return;
      if (ts - last > 32) {
        const sim = simRef.current;
        sim.step(speed);
        const s = sim.getStats();
        setStats({ ...s });
        histRef.current.push({ migRate: s.migRate, stable: s.stable/Math.max(s.n,1), clusters: s.clusters });
        if (histRef.current.length > HIST_LEN) histRef.current.shift();
        if (canvasRef.current) renderField(canvasRef.current, sim);
        if (sparkRef.current) renderSparkline(sparkRef.current, histRef.current, [
          { key:"migRate", col:"#38bdf8", label:"Migration" },
          { key:"stable",  col:"#34d399", label:"Stability" },
        ]);
        last = ts;
      }
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [running, speed]);

  // ── Keyboard shortcuts ─────────────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") return;
      if (e.code === "Space") { e.preventDefault(); dispatch({ type:"TOGGLE_RUN" }); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // ── Render once when switching to simulation tab ───────────────────────────
  useEffect(() => {
    if (tab === "simulation" && canvasRef.current && simRef.current)
      renderField(canvasRef.current, simRef.current);
  }, [tab]);

  // ── Export notes ──────────────────────────────────────────────────────────
  function exportNotes() {
    const blob = new Blob([JSON.stringify(savedNotes, null, 2)], { type:"application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = "id_notes.json"; a.click();
  }

  // ── Shared styles ──────────────────────────────────────────────────────────
  const S = {
    card: { background:"#0d1117", border:"1px solid #1e2a3a", borderRadius:8, padding:"16px 20px", marginBottom:16 },
    label: { fontSize:10, color:"#4a5568", letterSpacing:"0.1em", marginBottom:8, fontWeight:700 },
    pill: (active) => ({ padding:"4px 13px", border:`1px solid ${active?"#3b82f6":"#1e2a3a"}`, borderRadius:4, cursor:"pointer",
      fontFamily:"inherit", fontSize:11, background:active?"#1a2744":"transparent", color:active?"#93c5fd":"#4a5568", transition:"all 0.15s" }),
    btn: (variant="default") => ({ padding:"6px 18px", border:"1px solid", borderRadius:4, cursor:"pointer",
      fontFamily:"inherit", fontSize:12, fontWeight:700, transition:"all 0.15s",
      ...(variant==="run" ? { background:"#1a3a5f", color:"#60a5fa", borderColor:"#3b82f6" } :
          variant==="stop"? { background:"#7f1d1d", color:"#fca5a5", borderColor:"#ef4444" } :
          { background:"transparent", color:"#64748b", borderColor:"#1e2a3a" }) }),
  };

  const expsByPhase = {};
  Object.values(EXPS).forEach(e => { (expsByPhase[e.phase]||(expsByPhase[e.phase]=[])).push(e); });
  const noteCount = (savedNotes[expId]||[]).length;
  const ov = overrides[expId] || {};

  // ══════════════════════════════════════════════════════════════════════════
  return (
    <div style={{ display:"flex", height:"100vh", background:"#080c14", color:"#e2e8f0",
      fontFamily:"ui-monospace,SFMono-Regular,'SF Mono',Menlo,monospace", fontSize:13, overflow:"hidden" }}>

      {/* ── SIDEBAR ───────────────────────────────────────────────────────── */}
      <div style={{ width:224, background:"#0a0e18", borderRight:"1px solid #1a2030", overflowY:"auto", flexShrink:0 }}>
        <div style={{ padding:"16px 14px 10px", borderBottom:"1px solid #1a2030" }}>
          <div style={{ fontSize:10, fontWeight:800, color:"#60a5fa", letterSpacing:"0.15em" }}>INTERACTION DYNAMICS</div>
          <div style={{ fontSize:9, color:"#374151", letterSpacing:"0.08em", marginTop:2 }}>EXPERIMENT EXPLORER v1.0</div>
        </div>

        {PHASES.filter(p=>expsByPhase[p]).map(phase => (
          <div key={phase}>
            <div style={{ padding:"10px 14px 3px", fontSize:9, fontWeight:700, color:"#374151", letterSpacing:"0.1em", textTransform:"uppercase" }}>{phase}</div>
            {expsByPhase[phase].map(e => (
              <button key={e.id} onClick={() => { dispatch({type:"SET_EXP",id:e.id}); }}
                style={{ width:"100%", display:"flex", alignItems:"center", gap:8, padding:"7px 14px",
                  background:expId===e.id?"#111827":"transparent", border:"none",
                  borderLeft:`2px solid ${expId===e.id?"#3b82f6":"transparent"}`,
                  color:expId===e.id?"#e2e8f0":"#4a5568", cursor:"pointer", textAlign:"left",
                  fontFamily:"inherit", fontSize:11, transition:"all 0.12s" }}>
                <span style={{ color:expId===e.id?"#60a5fa":"#374151", fontWeight:800, minWidth:20 }}>{e.id}</span>
                <span style={{ whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis", flex:1 }}>
                  {e.label.split("—")[1]?.trim()}
                </span>
                {(savedNotes[e.id]||[]).length > 0 &&
                  <span style={{ background:"#1e3a5f", color:"#60a5fa", borderRadius:10, padding:"1px 6px", fontSize:9 }}>
                    {(savedNotes[e.id]||[]).length}
                  </span>}
              </button>
            ))}
          </div>
        ))}

        <div style={{ padding:"12px 14px", borderTop:"1px solid #1a2030", marginTop:8 }}>
          <div style={{ fontSize:9, color:"#374151", marginBottom:6 }}>SPACE = play/pause</div>
          <button onClick={exportNotes} style={{ ...S.btn(), width:"100%", justifyContent:"center", display:"flex", fontSize:10, padding:"5px" }}>
            ↓ export notes
          </button>
        </div>
      </div>

      {/* ── MAIN ──────────────────────────────────────────────────────────── */}
      <div style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden", minWidth:0 }}>

        {/* Header */}
        <div style={{ padding:"14px 22px 0", borderBottom:"1px solid #1a2030", background:"#090d18", flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"baseline", gap:12, marginBottom:10 }}>
            <div style={{ fontSize:17, fontWeight:700, color:"#f1f5f9" }}>{exp.label}</div>
            <div style={{ fontSize:10, color:"#374151", letterSpacing:"0.08em" }}>{exp.phase.toUpperCase()}</div>
          </div>
          <div style={{ display:"flex", gap:0 }}>
            {["description","simulation","code","notes"].map(t => (
              <button key={t} onClick={() => dispatch({type:"SET_TAB",tab:t})} style={{
                padding:"6px 18px", border:"none", background:"transparent", cursor:"pointer",
                color:tab===t?"#60a5fa":"#4a5568", fontFamily:"inherit", fontSize:11, fontWeight:tab===t?700:400,
                borderBottom:`2px solid ${tab===t?"#3b82f6":"transparent"}`,
                textTransform:"uppercase", letterSpacing:"0.08em", transition:"color 0.15s" }}>
                {t}{t==="notes"&&noteCount>0?` (${noteCount})`:""}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div style={{ flex:1, overflow:"auto" }}>

          {/* DESCRIPTION */}
          {tab==="description" && (
            <div style={{ padding:24, maxWidth:700 }}>
              <div style={S.card}>
                <div style={S.label}>WHAT THIS SHOWS</div>
                <div style={{ color:"#94a3b8", lineHeight:1.75 }}>{exp.demonstrates}</div>
              </div>
              <div style={{ ...S.card, borderColor:"#1e3a5f" }}>
                <div style={{ ...S.label, color:"#3b82f6" }}>KEY RESULT</div>
                <div style={{ color:"#bfdbfe", lineHeight:1.75 }}>{exp.what}</div>
              </div>
              <div style={S.card}>
                <div style={S.label}>INTERPRETATION</div>
                <div style={{ color:"#64748b", lineHeight:1.75 }}>{exp.result}</div>
              </div>
            </div>
          )}

          {/* SIMULATION */}
          {tab==="simulation" && (
            <div style={{ padding:20, display:"flex", gap:20, alignItems:"flex-start", flexWrap:"wrap" }}>
              <div>
                {/* Canvas */}
                <canvas ref={canvasRef} width={CW} height={CH}
                  style={{ display:"block", border:"1px solid #1a2030", borderRadius:6 }}/>

                {/* Transport */}
                <div style={{ display:"flex", gap:8, marginTop:10, alignItems:"center", flexWrap:"wrap" }}>
                  <button onClick={() => dispatch({type:"TOGGLE_RUN"})}
                    style={S.btn(running?"stop":"run")}>
                    {running ? "⏹ STOP" : "▶ RUN"}
                  </button>
                  <button onClick={buildSim} style={S.btn()}>↺ RESET</button>
                  <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                    <span style={{ color:"#374151", fontSize:10 }}>SPEED</span>
                    {[1,3,6,15].map(s => (
                      <button key={s} onClick={() => dispatch({type:"SET_SPEED",speed:s})} style={S.pill(speed===s)}>{s}×</button>
                    ))}
                  </div>
                </div>

                {/* Controls */}
                {exp.controls.length > 0 && (
                  <div style={{ marginTop:14, display:"flex", flexDirection:"column", gap:10 }}>
                    {exp.controls.map(ctrl => {
                      const cur = ov[ctrl.key] !== undefined ? ov[ctrl.key] : getControlDefault(ctrl, exp.simCfg);
                      return (
                        <div key={ctrl.key}>
                          <div style={S.label}>{ctrl.label.toUpperCase()}</div>
                          <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
                            {ctrl.options.map(opt => (
                              <button key={String(opt.v)} onClick={() => dispatch({type:"SET_OVERRIDE",key:ctrl.key,val:opt.v})}
                                style={S.pill(String(cur)===String(opt.v))}>
                                {opt.l}
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Sparkline */}
                <div style={{ marginTop:14 }}>
                  <div style={{ fontSize:9, color:"#374151", marginBottom:4, display:"flex", gap:16 }}>
                    <span><span style={{color:"#38bdf8"}}>—</span> migration rate</span>
                    <span><span style={{color:"#34d399"}}>—</span> stability ratio</span>
                  </div>
                  <canvas ref={sparkRef} width={CW} height={52} style={{ borderRadius:4, border:"1px solid #1a2030" }}/>
                </div>
              </div>

              {/* Stats */}
              {stats && (
                <div style={{ minWidth:176 }}>
                  <div style={S.label}>LIVE STATS</div>
                  {[
                    ["Tick",        stats.tick],
                    ["Anchors",     stats.n],
                    ["Stable",      stats.stable],
                    ["Clusters",    stats.clusters],
                    ["Mig/anchor",  stats.migRate.toFixed(3)],
                  ].map(([k,v]) => (
                    <div key={k} style={{ display:"flex", justifyContent:"space-between",
                      padding:"5px 10px", background:"#0d1117", border:"1px solid #1a2030",
                      borderRadius:4, marginBottom:5 }}>
                      <span style={{ color:"#4a5568" }}>{k}</span>
                      <span style={{ color:"#93c5fd", fontWeight:700 }}>{v}</span>
                    </div>
                  ))}

                  {exp.id === "Q" && (
                    <div style={{ marginTop:8, padding:"8px 10px", background:"#0f1f0f",
                      border:"1px solid #1a3a1a", borderRadius:4, textAlign:"center" }}>
                      <div style={{ color:"#86efac", fontWeight:700, fontSize:15 }}>Phase {stats.phase}</div>
                      <div style={{ color:"#4a5568", fontSize:10, marginTop:2 }}>
                        {stats.phase==="A"?"Establish neutral":stats.phase==="B"?"Biased → right":"Neutral restored"}
                      </div>
                    </div>
                  )}

                  {exp.id === "R" && stats.nearPct !== undefined && (
                    <div style={{ marginTop:10 }}>
                      <div style={S.label}>STABILITY GRADIENT</div>
                      {[["Near pillar",stats.nearPct,"#34d399"],["Far from pillar",stats.farPct,"#60a5fa"]].map(([l,v,col]) => (
                        <div key={l} style={{ marginBottom:8 }}>
                          <div style={{ display:"flex", justifyContent:"space-between", marginBottom:3 }}>
                            <span style={{ color:"#4a5568", fontSize:10 }}>{l}</span>
                            <span style={{ color:col, fontWeight:700, fontSize:11 }}>{v}%</span>
                          </div>
                          <div style={{ height:4, background:"#1a2030", borderRadius:2 }}>
                            <div style={{ height:"100%", width:`${v}%`, background:col, borderRadius:2, transition:"width 0.4s" }}/>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* CODE */}
          {tab==="code" && (
            <div style={{ padding:24, maxWidth:740 }}>
              <div style={S.label}>KEY MECHANISM — PYTHON</div>
              <pre style={{ background:"#0d1117", border:"1px solid #1a2030", borderRadius:8,
                padding:"20px 22px", overflowX:"auto", color:"#a5b4fc",
                lineHeight:1.85, fontSize:12, whiteSpace:"pre-wrap" }}>
                {exp.code}
              </pre>
              <div style={{ ...S.card, marginTop:14 }}>
                <div style={S.label}>FULL SOURCE</div>
                <div style={{ color:"#4a5568", fontSize:12 }}>
                  code/experiment_{exp.id.toLowerCase()}*.py — self-contained Python
                  (numpy · scipy{["O1","O2"].some(p=>exp.id.startsWith(p))?" · networkx":""})
                </div>
              </div>
            </div>
          )}

          {/* NOTES */}
          {tab==="notes" && (
            <div style={{ padding:24, maxWidth:680 }}>
              <div style={S.label}>ADD NOTE — {exp.label}</div>
              <textarea value={note} onChange={e => dispatch({type:"SET_NOTE",note:e.target.value})}
                placeholder="Observations · gaps · hypotheses · critique · connections to the framework…"
                style={{ width:"100%", height:100, background:"#0d1117", border:"1px solid #1a2030",
                  borderRadius:6, color:"#e2e8f0", fontFamily:"inherit", fontSize:13,
                  padding:"12px 14px", resize:"vertical", outline:"none",
                  boxSizing:"border-box", lineHeight:1.65 }}/>
              <div style={{ display:"flex", gap:8, marginTop:8 }}>
                <button onClick={() => { if(note.trim()){ dispatch({type:"SAVE_NOTE"}); }}}
                  style={S.btn("run")}>SAVE NOTE</button>
                {noteCount > 0 && (
                  <button onClick={exportNotes} style={S.btn()}>↓ EXPORT ALL</button>
                )}
              </div>

              {noteCount > 0 && (
                <div style={{ marginTop:22 }}>
                  <div style={S.label}>{noteCount} SAVED NOTE{noteCount!==1?"S":""}</div>
                  <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                    {(savedNotes[expId]||[]).map((n, i) => (
                      <div key={i} style={{ background:"#0d1117", border:"1px solid #1a2030",
                        borderRadius:6, padding:"12px 14px", position:"relative" }}>
                        <div style={{ color:"#94a3b8", lineHeight:1.7, whiteSpace:"pre-wrap", paddingRight:24 }}>{n.text}</div>
                        <div style={{ color:"#374151", fontSize:10, marginTop:6 }}>
                          {new Date(n.ts).toLocaleString()}
                        </div>
                        <button onClick={() => dispatch({type:"DELETE_NOTE",expId,idx:i})}
                          style={{ position:"absolute", top:10, right:12, background:"none", border:"none",
                            color:"#374151", cursor:"pointer", fontFamily:"inherit", fontSize:14,
                            padding:2, lineHeight:1 }}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
