from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();paths=[Path('g2/workflow/state.json'),b/'inventory/coverage.jsonl',b/'inventory/images.jsonl',b/'inventory/decoded-coverage-summary-001.json'];state=json.loads(paths[0].read_text());rows=[json.loads(x) for x in paths[1].read_text().splitlines() if x.strip()];images=[json.loads(x) for x in paths[2].read_text().splitlines() if x.strip()];groups=defaultdict(list)
for r in rows:groups[(r['scope']['kind'],r['scope']['id'])].append(r)
summary=[]
for (kind,ident),rr in sorted(groups.items()):
 rr.sort(key=lambda x:x['start']);cursor=0;counts=Counter();gaps=[]
 for r in rr:
  if r['start']!=cursor:gaps.append([cursor,r['start']])
  assert r['end']>=r['start'];cursor=r['end'];counts[r['kind']]+=r['end']-r['start']
 summary.append(dict(scope_kind=kind,scope_id=ident,rows=len(rr),extent=cursor,bytes_by_kind=dict(counts),partition_discontinuities=gaps))
missing=[name for name in ['functions.jsonl','data.jsonl','interfaces.jsonl','freeze.json'] if not (b/name).exists() and not (b/'inventory'/name).exists()]
result=dict(accepted=False,status='diagnostic',phase=state['phase'],gates={k:v['status'] for k,v in state['gates'].items()},image_records=len(images),coverage_records=len(rows),scope_summaries=summary,missing_canonical_records_at_campaign_or_inventory_root=missing,input_files={str(p):h(p.read_bytes()) for p in paths},limitations=['Inventory interval classifications do not admit private P2 maps or prove semantic completeness','Historical inventory/status.json is not current workflow gate authority','Unknown interval lengths must not be reduced using overlapping private instruction maps without reviewed ownership reconciliation','This diagnostic does not change admission/gates or supply a freeze denominator'])
o=Path('reviews/P2-15867-canonical-accounting-diagnostic-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'accounting.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['phase','image_records','coverage_records','missing_canonical_records_at_campaign_or_inventory_root','scope_summaries']},indent=2))
