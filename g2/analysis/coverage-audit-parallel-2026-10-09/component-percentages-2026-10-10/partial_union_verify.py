from pathlib import Path
import json,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09/component-percentages-2026-10-10';D=R/'g2/analysis/source-discovery-parallel-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((D/'partial-artifact-range-unions.json').read_text());ims={x['id']:x for x in [json.loads(l) for l in (R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines()]};manifest={l.split(None,1)[1].lstrip('*'):l.split(None,1)[0] for l in (R/'g2/research/MANIFEST.sha256').read_text().splitlines() if l.strip()};sizes={x['name']:x['provider']['size'] for x in json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text())['components']}
def union(rs):
 out=[]
 for a,b in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(b,out[-1][1])
  else:out.append([a,b])
 return out
out=[]
for c in d['components']:
 run=R/c['run_path'];assert sha(run.read_bytes())==c['run_sha256'];meta=json.loads(run.read_text());im=ims[c['image_id']];b=Path(im['content_path']).read_bytes();assert sha(b)==im['content_sha256']==meta['image_sha256'];assert len(b)==c['image_bytes']==meta['image_size'];base=c['base'];q=run.parent;rs=[];ps=[];fails=[];count=0
 for f in q.glob('functions*.jsonl'):
  assert sha(f.read_bytes())==manifest[str(f.relative_to(R/'g2/research'))]
  for l in f.read_text().splitlines():
   r=json.loads(l);count+=1;a=int(r['body_start'],16);z=int(r['body_end_inclusive'],16)+1;assert base<=a<z<=base+len(b);assert sha(b[a-base:z-base])==r['body_sha256']
   intervals=[[int(a,16),int(z,16)+1] for a,z in r['ranges']];assert all(base<=a<z<=base+len(b) for a,z in intervals);rs+=intervals
   if r['decompiled']:
    export=q/'decomp'/(r['entry']+'.c');s=export.read_text();assert s.strip() and '{' in s and '}' in s;assert sha(export.read_bytes())==manifest[str(export.relative_to(R/'g2/research'))];ps+=intervals
   else:fails.append(r['entry'])
 ru=union(rs);pu=union(ps);assert ru==c['body_ranges'];assert pu==c['raw_pseudocode_ranges'];assert sum(z-a for a,z in pu)==c['raw_pseudocode_range_union_bytes'];assert count==c['records'];assert len(fails)==c['decompiled_false_records'];assert sorted(fails)==sorted(c['missing_decompiled_artifacts']);gap=[];pos=base
 for a,z in pu:
  if pos<a:gap.append([pos,a])
  pos=z
 if pos<base+len(b):gap.append([pos,base+len(b)])
 assert gap==c['uncovered_image_ranges'];name=c['image_id'].split(':')[0];n=sum(z-a for a,z in pu);out.append({'component':name,'envelope_hashes_verified':count,'raw_success_functions':count-len(fails),'raw_union_bytes':n,'payload_bytes':sizes[name],'artifact_associated_payload_percent':round(n/sizes[name]*100,6),'image_bytes':len(b),'image_fraction_percent':round(n/len(b)*100,6),'union_and_complement_verified':True,'nonempty_output_hashes_verified':True})
# Explicit literal example within a successful touch envelope: constructor pool at AA1C–AA2C.
t=next(c for c in d['components'] if c['component']=='touch');assert not any(a<=0xaa1c and z>=0xaa2c for a,z in t['raw_pseudocode_ranges'])
res={'status':'PASS','components':out,'total_envelope_hashes_verified':sum(x['envelope_hashes_verified'] for x in out),'literal_example':'touch constructor envelope ends AA1C before its separately authenticated16-byte literal pool; byte-envelope authentication does not classify remaining corpus ranges as code or data','qualification':'Artifact-associated raw decompiler range fractions only; no executable, semantic review, source or correctness percentage. Four-component cohort, no six-component global total.'};(O/'PARTIAL-UNION-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
