"""
Experiment Q - Hysteresis and Path-Dependence
"""
import math, random, json, time
import numpy as np
from dataclasses import dataclass
from scipy.spatial.distance import cdist

GAUSSIAN_SIGMA=18.0; WAVE_FIELD_DECAY=0.995; ANCHOR_GRAD_THRESH=0.12
ANCHOR_MIN_STRENGTH=0.15; ANCHOR_COLLAPSE=0.05; DRIFT_SPEED=0.18
EDGE_REPEL=8; MAX_ANCHORS=32; STABILITY_THRESHOLD=80; CLUSTER_RADIUS=30.0
TOPOLOGY_EDGE_DIST=55.0; EVENT_RATE=0.012; FIELD_W,FIELD_H=160,120
PHASE_A=1000; PHASE_B=1000; PHASE_C=1000
CF=0.85; IS=1.1
MEMORY_REINFORCE=0.002; MEMORY_SIGMA_MULT=1.5; MEMORY_DECAY=0.9995; MEMORY_WEIGHT=0.15
BIAS_X=FIELD_W//3; SEEDS=[0,1,2,3,4]; LOG_INTERVAL=50

class Field:
    def __init__(self,w,h): self.w=w;self.h=h;self.data=np.zeros(w*h,dtype=np.float32)
    def _idx(self,x,y): return int(max(0,min(self.h-1,int(y))))*self.w+int(max(0,min(self.w-1,int(x))))
    def __getitem__(self,pos): return float(self.data[self._idx(*pos)])
    def decay(self,k): self.data*=k
    def reset(self): self.data[:]=0
    def add_field(self,o): self.data+=o.data
    def copy_from(self,o): self.data=o.data.copy()
    def total_energy(self): return float(np.sum(self.data))
    def gradient(self,x,y):
        xi=max(1,min(self.w-2,int(x)));yi=max(1,min(self.h-2,int(y)))
        gx=(self.data[yi*self.w+xi+1]-self.data[yi*self.w+xi-1])*0.5
        gy=(self.data[(yi+1)*self.w+xi]-self.data[(yi-1)*self.w+xi])*0.5
        return float(gx),float(gy)
    def gradient_magnitude(self,x,y):
        gx,gy=self.gradient(x,y); return math.sqrt(gx*gx+gy*gy)

def apply_gaussian(field,ex,ey,strength,sigma=GAUSSIAN_SIGMA):
    cx,cy=int(ex),int(ey); r=int(sigma*3)
    ys=np.arange(max(0,cy-r),min(field.h,cy+r)); xs=np.arange(max(0,cx-r),min(field.w,cx+r))
    if not len(xs) or not len(ys): return
    yy,xx=np.meshgrid(ys,xs,indexing="ij")
    vals=strength*np.exp(-((xx-cx)**2+(yy-cy)**2).astype(np.float32)/(2*sigma**2))
    np.add.at(field.data,(yy*field.w+xx).ravel(),vals.ravel())

@dataclass
class Anchor:
    x:float;y:float;strength:float;age:int=0;cluster_id:int=-1
    @property
    def is_stable(self): return self.age>=STABILITY_THRESHOLD and self.strength>0.1
    def distance_to(self,o): return math.sqrt((self.x-o.x)**2+(self.y-o.y)**2)

def s_detect(field,stride=6):
    candidates=[]
    for j in range(stride,field.h-stride,stride):
        for i in range(stride,field.w-stride,stride):
            v=field[i,j]
            if v<ANCHOR_MIN_STRENGTH: continue
            if field.gradient_magnitude(i,j)>=ANCHOR_GRAD_THRESH: continue
            if all(field[i+di,j+dj]<=v+0.01 for di in range(-stride,stride+1,stride)
                   for dj in range(-stride,stride+1,stride)
                   if (di,dj)!=(0,0) and 0<=i+di<field.w and 0<=j+dj<field.h):
                candidates.append({"x":float(i),"y":float(j),"strength":v})
    return candidates

def s_drift(anchor,field):
    gx,gy=field.gradient(int(anchor.x),int(anchor.y))
    fx=-gx*DRIFT_SPEED*8;fy=-gy*DRIFT_SPEED*8
    if anchor.x<EDGE_REPEL: fx+=(EDGE_REPEL-anchor.x)*0.1
    if anchor.x>FIELD_W-EDGE_REPEL: fx-=(anchor.x-(FIELD_W-EDGE_REPEL))*0.1
    if anchor.y<EDGE_REPEL: fy+=(EDGE_REPEL-anchor.y)*0.1
    if anchor.y>FIELD_H-EDGE_REPEL: fy-=(anchor.y-(FIELD_H-EDGE_REPEL))*0.1
    anchor.x=max(5,min(FIELD_W-5,anchor.x+fx)); anchor.y=max(5,min(FIELD_H-5,anchor.y+fy))
    anchor.age+=1; anchor.strength=anchor.strength*0.98+field[int(anchor.x),int(anchor.y)]*0.02

def s_cluster(anchors):
    n=len(anchors)
    if not n: return []
    assignments=[-1]*n;cid=0
    for i in range(n):
        if assignments[i]!=-1: continue
        assignments[i]=cid;queue=[i]
        while queue:
            curr=queue.pop()
            for j in range(n):
                if assignments[j]!=-1: continue
                if anchors[curr].distance_to(anchors[j])<=CLUSTER_RADIUS:
                    assignments[j]=cid;queue.append(j)
        cid+=1
    for i,a in enumerate(anchors): a.cluster_id=assignments[i]
    centroids=[]
    for c in range(cid):
        members=[anchors[i] for i in range(n) if assignments[i]==c]
        if not members: continue
        centroids.append({"id":c,"cx":round(sum(a.x for a in members)/len(members),2),
                          "cy":round(sum(a.y for a in members)/len(members),2),"size":len(members)})
    return centroids

def reinforce_memory(memory_field,anchors):
    for a in anchors:
        if a.is_stable:
            apply_gaussian(memory_field,a.x,a.y,MEMORY_REINFORCE,sigma=GAUSSIAN_SIGMA*MEMORY_SIGMA_MULT)

def topo_sig(anchors):
    n=len(anchors)
    if not n: return {"nodes":0,"laplacian_eigenvalues":[],"density":0.0,"components":0,"mean_x":None}
    positions=np.array([[a.x,a.y] for a in anchors])
    dists=cdist(positions,positions)
    adj=((dists<TOPOLOGY_EDGE_DIST)&(dists>0)).astype(float)
    weights=np.where(adj>0,1.0-dists/TOPOLOGY_EDGE_DIST,0.0)
    D=np.diag(np.sum(weights,axis=1));L=D-weights
    try: lap_eigs=sorted([round(float(e),6) for e in np.linalg.eigvalsh(L)])
    except: lap_eigs=[]
    parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b): parent[find(a)]=find(b)
    for i in range(n):
        for j in range(i+1,n):
            if adj[i,j]: union(i,j)
    components=len(set(find(i) for i in range(n)))
    density=int(np.sum(adj)//2)/(n*(n-1)/2) if n>1 else 0.0
    return {"nodes":n,"laplacian_eigenvalues":lap_eigs,"density":round(density,4),
            "components":components,"mean_x":round(float(np.mean([a.x for a in anchors])),2)}

def compare_topo(s1,s2):
    if s1["nodes"]==0 and s2["nodes"]==0: return 1.0
    if s1["nodes"]==0 or s2["nodes"]==0: return 0.0
    e1=s1["laplacian_eigenvalues"];e2=s2["laplacian_eigenvalues"]
    ml=max(len(e1),len(e2))
    e1p=np.array(e1+[0.0]*(ml-len(e1)));e2p=np.array(e2+[0.0]*(ml-len(e2)))
    eig=math.exp(-float(np.linalg.norm(e1p-e2p))*0.15)
    c1,c2=s1["components"],s2["components"]
    return round(0.50*eig+0.20*(1-abs(c1-c2)/max(c1,c2,1))+
                 0.15*(1-abs(s1["density"]-s2["density"]))+
                 0.15*(min(s1["nodes"],s2["nodes"])/max(s1["nodes"],s2["nodes"])),4)

def sep_frac(anchors):
    if not anchors: return None
    return round(sum(1 for a in anchors if a.x>FIELD_W/2)/len(anchors),3)

def run_trial(seed,mode):
    random.seed(seed);np.random.seed(seed)
    gauss=Field(FIELD_W,FIELD_H);wave=Field(FIELD_W,FIELD_H)
    combined=Field(FIELD_W,FIELD_H);memory=Field(FIELD_W,FIELD_H)
    anchors=[];prev={}; mig_c=[]
    snaps={}; total=PHASE_A+PHASE_B+PHASE_C

    for tick in range(1,total+1):
        phase="A" if tick<=PHASE_A else ("B" if tick<=PHASE_A+PHASE_B else "C")
        biased=(phase=="B")
        if random.random()<EVENT_RATE:
            ex=(BIAS_X+random.random()*(FIELD_W-EDGE_REPEL-BIAS_X)) if biased else (EDGE_REPEL+random.random()*(FIELD_W-EDGE_REPEL*2))
            ey=EDGE_REPEL+random.random()*(FIELD_H-EDGE_REPEL*2)
            apply_gaussian(gauss,ex,ey,IS)
        wave.reset();gauss.decay(CF);wave.decay(WAVE_FIELD_DECAY)
        combined.copy_from(gauss);combined.add_field(wave)
        if mode=="with_memory":
            memory.decay(MEMORY_DECAY)
            combined.data+=MEMORY_WEIGHT*memory.data
        if tick%8==0:
            for c in s_detect(combined):
                nb=next((a for a in anchors if math.sqrt((a.x-c["x"])**2+(a.y-c["y"])**2)<18),None)
                if nb: nb.strength=nb.strength*0.85+c["strength"]*0.15;nb.x=nb.x*0.95+c["x"]*0.05;nb.y=nb.y*0.95+c["y"]*0.05
                elif len(anchors)<MAX_ANCHORS: anchors.append(Anchor(c["x"],c["y"],c["strength"]))
            for a in anchors: s_drift(a,combined)
            anchors[:]=[a for a in anchors if a.strength>ANCHOR_COLLAPSE or a.age<30]
            s_cluster(anchors)
            if mode=="with_memory": reinforce_memory(memory,anchors)
            if phase=="C":
                cur={id(a):a.cluster_id for a in anchors};n_a=max(len(anchors),1)
                for a in anchors:
                    aid=id(a);p=prev.get(aid,a.cluster_id)
                    if p!=a.cluster_id and p!=-1: mig_c.append(1.0/n_a)
                prev.clear();prev.update(cur)
        if tick==PHASE_A: snaps["A"]=topo_sig(anchors);snaps["A_sep"]=sep_frac(anchors)
        elif tick==PHASE_A+PHASE_B: snaps["B"]=topo_sig(anchors);snaps["B_sep"]=sep_frac(anchors)
        elif tick==total: snaps["C"]=topo_sig(anchors);snaps["C_sep"]=sep_frac(anchors)

    ac=compare_topo(snaps["A"],snaps["C"]); bc=compare_topo(snaps["B"],snaps["C"])
    ab=compare_topo(snaps["A"],snaps["B"]); mig=round(sum(mig_c)/max(PHASE_C//8,1),6)
    return {"seed":seed,"mode":mode,
            "sim_AC":ac,"sim_BC":bc,"sim_AB":ab,
            "sep_A":snaps["A_sep"],"sep_B":snaps["B_sep"],"sep_C":snaps["C_sep"],
            "hysteresis_score":round(bc-ac,4),"migration_rate_C":mig,
            "mean_x_A":snaps["A"].get("mean_x"),"mean_x_B":snaps["B"].get("mean_x"),
            "mean_x_C":snaps["C"].get("mean_x")}

if __name__=="__main__":
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT Q — Hysteresis")
    print(f"  Phase A:{PHASE_A}t neutral → B:{PHASE_B}t biased → C:{PHASE_C}t neutral")
    print(f"  Hysteresis score = sim(B,C) - sim(A,C)")
    print(f"{'='*60}\n")
    all_results={}; t0=time.time()
    for mode in ["with_memory","without_memory"]:
        print(f"  Mode: {mode}")
        results=[]
        for seed in SEEDS:
            print(f"    seed={seed} elapsed={time.time()-t0:.1f}s",end="\r",flush=True)
            results.append(run_trial(seed,mode))
        print(f"\n    Done.")
        all_results[mode]=results
    with open("exp_q_results.json","w") as f:
        json.dump({"experiment":"Q_hysteresis","results":all_results},f,indent=2)
    print("  JSON → exp_q_results.json\n")
    print(f"{'─'*60}")
    print(f"  {'Mode':<22} {'sim(A,C)':>9} {'sim(B,C)':>9} {'sim(A,B)':>9} {'hyst':>8}  {'sep A→B→C'}")
    print(f"{'─'*60}")
    for mode in ["with_memory","without_memory"]:
        R=all_results[mode]
        ac=round(np.mean([r["sim_AC"] for r in R]),3)
        bc=round(np.mean([r["sim_BC"] for r in R]),3)
        ab=round(np.mean([r["sim_AB"] for r in R]),3)
        hs=round(np.mean([r["hysteresis_score"] for r in R]),4)
        sA=round(np.mean([r["sep_A"] for r in R if r["sep_A"]]),2)
        sB=round(np.mean([r["sep_B"] for r in R if r["sep_B"]]),2)
        sC=round(np.mean([r["sep_C"] for r in R if r["sep_C"]]),2)
        print(f"  {mode:<22} {ac:>9} {bc:>9} {ab:>9} {hs:>8}  {sA}→{sB}→{sC}")
    wm=all_results["with_memory"]; nm=all_results["without_memory"]
    wm_hs=np.mean([r["hysteresis_score"] for r in wm])
    nm_hs=np.mean([r["hysteresis_score"] for r in nm])
    wm_bc=np.mean([r["sim_BC"] for r in wm]); nm_bc=np.mean([r["sim_BC"] for r in nm])
    wm_mx=[(r["mean_x_A"],r["mean_x_B"],r["mean_x_C"]) for r in wm if r["mean_x_C"]]
    nm_mx=[(r["mean_x_A"],r["mean_x_B"],r["mean_x_C"]) for r in nm if r["mean_x_C"]]
    print(f"\n  mean_x A→B→C  with_memory:    {round(np.mean([x[0] for x in wm_mx]),1)}→{round(np.mean([x[1] for x in wm_mx]),1)}→{round(np.mean([x[2] for x in wm_mx]),1)}")
    print(f"  mean_x A→B→C  without_memory: {round(np.mean([x[0] for x in nm_mx]),1)}→{round(np.mean([x[1] for x in nm_mx]),1)}→{round(np.mean([x[2] for x in nm_mx]),1)}")
    print(f"\n  diff hysteresis_score: {round(wm_hs-nm_hs,4)}")
    if wm_hs>nm_hs+0.02: v="HYSTERESIS CONFIRMED — memory field produces path-dependent topology"
    elif wm_bc>0.55 and nm_bc<0.45: v="WEAK HYSTERESIS — directional, below clean threshold"
    else: v="NO HYSTERESIS — both modes recover symmetrically"
    print(f"  → {v}")
    print(f"\n  Total time: {time.time()-t0:.1f}s\n{'='*60}")
