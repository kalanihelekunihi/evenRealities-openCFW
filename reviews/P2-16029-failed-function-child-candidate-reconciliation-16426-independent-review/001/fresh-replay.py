from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');a=b/'analysis';h=lambda x:hashlib.sha256(x).hexdigest();cfg=a/'failed-function-cfg-and-consolidated-draft-16352/001/results.json';c=json.loads(cfg.read_text());idx=a/'campaign-private-instruction-image-candidates-16288/001/index.jsonl';pins={str(cfg):h(cfg.read_bytes()),str(idx):h(idx.read_bytes())};targets=sorted(set(r['target'] for r in c['direct_calls']));found={t:[] for t in targets}
for line in idx.open():
 q=json.loads(line)
 for match in q['candidate_matches']:
  if match['image_id']!='apollo_main:flash':continue
  for t in targets:
   if not any(lo<=t-0x438000<hi for lo,hi in match['image_spans']):continue
   ip=Path(q['path']);pp=Path(q['pseudocode_path']);ih=h(ip.read_bytes());ph=h(pp.read_bytes());pins[str(ip)]=ih;pins[str(pp)]=ph
   found[t].append(dict(kind='older-index-byte-candidate-lead',instructions_path=str(ip),pseudocode_path=str(pp),current_instructions_sha256=ih,current_pseudocode_sha256=ph,index_instructions_pin_matches=ih==q['sha256'],index_pseudocode_pin_matches=ph==q['pseudocode_sha256'],qualification='No owner/function/completeness/review binding inferred from instruction containing entry.'))
for t,n in [(0x540024,16354),(0x561810,16356),(0x561856,16358),(0x561b38,16360),(0x522a16,16364),(0x522ae0,16366),(0x5226e8,16368),(0x4b06a8,16376),(0x4b06c0,16378),(0x4b0748,16380),(0x4b146c,16382),(0x4b1516,16384),(0x4b1548,16386),(0x5144fa,16388),(0x514cf2,16390),(0x514d00,16392),(0x4b0b5a,16396),(0x4b1298,16398),(0x513e2e,16404),(0x514384,16408),(0x522b30,16412)]:
 path=list(a.glob(f'apollo-main-diagnostic-fixed-library-*-{n}-map/'+('002' if n==16398 else '001')));assert len(path)==1;p=path[0];q=json.loads((p/'instructions.json').read_text());assert len(q)==1 and q[0]['start']==t
 for fn in ['instructions.json','pseudocode.md','receipt.json']:pins[str(p/fn)]=h((p/fn).read_bytes())
 found[t].append(dict(kind='new-source-bound-entry-map',path=str(p),start=q[0]['start'],end=q[0]['end'],instruction_bytes=q[0]['end']-q[0]['start'],qualification='Partial/unaccepted entry map, may be only a function prefix; architecture/child effects and full semantics unresolved.'))
records=[dict(entry=t,call_sites=[q['pc'] for q in c['direct_calls'] if q['target']==t],candidate_leads=found[t],status='partial-candidate-evidence' if found[t] else 'no-indexed-instruction-candidate',accepted=False) for t in targets]
res=dict(status='partial',accepted=False,parent_entry=0x540036,children=len(records),children_with_candidate_leads=sum(bool(found[t]) for t in targets),children_without_candidate_leads=sum(not found[t] for t in targets),records=records,limitations=['Lead reconciliation only; containing-entry byte match is not complete child function, semantic coverage, owner or qualified interface.','Review bindings not resolved by this ledger; scoped reviews remain external evidence.','No canonical adoption, C, freeze or gate changes.'])
o=a/'failed-function-child-candidate-reconciliation-16426/001';o.mkdir(parents=True,exist_ok=False);(o/'results.json').write_text(json.dumps(res,indent=2)+'\n');(o/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(status='partial',accepted=False,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',res['children_with_candidate_leads'],'candidate children',res['children_without_candidate_leads'],'without indexed candidates')
