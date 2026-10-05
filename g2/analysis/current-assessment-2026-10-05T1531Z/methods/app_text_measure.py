import json,hashlib,re,collections
from pathlib import Path
R=Path('/Users/kalani/Repo/evenRealities-openCFW');O=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/audits/2026-10-05T1531Z-current');data=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();SHA=hashlib.sha256(data).hexdigest();BASE=0x437fe0
m=json.loads((O/'instruction-metrics.json').read_text());ranges=collections.defaultdict(list)
for l in (O/'instruction-payload-intervals.jsonl').read_text().splitlines():
 j=json.loads(l);ranges[j['payload']].append(j['range'])
arts=[];bad=collections.Counter();objects=O/'objects';manifest=[]
for vp in sorted((R/'g2/analysis').glob('*/validation.json')):
 v=json.loads(vp.read_text());image=v.get('image_sha256',v.get('firmware_sha256'))
 if image!=SHA:continue
 for fp in vp.parent.glob('*disassembly*.txt'):
  b=fp.read_bytes();h=hashlib.sha256(b).hexdigest();vh=hashlib.sha256(vp.read_bytes()).hexdigest();count=0
  for line in b.decode().splitlines():
   x=re.match(r'^([0-9a-fA-F]{8})\s+([0-9a-fA-F]+)\s+(\S+)',line)
   if not x:continue
   a=int(x[1],16);bb=bytes.fromhex(x[2]);mn=x[3]
   if mn.startswith('.') or mn in ['???','(bad)','invalid']:bad['invalid_or_data_rows']+=1;continue
   off=a-BASE
   if off<0 or data[off:off+len(bb)]!=bb:bad['unmatched_rows']+=1;continue
   ranges['apollo_main'].append([off,off+len(bb)]);count+=1
  arts.append({'path':str(fp.relative_to(R)),'sha256':h,'validation_path':str(vp.relative_to(R)),'validation_sha256':vh,'source_sha256':SHA,'matched_rows':count,'baseline_limit':'No saved text-file hash in13:41 audit; current-only supplementary evidence, not newly-generated delta.'})
  for pp,raw,hh in [(fp,b,h),(vp,vp.read_bytes(),vh)]:
   if not (objects/hh).exists():(objects/hh).write_bytes(raw)
   manifest.append({'path':str(pp.relative_to(R)),'sha256':hh,'expected_sha256':None,'bytes':len(raw),'mtime_ns':pp.stat().st_mtime_ns,'status':'verified','roles':['supplemental-app-instruction-export'],'object':'objects/'+hh})
def union(ss):
 out=[]
 for a,z in sorted(ss):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
counts={k:sum(z-a for a,z in union(s)) for k,s in ranges.items()};m['current_app_text_exports']=arts;m['current_app_text_outcomes']=dict(bad);m['current_app_text_incremental_bytes']=sum(counts.values())-m['current_combined_instruction_export_bytes'];m['current_combined_instruction_export_bytes']=sum(counts.values());m['per_payload_current_combined']=counts;m['current_combined_percent']=100*sum(counts.values())/4301227;(O/'instruction-metrics.json').write_text(json.dumps(m,indent=2)+'\n');(O/'instruction-payload-intervals.jsonl').write_text(''.join(json.dumps({'payload':p,'range':r})+'\n' for p,rs in ranges.items() for r in union(rs)))
with (O/'immutable-artifact-manifest.jsonl').open('a') as f:f.write(''.join(json.dumps(x)+'\n' for x in manifest))
print('Supplemental app text increment',m['current_app_text_incremental_bytes'],'bytes; new total',m['current_combined_instruction_export_bytes'],counts)
