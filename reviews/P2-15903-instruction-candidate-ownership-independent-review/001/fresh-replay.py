from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();source=b/'analysis/campaign-private-instruction-image-candidates-16288/001/index.jsonl';rows=[json.loads(x) for x in source.read_text().splitlines()];images=[json.loads(x) for x in (b/'inventory/images.jsonl').read_text().splitlines()];events=defaultdict(lambda:defaultdict(list));owners=[]
for i,row in enumerate(rows):
 p=Path(row['path']);assert h(p.read_bytes())==row['sha256'];owners.append(dict(id=i,path=str(p.relative_to(b)),sha256=row['sha256'],pseudocode_path=str(Path(row['pseudocode_path']).relative_to(b)) if row.get('pseudocode_path') else None,pseudocode_sha256=row.get('pseudocode_sha256'),candidate_match_count=len(row['candidate_matches'])))
 for match in row['candidate_matches']:
  merged=[]
  for start,end in sorted(match['image_spans']):
   if merged and start<=merged[-1][1]:merged[-1][1]=max(end,merged[-1][1])
   else:merged.append([start,end])
  for start,end in merged:events[match['image_id']][start].append((i,1));events[match['image_id']][end].append((i,-1))
records=[];summaries=[]
for image in images:
 ident=image['id'];size=image['size'];ev=events[ident];ev[0];ev[size];active=Counter();cursor=0;covered=0;multiple=0;n=0
 for pos,changes in sorted(ev.items()):
  assert 0<=pos<=size
  if pos>cursor:
   ids=sorted(k for k,v in active.items() if v>0);kind='candidate_instruction_evidence' if ids else 'no_indexed_instruction_evidence';record=dict(image_id=ident,image_sha256=image['content_sha256'],image_span=[cursor,pos],kind=kind,candidate_owner_ids=ids,accepted=False,status='diagnostic')
   if records and records[-1]['image_id']==ident and records[-1]['candidate_owner_ids']==ids:records[-1]['image_span'][1]=pos
   else:records.append(record);n+=1
   if ids:covered+=pos-cursor
   if len(ids)>1:multiple+=pos-cursor
  for oid,delta in changes:active[oid]+=delta;assert active[oid]>=0
  cursor=pos
 assert cursor==size and not any(active.values())
 summaries.append(dict(image_id=ident,image_bytes=size,bytes_with_candidate_instruction_evidence=covered,bytes_with_multiple_candidate_owners=multiple,bytes_without_indexed_instruction_evidence=size-covered,intervals=n))
o=Path('reviews/P2-15903-instruction-candidate-ownership-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'owners.json').write_text(json.dumps(owners,indent=2)+'\n');(o/'intervals.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records));(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='diagnostic',source_path=str(source.relative_to(b)),source_sha256=h(source.read_bytes()),candidate_map_files=len(rows),image_partitions=len(summaries),intervals=len(records),image_summaries=summaries,limitations=['Candidate byte evidence only not semantic review or code/data classification','Competing owners include revisions broad/narrow maps and possible sharedtails; unresolved not auto-selected','No-indexed-evidence intervals may contain data or other recovery formats; not proven opaque executable code','Conditionalroute/byteorder ambiguity remains in sourceindex; no guard satisfaction asserted','Nested images have separate denominators; never sum image totals as package coverage','No canonical admission freeze gates']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows),'owners',len(records),'intervals',len(summaries),'images');print(json.dumps([x for x in summaries if x['bytes_with_candidate_instruction_evidence']],indent=2))
