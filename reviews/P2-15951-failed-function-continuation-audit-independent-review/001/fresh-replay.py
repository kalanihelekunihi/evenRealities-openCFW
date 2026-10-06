from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z'); a=b/'analysis'; h=lambda x:hashlib.sha256(x).hexdigest()
src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin'; image=src.read_bytes(); assert h(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ids=[16312,16314,16316,16318,16320,16324,16326,16328,16330,16332,16334,16336,16340,16342,16344,16346,16348]; v2={16312,16328,16330,16332,16348}; cursor=0x540036; records=[]; pins={str(src):h(image)}; inscount=0; refs=set()
for n in ids:
 paths=list(a.glob(f'apollo-main-diagnostic-fixed-library-*-{n}-map/'+('002' if n in v2 else '001')));assert len(paths)==1,(n,paths)
 p=paths[0]; data=json.loads((p/'instructions.json').read_text()); assert len(data)==1; q=data[0]; assert q['start']==cursor
 rc=cursor
 for row in q['instructions']:
  raw=bytes.fromhex(row['bytes']); assert row['address']==rc and raw==image[rc-0x438000:rc-0x438000+len(raw)];rc+=len(raw)
 assert rc==q['end']; cursor=rc;inscount+=len(q['instructions'])
 for f in ['instructions.json','pseudocode.md','references.json','receipt.json']:
  pins[str(p/f)]=h((p/f).read_bytes())
 for r in json.loads((p/'references.json').read_text()):
  raw=bytes.fromhex(r['bytes']); off=r['address']-0x438000;assert raw==image[off:off+len(raw)];refs.add(r['address'])
 records.append(dict(candidate_id=n,path=str(p),start=q['start'],end=q['end'],instruction_bytes=q['end']-q['start'],instruction_rows=len(q['instructions'])))
assert cursor==0x5409c4
result=dict(status='partial',accepted=False,image_sha256=h(image),entry=0x540036,raw_discovered_end=0x5409c4,raw_discovered_envelope_bytes=2446,candidate_tiled_start=0x540036,candidate_tiled_end=cursor,candidate_tiled_bytes=cursor-0x540036,unmapped_suffix_start=cursor,unmapped_suffix_end=0x5409c4,unmapped_suffix_bytes=0x5409c4-cursor,candidate_count=len(records),instruction_rows=inscount,literal_reference_addresses=sorted(refs),candidates=records,limitations=['Local byte tiling only; not semantic or whole-function completeness.','Candidate children, floating architectural conditions, external effects and semantic completeness remain unresolved.','No independent-review binding audit, canonical admission, freeze, C or gate change.'])
o=Path('reviews/P2-15951-failed-function-continuation-audit-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False)
(o/'results.json').write_text(json.dumps(result,indent=2)+'\n');(o/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(status='partial',accepted=False,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n')
print('PASS',result['candidate_tiled_bytes'],result['unmapped_suffix_bytes'],inscount)
