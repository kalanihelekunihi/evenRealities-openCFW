from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();tp=Path('g2/workflow/target.json');traw=tp.read_bytes();t=json.loads(traw);state=json.loads(Path('g2/workflow/state.json').read_text());assert h(traw)==state['target_lock_sha256'];bundle=Path('g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin');raw=bundle.read_bytes();assert len(raw)==t['bundle']['size'] and h(raw)==t['bundle']['sha256'];outputs=[]
for slug in ['queue-candidate-ledger-16290','clock-candidate-ledger-16294']:
 old=b/'analysis'/slug/'001';new=Path('reviews/P2-15897-target-binding-independent-review/001/fresh2')/slug;new.mkdir(parents=True,exist_ok=False);counts={}
 for name in ['functions.jsonl','data.jsonl']:
  p=old/name;rows=[json.loads(x) for x in p.read_text().splitlines()]
  for r in rows:r.update(target_sha256=t['bundle']['sha256'],target_lock_sha256=h(traw),path_root_kind='repository_relative_campaign',path_root=str(b),direct_input=dict(path=str(p.relative_to(b)),sha256=h(p.read_bytes())))
  (new/name).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));counts[name]=len(rows)
 (new/'revision.json').write_text(json.dumps(dict(accepted=False,status='draft_partial',predecessor=str(old.relative_to(b)),change='Add exact authenticated bundle/target-lock and explicit path-root bindings; preserve source and review evidence',records=counts),indent=2)+'\n');outputs.append(str(new))
o=Path('reviews/P2-15897-target-binding-independent-review/001/fresh2/receipt');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='draft_partial',target_sha256=h(raw),target_lock_sha256=h(traw),bundle_path=str(bundle),outputs=outputs,limitations=['No semantic ownership review admission C freeze or gates']),indent=2)+'\n');print('PASS20 function7data target bindings')
