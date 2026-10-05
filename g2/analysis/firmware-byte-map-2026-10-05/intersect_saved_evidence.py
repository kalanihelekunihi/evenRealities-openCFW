#!/usr/bin/env python3
"""Intersect saved main-payload evidence with confirmed PCs; no campaign rescan."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;A=ROOT/'g2/build/audits/2026-10-05T0534Z-byte-map';BASE=0x437fe0
rows=lambda p:list(map(json.loads,p.read_text().splitlines()))
def union(rs):
 out=[]
 for a,z in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
def size(rs):return sum(z-a for a,z in union(rs))
def intersect(x,y):return union([(max(a,b),min(z,w)) for a,z in union(x) for b,w in union(y) if max(a,b)<min(z,w)])
C=[r['payload_range'] for r in rows(P/'interval-map.jsonl') if r['payload']=='apollo_main' and r['classification']=='code'];R=[[r['range'][0]-BASE,r['range'][1]-BASE] for r in rows(A/'repaired/nonoverlapping-intervals.jsonl') if r['cohort']=='apollo-main/ghidra/open-2026-09-29'];I=[r['payload_range'] for r in rows(A/'instructions-current/instruction-ledger.jsonl') if r['payload']=='apollo_main'];catalog=rows(A/'bundle-byte-ledger.jsonl');F=[r['payload_range'] for r in catalog if r['payload']=='apollo_main'];Q=[r['payload_range'] for r in catalog if r['payload']=='apollo_main' and r['raw_pseudocode_available']]
assert size(R)==52624 and size(C)==1570
metrics={'known_observed_CPU_code_bytes':size(C),'code_only_intersections':{name:{'bytes':size(intersect(C,ranges)),'percent_of_observed_CPU_code':100*size(intersect(C,ranges))/size(C)} for name,ranges in [('catalogued_candidate_body',F),('raw_pseudocode_body',Q),('prior_receipt_pinned_instruction_export',I),('authenticated_scoped_review',R)]},'limits':['Saved evidence intersection only. Fractions describe this selected 1570-byte observed set, not all firmware executable content or semantic completion.','Only main payload has confirmed execution in this refinement; other payload CPU code remains unclassified.','New display/angle trace exports are evidence introduced by this refinement and would cover observed set by construction; excluded from prior export intersection.'],'evidence_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'interval-map.jsonl',A/'repaired/nonoverlapping-intervals.jsonl',A/'instructions-current/instruction-ledger.jsonl',A/'bundle-byte-ledger.jsonl']}}
(P/'code-evidence-intersections.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
