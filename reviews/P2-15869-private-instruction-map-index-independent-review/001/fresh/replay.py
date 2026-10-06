from pathlib import Path
import json,hashlib,subprocess
b=Path('g2/build/pseudocode-first/20260930T190500Z');root=b/'analysis';d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
paths=sorted(Path(x) for x in subprocess.check_output(['rg','--files',str(root),'-g','instructions.json'],text=True).splitlines());records=[];skipped=[];intervals=[]
for p in paths:
 try:
  raw=p.read_bytes();obj=json.loads(raw)
  if not isinstance(obj,list):raise ValueError('unsupported top level')
  blocks=[]
  for block in obj:
   if not isinstance(block,dict) or not isinstance(block.get('instructions'),list):raise ValueError('unsupported block shape')
   rows=block['instructions'];spans=[]
   for r in rows:
    a=r['address'];a=int(a,0) if isinstance(a,str) else a;v=bytes.fromhex(r['bytes'])
    if not 0x438000<=a<a+len(v)<=0x438000+len(d):raise ValueError('outside main flash mapping')
    if d[a-0x438000:a-0x438000+len(v)]!=v:raise ValueError('not main flash byte match')
    if spans and spans[-1][1]==a:spans[-1][1]=a+len(v)
    else:spans.append([a,a+len(v)])
   blocks.extend(spans)
  if not blocks:raise ValueError('no instructions')
  pseudo=p.parent/'pseudocode.md';records.append(dict(path=str(p),sha256=h(raw),ranges=blocks,pseudocode_path=str(pseudo) if pseudo.exists() else None,pseudocode_sha256=h(pseudo.read_bytes()) if pseudo.exists() else None,qualification='byte match only; no image ownership or semantic admission'))
  intervals.extend(blocks)
 except (ValueError,KeyError,TypeError) as e:skipped.append(dict(path=str(p),reason=str(e)))
merged=[]
for start,end in sorted(intervals):
 if merged and start<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],end)
 else:merged.append([start,end])
o=Path('reviews/P2-15869-private-instruction-map-index-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'index.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records));(o/'unindexed.json').write_text(json.dumps(skipped,indent=2)+'\n');(o/'byte-match-union.json').write_text(json.dumps(merged,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='diagnostic',input_sha256=h(d),files_scanned=len(paths),indexed_byte_matching_files=len(records),unindexed_files=len(skipped),unique_byte_matching_instruction_bytes=sum(y-x for x,y in merged),merged_intervals=len(merged),limitations=['Only instructions.json list/block schema indexed; other recovery formats explicitly unindexed','Byte coincidence is not authoritative image ownership','All revisions retained including superseded and incorrect interpretations','Union deduplicates overlap but is not code or reviewed semantic coverage','No canonical admission gate or freeze changes']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
