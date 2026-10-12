#!/usr/bin/env python3
"""Classify selected alloc sections and XIP relocation reachability; no placement inference."""
import argparse, collections, hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
READELF=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
CAPACITY=36484

def run(*args):return subprocess.check_output([str(READELF),*args],text=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 secs={};byname={}
 for line in run('-SW',str(a.candidate)).splitlines():
  m=re.search(r'^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)\s+\d+\s+(\S+)\s+\d+\s+\d+\s+(\d+)',line)
  if not m:continue
  i,n,t,z,f,align=m.groups();i=int(i);secs[i]={'name':n,'type':t,'size':int(z,16),'flags':f,'alignment':int(align)};byname[n]=i
 syms={}
 for line in run('-sW',str(a.candidate)).splitlines():
  m=re.search(r'^\s*\d+:\s+[0-9a-f]+\s+\d+\s+\S+\s+\S+\s+\S+\s+(\d+)\s+(\S+)',line)
  if m:syms[m[2]]=int(m[1])
 graph=collections.defaultdict(set);missing=collections.defaultdict(set);src=None
 for line in run('-rW',str(a.candidate)).splitlines():
  m=re.search(r"^Relocation section '\.rela(\S+)'",line)
  if m:src=byname.get(m[1]);continue
  m=re.search(r'^\s*[0-9a-f]+\s+[0-9a-f]+\s+R_\S+\s+[0-9a-f]+\s+(\S+)',line)
  if m and src is not None:
   target=syms.get(m[1],byname.get(m[1]));(graph[src] if target is not None else missing[src]).add(target if target is not None else m[1])
 direct={i for i,s in secs.items() if s['name'].startswith(('.text.gx8002_xip_','.rodata.gx8002_xip_','.gx8002.sample_name.','.gx8002.flash_name.','.gx8002.xip.')) and s['size']}
 def closure(seeds):
  seen=set(seeds);todo=list(seeds)
  while todo:
   i=todo.pop()
   for j in graph[i]:
    if j not in seen and j in secs and secs[j]['size'] and 'A' in secs[j]['flags']:
     seen.add(j);todo.append(j)
  return seen
 seen=closure(direct)
 def tally(indices):
  arr=[{'section':secs[i]['name'],'bytes':secs[i]['size'],'alignment':secs[i]['alignment']} for i in sorted(indices) if secs[i]['size'] and 'A' in secs[i]['flags'] and secs[i]['type']=='PROGBITS']
  return {'section_count':len(arr),'bytes':sum(x['bytes'] for x in arr),'sections':arr}
 resident={i for i,s in secs.items() if s['name'].startswith(('.text.gx8002_resident_','.rodata.gx8002_resident_')) and s['size']}
 resident_roots=resident|{i for i,s in secs.items() if s['name']=='.text' or s['name'].startswith('.gx8002.') and not s['name'].startswith(('.gx8002.sample_name.','.gx8002.flash_name.','.gx8002.xip.'))}
 joint=closure(direct|resident_roots)
 result={'candidate_sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'native_xip_capacity_bytes':CAPACITY,'direct_xip':tally(direct),'xip_relocation_closure':tally(seen),'closure_extra':tally(seen-direct),'resident_named':tally(resident),'all_source_roots_closure':tally(joint),'source_root_closure_extra':tally(joint-seen),'closure_resident_overlap':tally(seen&resident),'all_alloc_progbits':tally(set(secs)),'unresolved_relocations_from_closure':{secs[i]['name']:sorted(missing[i]) for i in sorted(seen) if missing[i]},'limits':['Relocation closure is a reference graph, not a destination assignment; referenced helpers may reside in SRAM if call reach and loader contracts permit.','Sections omitted from closure may still be reached by indirect pointers or external startup roots.','Summing section bytes omits alignment padding, branch veneers, and final linker-generated literals.']}
 result['closure_minus_capacity_bytes']=result['xip_relocation_closure']['bytes']-CAPACITY
 a.output.write_text(json.dumps(result,indent=2)+'\n')
 print({k:result[k] if not isinstance(result[k],dict) else {x:result[k][x] for x in ('section_count','bytes')} for k in ('direct_xip','xip_relocation_closure','closure_extra','resident_named','closure_resident_overlap','all_alloc_progbits','closure_minus_capacity_bytes')})
if __name__=='__main__':main()
