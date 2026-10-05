from pathlib import Path
import json,hashlib,datetime,collections,sys,re
ROOT=Path('/Users/kalani/Repo/evenRealities-openCFW')
CAM='g2/build/pseudocode-first/20260930T190500Z'
def sha(b):return hashlib.sha256(b).hexdigest()
def union(rs):
 out=[]
 for a,z in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
def size(rs):return sum(z-a for a,z in union(rs))
def intersect(x,y):return union([(max(a,b),min(z,w)) for a,z in x for b,w in y if max(a,b)<min(z,w)])
def load(p):return json.loads(p.read_text())
def readlines(p):return list(map(json.loads,p.read_text().splitlines()))
def status(j):
 vals=[str(j[k]).upper() for k in ['decision','status','disposition','verdict'] if isinstance(j.get(k),str)]
 if any(re.search('REVISE|REJECT|WITHDRAW',v) for v in vals):return 'revision'
 return 'pass' if any(v.startswith('PASS') or v.startswith('SCOPED-PASS') for v in vals) else 'unknown'
def reference(j,available):
 refs=[]
 if isinstance(j.get('packet'),str):refs.append(j['packet'])
 if isinstance(j.get('scope'),dict) and isinstance(j['scope'].get('candidate'),str):refs.append(j['scope']['candidate'])
 if not refs:return None,'no_supported_reference'
 found=set()
 for ref in refs:
  p=Path(ref)
  if p.is_absolute() or '..' in p.parts:return None,'unsafe_reference'
  rel=str(p)
  if rel.startswith('analysis/'):rel=CAM+'/'+rel
  if not rel.endswith('/receipt.json'):rel+='/receipt.json'
  if rel not in available:return None,'candidate_not_in_snapshot'
  found.add(rel)
 if len(found)!=1:return None,'ambiguous_reference'
 return next(iter(found)),None

def bind(j,art,images,bytefiles):
 # Snapshot SHA anchors review elsewhere; here validate every candidate layer.
 rp=art['receipt'];rb=bytefiles.get(rp)
 if rb is None or sha(rb)!=art['receipt_sha256']:return [],'candidate_hash_mismatch'
 if status(j)!='pass':return [],'nonpassing_review'
 sc=j.get('scope');checks=j.get('checks')
 if not (isinstance(sc,dict) and isinstance(sc.get('reviewed'),str) and sc['reviewed'].strip()) and not (isinstance(checks,dict) and checks):return [],'unresolved_review_scope'
 if not art['pseudocode']:return [],'no_hash_bound_pseudocode'
 for p in art['pseudocode']:
  if p['path'] not in bytefiles or sha(bytefiles[p['path']])!=p['sha256']:return [],'pseudocode_hash_mismatch'
 receipt=json.loads(rb)
 for name,h in receipt.get('files',{}).items():
  if not isinstance(h,str):return [],'unsupported_file_pin'
  f=str(Path(rp).parent/name)
  if f not in bytefiles or sha(bytefiles[f])!=h:return [],'candidate_file_hash_mismatch'
 out=[]
 for b in art['ranges']:
  im=images.get(b['image'])
  if im is None or im['sha256']!=b['source_sha256']:return [],'wrong_image_hash'
  a,z=b['range'];off=a-im['base']
  if off<0 or z<=a or off+z-a>len(im['data']):return [],'invalid_range'
  if sha(im['data'][off:off+z-a])!=b['body_sha256']:return [],'wrong_body_hash'
  out.append(b)
 return out,('bound_scoped_evidence' if out else 'no_authenticated_ranges')

def fixtures():
 import copy
 data=b'abcdefgh';images={'image':{'sha256':sha(data),'base':100,'data':data}};pseudo=b'limited scope';rb=b'{}';bf={'candidate/receipt.json':rb,'candidate/pseudocode.md':pseudo}
 art={'receipt':'candidate/receipt.json','receipt_sha256':sha(rb),'pseudocode':[{'path':'candidate/pseudocode.md','sha256':sha(pseudo)}],'ranges':[{'image':'image','range':[101,104],'source_sha256':sha(data),'body_sha256':sha(data[1:4])}]};review={'disposition':'PASS_SCOPED','checks':{'bytes':True},'packet':'candidate'}
 assert bind(review,art,images,bf)[1]=='bound_scoped_evidence'
 x=copy.deepcopy(art);x['receipt_sha256']='0'*64;assert bind(review,x,images,bf)[1]=='candidate_hash_mismatch'
 x=copy.deepcopy(art);x['ranges'][0]['source_sha256']='0'*64;assert bind(review,x,images,bf)[1]=='wrong_image_hash'
 x=copy.deepcopy(art);x['ranges'][0]['body_sha256']='0'*64;assert bind(review,x,images,bf)[1]=='wrong_body_hash'
 x=copy.deepcopy(review);x.pop('checks');assert bind(x,art,images,bf)[1]=='unresolved_review_scope'
 x=copy.deepcopy(review);x['decision']='REVISE';assert bind(x,art,images,bf)[1]=='nonpassing_review'
 assert reference({'packet':'a','scope':{'candidate':'b'}},{'a/receipt.json':{},'b/receipt.json':{}})[1]=='ambiguous_reference'
 assert reference({'packet':'../a'},{} )[1]=='unsafe_reference'
 assert reference({'packet':'missing'},{} )[1]=='candidate_not_in_snapshot'
 assert size([[101,104],[101,104],[102,103]])==3
 assert intersect([[101,109]],[[103,105]])==[[103,105]]
 x=copy.deepcopy(art);x['pseudocode'][0]['sha256']='0'*64;assert bind(review,x,images,bf)[1]=='pseudocode_hash_mismatch'
 return 12

def repair(snapshot,out):
 out.mkdir(exist_ok=True);arts=readlines(snapshot/'artifact-ledger.jsonl');index={x['receipt']:x for x in arts};revs=readlines(snapshot/'review-ledger.jsonl');rows=readlines(snapshot/'function-ledger.jsonl');ims=readlines(ROOT/CAM/'inventory/images.jsonl');images={};meta={x['id']:x for x in ims}
 for im in ims:
  p=Path(im['content_path']);p=p if p.is_absolute() else ROOT/p;data=p.read_bytes();assert sha(data)==im['content_sha256']
  maps=[m for s in im.get('address_spaces',[]) for m in s.get('mappings',[]) if 'loaded_start' in m and 'image_start' in m]
  base=maps[0]['loaded_start']-maps[0]['image_start'] if len(maps)==1 else 0
  images[im['id']]={'sha256':im['content_sha256'],'data':data,'base':base}
 # For catalogue codec coordinates use the exact authenticated RUN base.
 for f in (ROOT/'g2/research/corpus/codec/ghidra/open-2026-09-29').glob('*/RUN.json'):
  run=load(f)
  for iid,im in images.items():
   if im['sha256']==run['image_sha256']:im['base']=int(run['base'],0)
 verified=[];newbindings=[];outcomes=collections.Counter();bytefiles={};seen=set();passing=collections.defaultdict(list);rejects=collections.defaultdict(list)
 for rv in revs:
  if rv['candidate_receipts']:continue # Existing parser metric retained as comparison anchor.
  fp=ROOT/rv['review'];raw=fp.read_bytes()
  if sha(raw)!=rv['review_sha256']:outcomes['review_hash_mismatch']+=1;verified.append({'review':rv['review'],'reason':'review_hash_mismatch'});continue
  j=json.loads(raw);cp,err=reference(j,index)
  if err:outcomes[err]+=1;verified.append({'review':rv['review'],'reason':err});continue
  duplicate=(sha(raw),cp)
  if duplicate in seen:
   outcomes['duplicate_review']+=1;verified.append({'review':rv['review'],'candidate':cp,'reason':'duplicate_review'});continue
  seen.add(duplicate)
  if status(j)=='revision':
   rejects[cp].append(rv['review']);outcomes['revision_review']+=1;verified.append({'review':rv['review'],'review_sha256':rv['review_sha256'],'candidate':cp,'reason':'revision_review'});continue
  art=index[cp]
  for pp in [cp]+[p['path'] for p in art['pseudocode']]:
   f=ROOT/pp
   if f.is_file():bytefiles[pp]=f.read_bytes()
  if cp in bytefiles:
   receipt=json.loads(bytefiles[cp])
   for name in receipt.get('files',{}):
    pp=str(Path(cp).parent/name);f=ROOT/pp
    if f.is_file():bytefiles[pp]=f.read_bytes()
  bb,reason=bind(j,art,images,bytefiles);outcomes[reason]+=1
  record={'review':rv['review'],'review_sha256':rv['review_sha256'],'candidate':cp,'candidate_sha256':art['receipt_sha256'],'reason':reason,'ranges':bb,'scope':j.get('scope'),'checks':j.get('checks'),'limitations':j.get('limitations'),'binding':'snapshot-hash-authenticated exact candidate path; review does not itself embed candidate digest','canonical_admission':False,'semantic_completion':False}
  verified.append(record)
  if bb:passing[cp].append(record)
 for cp,rr in passing.items():
  if rejects.get(cp):
   for rec in rr:rec['reason']='conflicting_or_revision';rec['ranges']=[]
   outcomes['bound_candidate_blocked_by_revision']+=1
  else:newbindings.extend(rr)
 # Preserve old extractable reviewed union; add only authenticated new scoped footprint.
 old=list(x for x in readlines(snapshot/'nonoverlapping-intervals.jsonl') if x['metric']=='scoped_pass_evidence');cohorts=collections.defaultdict(list)
 for x in old:cohorts[x['cohort']].append(x['range'])
 image_to_cohort={'apollo_main:flash':'apollo-main/ghidra/open-2026-09-29','apollo_bootloader:flash':'apollo-bootloader/ghidra/open-2026-09-29','case:flash':'case/ghidra/open-2026-09-29','touch:flash':'touch/ghidra/open-2026-09-29'}
 for rec in newbindings:
  for b in rec['ranges']:
   if b['image'] in image_to_cohort:cohorts[image_to_cohort[b['image']]].append(b['range'])
 den=collections.defaultdict(list)
 for row in rows:den[row['cohort']].extend(row['ranges'])
 metrics={};remaining=[];intervals=[]
 for c,dr in den.items():
  rs=intersect(union(dr),union(cohorts[c]));before=size([x['range'] for x in old if x['cohort']==c]);metrics[c]={'catalogued_bytes':size(dr),'old_parser_reviewed_bytes':before,'new_parser_reviewed_bytes':size(rs),'method_gain':size(rs)-before,'percent':100*size(rs)/size(dr)}
  intervals.extend({'cohort':c,'metric':'scoped_pass_evidence','range':z} for z in rs)
  for row in [x for x in rows if x['cohort']==c]:
   rem=[]
   for a,z in row['ranges']:
    pos=a
    for x,y in intersect([[a,z]],rs):
     if x>pos:rem.append([pos,x])
     pos=y
    if pos<z:rem.append([pos,z])
   if rem:remaining.append({'cohort':c,'entry':row['entry'],'remaining_outside_scoped_evidence':rem,'catalogue_body_sha256':row['catalogue_body_sha256']})
 # Project ranges to stored bundle payload offsets using identity-only image spans.
 def offset(i):
  im=meta[i];assert im['transform']['kind']=='identity';a,z=im['source_span'];assert z-a==im['size'];return a+(offset(im['parent_image_id']) if im.get('parent_image_id') else 0)
 projected=collections.defaultdict(list)
 for c in den:
  run=load(ROOT/'g2/research/corpus'/c/'RUN.json');ids=[i for i,x in images.items() if x['sha256']==run['image_sha256']];assert len(ids)==1;i=ids[0];base=int(run['base'],0)
  for x in [a for a in intervals if a['cohort']==c]:
   a,z=x['range'];projected[meta[i]['payload_id']].append([a-base+offset(i),z-base+offset(i)])
 # Existing ARC / conditional stage1 counted once, plus valid repaired evidence for them.
 for art in arts:
  for bb in art['ranges']:
   if bb['review_status']=='scoped_pass' and bb['image'] in ['ble_em9305:record-3','binh_a_stage1']:
    i=bb['image'];a,z=bb['range'];base=images[i]['base'];projected[meta[i]['payload_id']].append([a-base+offset(i),z-base+offset(i)])
 for rec in newbindings:
  for bb in rec['ranges']:
   if bb['image'] in ['ble_em9305:record-3','binh_a_stage1']:
    i=bb['image'];a,z=bb['range'];base=images[i]['base'];projected[meta[i]['payload_id']].append([a-base+offset(i),z-base+offset(i)])
 n=load(snapshot/'bundle-metrics.json')['bundle_bytes'];whole=sum(size(z) for z in projected.values());result={'frozen_snapshot':str(snapshot),'snapshot_scan_utc':load(snapshot/'summary.json')['scan_started_utc'],'repaired_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'review_outcomes':dict(outcomes),'new_bindings':len(newbindings),'per_cohort':metrics,'bundle_reviewed_bytes':whole,'bundle_bytes':n,'bundle_reviewed_percent':100*whole/n,'per_payload_reviewed_bytes':{k:size(v) for k,v in projected.items()},'limits':['Path association authenticated against saved snapshot hashes, not a digest embedded in the original review.','Existing old-parser range decisions are inherited, not independently re-adjudicated.','Footprint union measures scoped review-linked evidence, not whole-function/full-path semantics.','All mapped ranges remain constrained to declared candidate evidence and source bytes; unbound or unsupported scopes excluded.','Candidate revisions block only exact same candidate; cross-version supersession remains a semantic boundary.','Live files are used only if they still match frozen snapshot digests; no current campaign discoveries added.']}
 for name,items in [('repaired-review-ledger.jsonl',verified),('nonoverlapping-intervals.jsonl',intervals),('remaining-outside-scoped-evidence.jsonl',remaining)]: (out/name).write_text(''.join(json.dumps(x)+'\n' for x in items))
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 print('fixtures PASS',fixtures())
 destination=Path(sys.argv[1]);destination.mkdir(exist_ok=True)
 summaries=[]
 for name in ['2026-10-03T0526Z-status','2026-10-03T1341Z-status']:
  summaries.append(repair(destination.parent/name,destination/name))
 (destination/'comparison.json').write_text(json.dumps(summaries,indent=2)+'\n')
 print(json.dumps(summaries,indent=2))
