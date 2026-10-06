from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();source=b/'analysis/clock-candidate-ledger-16294/001/functions.jsonl';rows=[json.loads(x) for x in source.read_text().splitlines()];out=[]
for r in rows:
 bound=[];unbound=[];candidate=str(Path(r['pseudocode']['path']).parent)
 for lead in r['candidate_review_references']:
  rp=b/lead['path'];raw=rp.read_bytes();assert h(raw)==lead['sha256'];v=json.loads(raw);candidates=v.get('candidates',[v.get('candidate')]);pins=v.get('fresh_files_sha256',{});checks=dict(exact_candidate_revision=candidate in candidates,image_sha256=v.get('image_sha256')==r['image_sha256'],instruction_sha256=pins.get('instructions.json')==r['instructions']['sha256'],pseudocode_sha256=pins.get('pseudocode.md')==r['pseudocode']['sha256'],decision_pass=str(v.get('decision','')).startswith('PASS'),scope_partial=v.get('accepted') is False and v.get('status')=='partial')
  if all(checks.values()):
   for name in ['instructions.json','pseudocode.md']:assert h((rp.parent/name).read_bytes())==pins[name],(rp,name)
   bound.append(dict(review_id=v['review_id'],path=lead['path'],sha256=h(raw),checks=checks,qualification='Exact scoped partial review binding only; not coverage admission'))
  else:unbound.append(dict(reference=lead,checks=checks))
 r['exact_scoped_review_bindings']=bound;r['unbound_review_leads']=unbound;r['review_binding_status']='bound_scoped_partial' if bound else 'missing_exact_scoped_binding';out.append(r)
o=Path('reviews/P2-15893-clock-review-binding-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'functions.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in out));(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='draft_partial',input=dict(path=str(source.relative_to(b)),sha256=h(source.read_bytes())),function_records=len(out),bound_records=sum(bool(r['exact_scoped_review_bindings']) for r in out),unbound_records=[r['stable_id'] for r in out if not r['exact_scoped_review_bindings']],limitations=['Scoped review bindings not globalownership semanticclosure or canonicaladmission','Allreview acceptedfalse partial preserved','No C freeze gates']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
