#!/usr/bin/env python3
"""Check target -Os against remaining -O2 source-owned XIP units."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
RD=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'

def sections(p):
 t=subprocess.check_output([str(RD),'-SW',str(p)],text=True);out={}
 for l in t.splitlines():
  m=re.search(r'^\s*\[\s*\d+\]\s+(\S+)\s+PROGBITS\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)',l)
  if m:out[m[1]]=int(m[2],16)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int,default=35);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 image=json.loads(a.receipt.read_text())['images']['codec'];base=a.receipt.parent/'codec';cmds=[]
 for row in image['build_commands']:
  v=row['argv']
  if '-c' not in v or '-O2' not in v:continue
  path=v[v.index('-c')+1]
  if '/resident_xip_' not in path:continue
  obj=base/Path(v[v.index('-o')+1]).name
  if not obj.exists():continue
  sec=sections(obj);size=sum(z for n,z in sec.items() if n.startswith('.text.gx8002_xip_'))
  if size:cmds.append((size,path,obj,v,sec))
 rows=[]
 for sz,path,obj,old,prior in sorted(cmds,reverse=True)[:a.limit]:
  out=a.output/obj.name
  cmd=[('-Os' if v=='-O2' else f'type=bind,src={a.output.resolve()},dst=/out' if v.startswith('type=bind,src=') and v.endswith(',dst=/out') else v) for v in old]
  ret=subprocess.run(cmd,capture_output=True,text=True)
  if ret.returncode:rows.append({'source':path,'error':ret.stderr[-1000:]});continue
  newer=sections(out);names={n for n in prior|newer if n.startswith('.text.gx8002_xip_')};before=sum(prior.get(n,0) for n in names);after=sum(newer.get(n,0) for n in names)
  grown={n:newer.get(n,0)-prior.get(n,0) for n in names if newer.get(n,0)>prior.get(n,0)}
  rows.append({'source':path.removeprefix('/repo/'),'source_sha256':hashlib.sha256((ROOT/path.removeprefix('/repo/')).read_bytes()).hexdigest(),'O2_xip_text':before,'Os_xip_text':after,'delta_bytes':after-before,'grown_sections':grown,'O2_object':obj.name,'Os_object_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 result={'receipt_sha256':hashlib.sha256(a.receipt.read_bytes()).hexdigest(),'rows':rows,'total_delta_bytes':sum(r.get('delta_bytes',0) for r in rows),'improved_count':sum(r.get('delta_bytes',0)<0 for r in rows),'regressed_count':sum(r.get('delta_bytes',0)>0 for r in rows)}
 (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print({'rows':len(rows),'total_delta_bytes':result['total_delta_bytes'],'improved':result['improved_count'],'regressed':result['regressed_count']})
if __name__=='__main__':main()
