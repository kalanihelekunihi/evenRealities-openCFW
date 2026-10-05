from pathlib import Path
import json,hashlib,collections,datetime,sys
R=Path('/Users/kalani/Repo/evenRealities-openCFW');O=Path(sys.argv[1]);P=R/'g2/build/pseudocode-first/20260930T190500Z'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def union(ss):
 out=[]
 for a,z in sorted(ss):
  if out and a<=out[-1][1]:out[-1][1]=max(z,out[-1][1])
  else:out.append([a,z])
 return out
def count(ss):return sum(z-a for a,z in union(ss))
target=json.loads((R/'g2/workflow/target.json').read_text());bundle=R/'g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin';assert sha(bundle)==target['bundle']['sha256'] and bundle.stat().st_size==target['bundle']['size'];sizes={c['id']:c['size'] for c in target['components']};checks=[]
for c in target['components']:
 p=R/c['local_payload_path'];assert sha(p)==c['sha256'] and p.stat().st_size==c['size'];checks.append({'payload':c['id'],'sha256':c['sha256'],'size':c['size'],'verified':True})
ims={r['id']:r for r in map(json.loads,(P/'inventory/images.jsonl').read_text().splitlines())}
def payload_offset(i):
 r=ims[i];assert r['transform']['kind']=='identity';a,z=r['source_span'];assert z-a==r['size'];return a+(payload_offset(r['parent_image_id']) if r['parent_image_id'] else 0)
def meta(cohort):
 runp=R/'g2/research/corpus'/cohort/'RUN.json';run=json.loads(runp.read_text());h=run['image_sha256'];ii=[i for i,r in ims.items() if r['content_sha256']==h];assert len(ii)==1
 return ii[0],int(run['base'],0),str(runp.relative_to(R)),sha(runp)
rows=[json.loads(l) for l in (O/'function-ledger.jsonl').read_text().splitlines()];maps={c:meta(c) for c in {r['cohort'] for r in rows}};catalogue=collections.defaultdict(list);raw=collections.defaultdict(list);ledger=[]
for r in rows:
 iid,base,rp,rh=maps[r['cohort']];im=ims[iid];offset=payload_offset(iid);pay=im['payload_id']
 for a,z in r['ranges']:
  a=a-base+offset;z=z-base+offset;assert 0<=a<z<=sizes[pay];catalogue[pay].append([a,z]);
  if r['raw_available']:raw[pay].append([a,z])
  ledger.append({'payload':pay,'image':iid,'entry':r['entry'],'payload_range':[a,z],'raw_pseudocode_available':r['raw_available'],'catalogue_path':r['catalogue_path'],'catalogue_sha256':r['catalogue_sha256'],'mapping_run':rp,'mapping_run_sha256':rh,'confidence':'candidate catalogue code extent; code/data completeness unvalidated'})
# Review-linked catalogue ranges map independently, excluding decoded/compressed representations.
reviewed=collections.defaultdict(list)
for l in (O/'nonoverlapping-intervals.jsonl').read_text().splitlines():
 r=json.loads(l)
 if r['metric']!='scoped_pass_evidence':continue
 iid,base,_,_=maps[r['cohort']];off=payload_offset(iid);a,z=r['range'];reviewed[ims[iid]['payload_id']].append([a-base+off,z-base+off])
# ARC and BINH A lack comparable catalogues; retain verified declared-body footprints only.
for l in (O/'artifact-ledger.jsonl').read_text().splitlines():
 r=json.loads(l)
 for b in r['ranges']:
  if b['review_status']!='scoped_pass' or b['image'] not in ['ble_em9305:record-3','binh_a_stage1']:continue
  iid=b['image'];base=0x302400 if iid=='ble_em9305:record-3' else 0;off=payload_offset(iid);a,z=b['range'];a=a-base+off;z=z-base+off;pay=ims[iid]['payload_id'];assert 0<=a<z<=sizes[pay];reviewed[pay].append([a,z])
N=target['bundle']['size'];summary={pay:{'payload_bytes':sizes[pay],'catalogued_candidate_body_bytes':count(catalogue[pay]),'raw_pseudocode_addressed_bytes':count(raw[pay]),'scoped_review_linked_bytes':count(reviewed[pay])} for pay in sizes};tot={k:sum(v[k] for v in summary.values()) for k in ['catalogued_candidate_body_bytes','raw_pseudocode_addressed_bytes','scoped_review_linked_bytes']}
current=json.loads((O/'summary.json').read_text());prior=json.loads((R.parent.parent/'Documents/Codex/OpenCFW/audits/2026-10-03T1956Z-status/summary.json').read_text());delta={k:{'previous':prior['summary'][k]['scoped_pass_footprint_bytes'],'current':v['scoped_pass_footprint_bytes'],'change':v['scoped_pass_footprint_bytes']-prior['summary'][k]['scoped_pass_footprint_bytes']} for k,v in current['summary'].items()}
report={'scan_started_utc':current['scan_started_utc'],'scan_finished_utc':current['scan_finished_utc'],'supplement_verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bundle_sha256':target['bundle']['sha256'],'bundle_bytes':N,'payload_checks':checks,'per_payload':summary,'whole_bundle_byte_representation':{k:{'numerator':v,'denominator':N,'percent':100*v/N} for k,v in tot.items()},'delta_from_oct3_1957':delta,'raw_audit_0538_baseline':{'provenance':'prior recorded audit, not a filesystem snapshot','pseudocode_artifacts':1328,'receipts':1820},'fresh_artifact_counts':{'pseudocode_md':len(list((P/'analysis').glob('*/*/pseudocode.md'))),'receipts':len(list((P/'analysis').glob('*/*/receipt.json')))},'limits':['These byte-weighted figures describe stored bundle bytes addressed by candidate function or pseudocode evidence, NOT percentages of completed firmware decompilation.','Catalogued bodies are not validated exhaustive executable-code classification. EM9305 has no complete function catalogue here.','All source projections use identity transforms to payload offsets, unioned within payloads. No decoded RAM expansion is added to its compressed source bytes.','Packaging/resources/weights/padding and unclassified regions remain in the whole-bundle denominator, not declared missing C code.','Review-linked bytes retain scoped/static/controlled-callee limitations; exact semantic completion not inferred.','All six active providers are official_blob. No standalone source-build receipt found; partial C fraction is unmeasured, not asserted zero.'],'method_sha256':sha(Path(__file__))}
(O/'bundle-byte-ledger.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ledger));(O/'bundle-metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
