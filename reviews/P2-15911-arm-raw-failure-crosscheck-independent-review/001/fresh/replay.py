from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();rp=b/'analysis/arm-raw-corpus-candidate-index-16308/001/candidates.jsonl';ip=b/'analysis/campaign-instruction-candidate-ownership-16306/001/intervals.jsonl';raw=[json.loads(l) for l in rp.read_text().splitlines()];byimage=defaultdict(list)
for line in ip.read_text().splitlines():
 r=json.loads(line);byimage[r['image_id']].append(r)
records=[];counts=Counter()
for r in raw:
 if r['raw_decompiled_flag']:continue
 pieces=[];covered=0;missing=0;body=0;owners=set()
 for span in r['discontiguous_body_ranges']:
  a,z=span['image_span'];body+=z-a;cursor=a
  for iv in byimage[r['image_id']]:
   x,y=iv['image_span'];s=max(a,x);end=min(z,y)
   if s>=end:continue
   assert s==cursor;cursor=end;ids=iv['candidate_owner_ids'];n=end-s
   if ids:covered+=n;owners.update(ids)
   else:missing+=n
   pieces.append(dict(image_span=[s,end],candidate_owner_ids=ids))
  assert cursor==z
 assert covered+missing==body==r['body_bytes_claim'];category='fully_candidate_byte_mapped' if missing==0 else ('partly_candidate_byte_mapped' if covered else 'no_candidate_byte_map');counts[category]+=1;records.append(dict(accepted=False,status='diagnostic',stable_candidate_id=r['stable_candidate_id'],image_id=r['image_id'],entry=r['entry'],body_bytes=body,bytes_with_candidate_maps=covered,bytes_without_candidate_maps=missing,category=category,candidate_owner_ids=sorted(owners),pieces=pieces,raw_body_ranges=r['discontiguous_body_ranges'],limitations=['Raw decompiler failure is not proof of opaque semantics','Candidate byte maps are not independent semantic review','Discovered body may be incomplete or overlap data/sharedtail; denominator must be reviewed']))
records.sort(key=lambda x:(-x['bytes_without_candidate_maps'],x['image_id'],x['entry']));o=Path('reviews/P2-15911-arm-raw-failure-crosscheck-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'failures.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records));(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='diagnostic',inputs=[dict(path=str(p.relative_to(b)),sha256=h(p.read_bytes())) for p in [rp,ip]],raw_failed_candidates=len(records),categories=dict(counts),image_counts=dict(Counter(r['image_id'] for r in records)),limitations=['Counts are discovered raw function candidates not wholefirmware semantic denominator','No candidate promoted or discarded; overlap and superseded interpretations preserved','No C admission freeze gates']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print('Largest discovered failed bodies without indexed maps:',[(r['image_id'],hex(r['entry']),r['bytes_without_candidate_maps']) for r in records[:8]])
