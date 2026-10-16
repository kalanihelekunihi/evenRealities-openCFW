import json,hashlib,datetime,subprocess,collections
from pathlib import Path
ROOT=Path('/Users/kalani/Repo/evenRealities-openCFW'); OUT=ROOT/'g2/analysis/dashboard-wave-integration-20261013/review-20261016-001'; OUT.mkdir(exist_ok=True)
cache={};records=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(s):
 p=Path(s);p=p if p.is_absolute() else ROOT/p
 if str(p) not in cache:
  b=p.read_bytes();cache[str(p)]=b
  rel=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
  dest=OUT/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 return cache[str(p)]
def doc(s):return json.loads(capture(s))
def check(s,h,context):
 try:
  b=capture(s); actual=sha(b);status='match' if actual==h else 'mismatch'
 except Exception as e:actual=None;status='missing';
 records.append(dict(path=s,expected_sha256=h,actual_sha256=actual,status=status,context=context))
def refs(d,ctx):
 if isinstance(d,dict):
  if isinstance(d.get('path'),str) and isinstance(d.get('sha256'),str):check(d['path'],d['sha256'],ctx)
  for k,v in d.items():
   if k.endswith('_sha256'):
    stem=k[:-7]; p=d.get(stem) or d.get(stem+'_path')
    if isinstance(p,str) and ('/' in p):check(p,v,ctx)
   if isinstance(v,(dict,list)):refs(v,ctx)
 elif isinstance(d,list):
  for v in d:refs(v,ctx)
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
target=doc('g2/workflow/target.json');state=doc('g2/workflow/state.json')
audit=doc('g2/analysis/c-source-completion-20261011/six-current-20261014.json');replay=doc('g2/build/c-firmware/20261014/main-post-tail-c-replay/receipt.json')
g1=doc('g2/build/pseudocode-first/20260930T190500Z/receipts/G1-target-and-inventory-107/receipt.json')
base=doc('g2/analysis/coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/full-v3.json')
res=doc('g2/analysis/coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/resource-expansion/dashboard-resources.json')
old=doc('g2/analysis/dashboard-wave-integration-20261013/round651-library-export/OpenCFW MAIN651 immutable receipt.json')
for x,c in [(audit,'six-image audit'),(replay,'main replay'),(g1,'G1 inventory')]:refs(x,c)
# Inspect each pinned stage receipt; bounded one-level evidence, no collectors or firmware execution.
for stage in replay['stages']:
 p=stage.get('receipt')
 if p:
  try:refs(doc(p),'stage receipt '+stage['stage'])
  except Exception as e:records.append(dict(path=p,status='parse_error',error=str(e)))
for c,v in audit['images'].items():
 try:refs(doc(v['receipt']['path']),'component '+c)
 except Exception as e:pass
# Authenticate all official payloads and outer bundle.
check(target['bundle']['verified_local_path'],target['bundle']['sha256'],'official bundle')
for c in target['components']:check(c['local_payload_path'],c['sha256'],'official '+c['id'])
bundle=capture(target['bundle']['verified_local_path']);segments=base['bundle']['segments'];cursor=0
for s in segments:
 a,b=s['range'];assert a==cursor;assert sha(bundle[a:b])==s['sha256'];cursor=b
assert cursor==len(bundle)==4301227
rows=[json.loads(x) for x in capture('g2/build/pseudocode-first/20260930T190500Z/inventory/coverage.jsonl').decode().splitlines()]
ledgers={}
for r in rows:ledgers.setdefault(r['scope']['kind']+':'+r['scope']['id'],[]).append(r)
partitions=[]
for scope,rs in ledgers.items():
 cursor=0;tot=collections.Counter()
 for r in sorted(rs,key=lambda r:r['start']):assert r['start']==cursor;(tot.update({r['kind']:r['end']-r['start']}));cursor=r['end']
 partitions.append(dict(scope=scope,bytes=cursor,kinds=dict(tot)))
# Historical exclusive baseline is byte-complete, not current code recovery coverage.
cur=0;tot=collections.Counter()
for a,b,k in base['bundle']['exclusiveRuns']:assert a==cur;tot[base['bundle']['categories'][k]]+=b-a;cur=b
assert cur==4301227
# Current final ELF import evidence: read tool path from available pinned toolchains.
obj=ROOT/replay['linked_object']; tools=list((ROOT/'tools').glob('**/arm-none-eabi-nm')) if (ROOT/'tools').exists() else []
nm=subprocess.run(['which','arm-none-eabi-nm'],capture_output=True,text=True).stdout.strip()
if nm:
 r=subprocess.run([nm,'-u',str(obj)],capture_output=True,text=True);(OUT/'main-nm-undefined.txt').write_text(r.stdout);nm_result=dict(tool=nm,exit_code=r.returncode,undefined_lines=len(r.stdout.splitlines()))
else:nm_result={'status':'not_on_PATH; candidate hash verified; import count remains recorded evidence'}
components=[]
for c,v in audit['images'].items():
 components.append(dict(id=c,source_complete=v.get('source_complete'),full_payload_linked=v.get('full_payload_linked'),candidate_compilation_passed=v.get('candidate_compilation_passed'),remaining_gate=v.get('remaining_gate'),recorded_unresolved_count=len(v.get('recorded_unresolved',v.get('strong_unresolved',[]))),qualifications={k:x for k,x in v.items() if k in ['resident_rom_binding','mixed_oz_size_frontier','gc_size_frontier','lp_history_capacity_proven']}))
changed=[]
for p,b in cache.items():
 q=Path(p)
 if q.exists() and sha(q.read_bytes())!=sha(b):changed.append(str(q))
result=dict(schema='opencfw-independent-evidence-refresh-v1',snapshot_started_utc=start,snapshot_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Read-only evidence/hash and partition review; no firmware rebuild, native-oracle rerun, producer interruption, source edit or device operation',workflow_phase=state['phase'],gates=state['gates'],bundle=dict(bytes=len(bundle),sha256=sha(bundle),overhead_bytes=base['bundle']['overheadBytes'],payload_bytes=base['bundle']['componentPayloadBytes'],exact_contiguous_segment_partition=True),payloads=target['components'],inventory_partitions=partitions,historical_exclusive_baseline=dict(as_of=base['asOfUTC'],totals=dict(tot),policy='Historical classification only; not promoted to current pseudocode or C byte coverage'),resources=res,components=components,main=dict(stage_count=len(replay['stages']),unresolved_before=replay['unresolved_before'],unresolved_after=replay['unresolved_after'],linked_object=replay['linked_object'],linked_sha256=replay['linked_object_sha256'],nm=nm_result),previous_verified=dict(round=old['round'],selected_apollo_unresolved=old['selected_apollo_unresolved'],whole_images_complete=old['whole_images_complete'],comparison='Different manifest and inclusion policy; do not turn import delta into recovery percentage'),hash_checks=records,hash_check_summary=dict(collections.Counter(r['status'] for r in records)),changed_during_capture=changed,complete_source_payloads=0,exact_payload_equality_proven=0,hardware_validated_payloads=0)
(OUT/'review-dataset.json').write_text(json.dumps(result,indent=2)+'\n')
manifest=[dict(path=str(Path(p).relative_to(ROOT)),sha256=sha(b),bytes=len(b)) for p,b in cache.items() if Path(p).is_relative_to(ROOT)]
(OUT/'snapshot-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(main=result['main'],checks=result['hash_check_summary'],changed=changed,snapshot_files=len(manifest),mismatches=[r for r in records if r['status']!='match'][:20]),indent=2))
