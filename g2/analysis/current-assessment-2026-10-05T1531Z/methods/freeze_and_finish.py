from pathlib import Path
import json,hashlib,collections,datetime,shutil,subprocess
R=Path('/Users/kalani/Repo/evenRealities-openCFW');A=Path('/Users/kalani/Documents/Codex/OpenCFW/audits');O=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/audits/2026-10-05T1531Z-current');B=A/'2026-10-05T0013Z-status';BR=B/'repaired';P=R/'g2/build/pseudocode-first/20260930T190500Z'
def load(p):return json.loads(p.read_text())
def jl(p):return list(map(json.loads,p.read_text().splitlines()))
def sha(b):return hashlib.sha256(b).hexdigest()
def union(rs):
 out=[]
 for a,z in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
def diff(base,covered):
 out=[]
 for a,z in union(base):
  cursor=a
  for x,y in union(covered):
   if y<=cursor or x>=z:continue
   if x>cursor:out.append([cursor,min(x,z)])
   cursor=max(cursor,min(z,y))
  if cursor<z:out.append([cursor,z])
 return out
old=load(BR/'summary.json');new=load(O/'repaired/summary.json');bundle=load(O/'bundle-metrics.json');inst=load(O/'instruction-metrics.json');n=bundle['bundle_bytes'];state=load(R/'g2/workflow/state.json');manifest=load(R/'g2/manifests/g2-2.2.6.10.json')
# Freeze exact snapshot evidence bytes, including ignored files, in content-addressed storage.
objects=O/'objects';objects.mkdir(exist_ok=True);filepins={};roles=collections.defaultdict(set);conflicts=collections.defaultdict(set)
def add(path,h=None,role='evidence'):
 pp=Path(path);pp=pp if pp.is_absolute() else R/pp
 try:rel=str(pp.relative_to(R))
 except ValueError:return
 if h and rel in filepins and filepins[rel] is not None and filepins[rel]!=h:
  conflicts[rel].update([filepins[rel],h]);roles[rel].add(role);return
 if h:filepins[rel]=h
 else:filepins.setdefault(rel,None)
 roles[rel].add(role)
arts=jl(O/'artifact-ledger.jsonl');reviews=jl(O/'review-ledger.jsonl');oldarts={x['receipt']:x for x in jl(B/'artifact-ledger.jsonl')};oldreviews={x['review']:x for x in jl(B/'review-ledger.jsonl')}
for x in arts:
 add(x['receipt'],x['receipt_sha256'],'receipt')
 for p in x['pseudocode']:add(p['path'],p['sha256'],'pseudocode')
 rp=R/x['receipt']
 if rp.is_file() and sha(rp.read_bytes())==x['receipt_sha256']:
  receipt=load(rp)
  for key in ['files','outputs','artifacts']:
   ff=receipt.get(key)
   if not isinstance(ff,dict):continue
   for name,h in ff.items():
    if isinstance(h,dict):h=h.get('sha256',h.get('expected'))
    if isinstance(h,str) and len(h)==64:add(str(Path(x['receipt']).parent/name),h,'candidate-file')
for x in reviews:add(x['review'],x['review_sha256'],'review')
for x in jl(O/'function-ledger.jsonl'):
 add(x['catalogue_path'],x['catalogue_sha256'],'function-catalogue')
 for p in x['raw_evidence']:add(p,role='raw-export')
for x in jl(P/'inventory/images.jsonl'):add(x['content_path'],x['content_sha256'],'source-image')
for p in ['g2/workflow/state.json','g2/workflow/target.json','g2/manifests/g2-2.2.6.10.json','g2/Makefile','g2/tools/open_cfw.py','g2/components/em9305/source_image/README.md','g2/components/em9305/source_image/build_image.py','g2/components/em9305/source_image/record_package.py',str((P/'inventory/images.jsonl').relative_to(R)),str((P/'inventory/coverage.jsonl').relative_to(R))]:add(p,role='build-or-inventory')
for c in load(R/'g2/workflow/target.json')['components']:add(c['local_payload_path'],c['sha256'],'official-payload')
add('g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin',bundle['bundle_sha256'],'official-bundle')
arc=inst['current_arc_text_export'];add(arc['path'],arc['sha256'],'text-instruction-export')
entries=[];outcomes=collections.Counter()
for path,h in sorted(filepins.items()):
 f=R/path
 if not f.is_file():outcomes['missing']+=1;entries.append({'path':path,'expected_sha256':h,'status':'missing','roles':sorted(roles[path])});continue
 before=f.stat();data=f.read_bytes();after=f.stat();actual=sha(data);status='verified' if h is None or h==actual else 'hash_mismatch'
 if before.st_mtime_ns!=after.st_mtime_ns or before.st_size!=after.st_size:status='changed_during_capture'
 entry={'path':path,'sha256':actual,'expected_sha256':h,'bytes':len(data),'mtime_ns':after.st_mtime_ns,'status':status,'roles':sorted(roles[path]),'conflicting_expected_hashes':sorted(conflicts.get(path,[]))}
 if status=='verified':
  obj=objects/actual
  if not obj.exists():
   previous=B/'objects'/actual
   if previous.is_file():obj.symlink_to(previous)
   else:obj.write_bytes(data)
  entry['object']=str(obj.relative_to(O))
 entries.append(entry);outcomes[status]+=1
(O/'conflicting-file-pins.json').write_text(json.dumps(dict((k,sorted(v)) for k,v in conflicts.items()),indent=2)+'\n')
(O/'immutable-artifact-manifest.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in entries))
source={'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'providers':[{'payload':x['name'],**x['provider']} for x in manifest['components']],'component_c_files':[str(f.relative_to(R)) for f in (R/'g2/components').rglob('*.c')],'c_assignments':state.get('c_implementation_assignments',[]),'gates':state['gates'],'source_gate_receipt_candidates':[str(f.relative_to(R)) for f in (P/'receipts').rglob('receipt.json') if any(s in f.read_text() for s in ['G5_SOURCE_COMPLETE','G6_IDENTICAL_SOURCE_BUILD'])],'completed_blob_free_payloads':0,'payload_denominator':6,'partial_C_percent':None,'build_independence':'Active Makefile reference invokes open_cfw.py build, whose read_providers reads each provider path. All6 active providers point to official binaries. EM9305 build_image.py packages caller-supplied records; it does not implement controller/vendor record programs.'}
(O/'source-build-status.json').write_text(json.dumps(source,indent=2)+'\n')
raw=jl(O/'function-ledger.jsonl');(O/'remaining-raw-exports.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in raw if not x['raw_available']));(O/'unknown-code-data.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in jl(P/'inventory/coverage.jsonl') if x.get('kind')=='unknown'))
# Complete stored-byte complements, explicitly outside measured evidence, not missing executable code.
instruction=collections.defaultdict(list)
for x in jl(O/'instruction-payload-intervals.jsonl'):instruction[x['payload']].append(x['range'])
reviewed=collections.defaultdict(list);images={x['id']:x for x in jl(P/'inventory/images.jsonl')}
def off(i):
 x=images[i];assert x['transform']['kind']=='identity';a,z=x['source_span'];assert z-a==x['size'];return a+(off(x['parent_image_id']) if x.get('parent_image_id') else 0)
for x in jl(O/'repaired/nonoverlapping-intervals.jsonl'):
 run=load(R/'g2/research/corpus'/x['cohort']/'RUN.json');matches=[i for i,v in images.items() if v['content_sha256']==run['image_sha256']];assert len(matches)==1;i=matches[0];base=int(run['base'],0);a,z=x['range'];reviewed[images[i]['payload_id']].append([a-base+off(i),z-base+off(i)])
for x in arts:
 for b in x['ranges']:
  if b['review_status']=='scoped_pass' and b['image'] in ['ble_em9305:record-3','binh_a_stage1']:
   i=b['image'];base=0x302400 if i.startswith('ble') else 0;a,z=b['range'];reviewed[images[i]['payload_id']].append([a-base+off(i),z-base+off(i)])
# Repaired additions for ARC/codec are absent (unchanged); assert totals before publishing complements.
assert sum(sum(z-a for a,z in union(v)) for v in reviewed.values())==new['bundle_reviewed_bytes']
catalogue=collections.defaultdict(list);pseudocode=collections.defaultdict(list)
for x in jl(O/'bundle-byte-ledger.jsonl'):
 catalogue[x['payload']].append(x['payload_range'])
 if x['raw_pseudocode_available']:pseudocode[x['payload']].append(x['payload_range'])
remaining=[]
for metric,ranges in [('candidate_body',catalogue),('instruction_export',instruction),('raw_pseudocode',pseudocode),('scoped_review',reviewed)]:
 for c in load(R/'g2/workflow/target.json')['components']:
  for span in diff([[0,c['size']]],ranges[c['id']]):remaining.append({'payload':c['id'],'metric':metric,'payload_range':span,'payload_sha256':c['sha256'],'interpretation':'stored bytes outside measured subset; not necessarily unexplained executable code'})
(O/'remaining-bundle-ranges.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in remaining))
changes={'baseline_snapshot':str(B),'baseline_corrected_metrics':str(BR/'summary.json'),'current_cutoff_utc':bundle['scan_started_utc'],'current_scan_finished_utc':bundle['scan_finished_utc'],'method':'Unchanged measure.py and unchanged review_repair.py; new supplemental instruction metric applied equally to both frozen snapshots.','reviewed_bytes_previous':old['bundle_reviewed_bytes'],'reviewed_bytes_current':new['bundle_reviewed_bytes'],'reviewed_bytes_progress':new['bundle_reviewed_bytes']-old['bundle_reviewed_bytes'],'per_cohort_progress':{k:v['new_parser_reviewed_bytes']-old['per_cohort'][k]['new_parser_reviewed_bytes'] for k,v in new['per_cohort'].items()},'instruction_json_delta_bytes':inst['comparable_json_delta_bytes'],'artifact_deltas':{'new_receipt_paths':sum(x['receipt'] not in oldarts for x in arts),'changed_receipt_hashes':sum(x['receipt'] in oldarts and x['receipt_sha256']!=oldarts[x['receipt']]['receipt_sha256'] for x in arts),'new_review_paths':sum(x['review'] not in oldreviews for x in reviews),'changed_review_hashes':sum(x['review'] in oldreviews and x['review_sha256']!=oldreviews[x['review']]['review_sha256'] for x in reviews)},'new_vs_stale':'New paths are first observed relative to baseline, not proof of generation time. Previously seen unchanged hashes are reverified stale evidence. mtime retained but not treated as provenance proof.','immutable_manifest_outcomes':dict(outcomes),'repaired_unresolved_counts':new['review_outcomes'],'instruction_unmatched_counts':inst['current_receipt_pinned_json']['outcomes']}
(O/'comparison.json').write_text(json.dumps(changes,indent=2)+'\n')
for f in ['/tmp/opencfw_oct5_instruction.py','/tmp/opencfw_oct5_finish.py']:shutil.copy2(f,O/Path(f).name)
shutil.copy2('/tmp/opencfw-oct5-instruction.log',O/'instruction-validation.log')
print(json.dumps(changes,indent=2));print('Frozen files',len(entries),'objects',len(list(objects.iterdir())))
