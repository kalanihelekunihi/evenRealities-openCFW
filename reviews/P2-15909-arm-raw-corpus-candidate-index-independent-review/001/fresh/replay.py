from pathlib import Path
from collections import Counter
import hashlib,json
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();audit=b/'inventory/arm-corpus-reuse-audit-001.json';a=json.loads(audit.read_text());images={x['id']:x for x in [json.loads(l) for l in (b/'inventory/images.jsonl').read_text().splitlines()]};ids={'apollo-main':'apollo_main:flash','apollo-bootloader':'apollo_bootloader:flash','touch':'touch:flash','case':'case:flash'};records=[];summaries=[];pins=[]
for component in a['components']:
 run=Path(component['run_path']);raw=run.read_bytes();assert h(raw)==component['run_sha256'];meta=json.loads(raw);imageid=ids[component['component']];im=images[imageid];d=Path(im['content_path']).read_bytes();assert h(d)==im['content_sha256']==meta['image_sha256'];base=int(meta['base'],16);directory=run.parent;manifest=directory/'SHA256SUMS';manifestpins={}
 for line in manifest.read_text().splitlines():
  sha,name=line.split(None,1);name=name.strip().lstrip('*');p=directory/name;assert h(p.read_bytes())==sha,(p,'manifest');manifestpins[name]=sha
 rows=[]
 for fp in sorted(directory.glob('functions-*.jsonl')):
  pins.append(dict(path=str(fp),sha256=h(fp.read_bytes())));rows.extend(json.loads(l) for l in fp.read_text().splitlines() if l.strip())
 assert len(rows)==component['functions'];status=Counter()
 for row in rows:
  entry=int(row['entry'],16);start=int(row['body_start'],16);end=int(row['body_end_inclusive'],16)+1;assert base<=start<end<=base+len(d);envelope=d[start-base:end-base];assert h(envelope)==row['body_sha256'];ranges=[[int(s,16),int(z,16)+1] for s,z in row['ranges']];assert sum(z-s for s,z in ranges)==row['body_bytes'];assert all(start<=s<z<=end for s,z in ranges)
  actual=[]
  for s,z in ranges:actual.append(dict(runtime_span=[s,z],image_span=[s-base,z-base],sha256=h(d[s-base:z-base])))
  dp=directory/'decomp'/(row['entry']+'.c');decomp=None
  if dp.exists():decomp=dict(path=str(dp),sha256=h(dp.read_bytes()));assert decomp['sha256']==manifestpins[str(dp.relative_to(directory))]
  status['decompiled_true' if row['decompiled'] else 'decompiled_false']+=1
  records.append(dict(accepted=False,status='raw_discovery_only',image_id=imageid,image_sha256=h(d),stable_candidate_id=f'{imageid}:loaded:{entry:08x}:Thumb',entry=entry,discontiguous_body_ranges=actual,bounding_envelope=dict(runtime_span=[start,end],sha256=h(envelope),qualification='Envelope includes gaps; not unique executable coverage'),body_bytes_claim=row['body_bytes'],raw_signature=row['signature'],raw_calling_convention=row['calling_convention'],raw_callees=row['callees'],raw_decompiled_flag=row['decompiled'],raw_decompiler_output=decomp,run=dict(path=str(run),sha256=h(raw)),unresolved=['Function discovery denominator and overlapping/shared-tail ownership unreviewed','Decompiler semantics calling ABI flags faults and indirect edges unreviewed','Raw output not C reconstruction or admitted pseudocode']))
 summaries.append(dict(image_id=imageid,candidate_functions=len(rows),raw_decompiler_status=dict(status),manifest_files_verified=len(manifestpins)));pins.extend([dict(path=str(run),sha256=h(raw)),dict(path=str(manifest),sha256=h(manifest.read_bytes()))])
o=Path('reviews/P2-15909-arm-raw-corpus-candidate-index-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'candidates.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records));(o/'inputs.json').write_text(json.dumps(pins,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='raw_discovery_only',audit_path=str(audit.relative_to(b)),audit_sha256=h(audit.read_bytes()),candidate_functions=len(records),components=summaries,limitations=['Rawdiscovery and decompiler output only not semanticadmission','Bounding hashes explicitly distinguished from actualdiscontiguous body byte hashes','Nested and nonARM images outside this corpusindex; no entirefirmware denominator claim','No C implementation freeze gates']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
