from pathlib import Path
import json,hashlib,collections,datetime,sys,re
R=Path('/Users/kalani/Repo/evenRealities-openCFW');O=Path(sys.argv[1]);O.mkdir(parents=True,exist_ok=True)
def digest(b):return hashlib.sha256(b).hexdigest()
def jread(p):return json.loads(p.read_text())
def num(x):return int(x,0) if isinstance(x,str) else int(x)
def union(rs):
 out=[]
 for a,z in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
def length(rs):return sum(z-a for a,z in union(rs))
def intersection(x,y):return union([(max(a,b),min(z,w)) for a,z in x for b,w in y if max(a,b)<min(z,w)])
def strings(j):
 if isinstance(j,str):yield j
 elif isinstance(j,dict):
  for x in j.values():yield from strings(x)
 elif isinstance(j,list):
  for x in j:yield from strings(x)
start=datetime.datetime.now(datetime.timezone.utc).isoformat();state=jread(R/'g2/workflow/state.json');P=R/'g2/build/pseudocode-first'/state['campaign_id'];target=jread(R/'g2/workflow/target.json')
images={};checks=[]
for l in (P/'inventory/images.jsonl').read_text().splitlines():
 im=json.loads(l);p=Path(im['content_path']);p=p if p.is_absolute() else R/p
 data=p.read_bytes();ok=digest(data)==im['content_sha256'];checks.append({'image':im['id'],'path':str(p),'sha256':digest(data),'verified':ok});assert ok
 maps=[m for s in im.get('address_spaces',[]) for m in s.get('mappings',[]) if all(k in m for k in ['loaded_start','image_start','image_end'])]
 if len(maps)==1:images[im['content_sha256']]={'record':im,'data':data,'base':maps[0]['loaded_start']-maps[0]['image_start']}
# Codec inventory deliberately records conditional execution contracts, not fixed maps.
# For catalogue comparison only, retain its exact raw-export coordinate system.
codec_cohorts={}
image_records=[json.loads(l) for l in (P/'inventory/images.jsonl').read_text().splitlines()]
for runfile in (R/'g2/research/corpus/codec/ghidra/open-2026-09-29').glob('*/RUN.json'):
 run=jread(runfile);h=run['image_sha256'];matches=[im for im in image_records if im['content_sha256']==h]
 if len(matches)==1:
  im=matches[0];fp=Path(im['content_path']);fp=fp if fp.is_absolute() else R/fp
  images[h]={'record':im,'data':fp.read_bytes(),'base':num(run['base']),'mapping_basis':'raw export coordinate hypothesis, not runtime-placement proof'}
  codec_cohorts[im['id']]=str(runfile.parent.relative_to(R/'g2/research/corpus'))
for im in image_records:
 if im['payload_id']=='codec' and im['content_sha256'] not in images:
  fp=Path(im['content_path']);fp=fp if fp.is_absolute() else R/fp
  images[im['content_sha256']]={'record':im,'data':fp.read_bytes(),'base':0,'mapping_basis':'child file offsets only; runtime unresolved'}
rows=[]
for p in sorted((R/'g2/research/corpus').glob('*/ghidra/open-2026-09-29/**/functions-000.jsonl')):
 component=p.relative_to(R/'g2/research/corpus').parts[0];cohort=str(p.parent.relative_to(R/'g2/research/corpus'));seen=set();catalogue_hash=digest(p.read_bytes())
 for l in p.read_text().splitlines():
  f=json.loads(l);entry=int(f['entry'],16)
  if entry in seen:continue
  seen.add(entry);rs=[[int(a,16),int(z,16)+1] for a,z in f['ranges']];raw=p.parent/'decomp'/f'{f["entry"]}.c'
  rows.append({'cohort':cohort,'component':component,'entry':hex(entry),'ranges':union(rs),'catalogue_body_sha256':f['body_sha256'],'confidence':'catalogue range only; not independently validated code/data boundary','target_sha256':target['bundle']['sha256'],'catalogue_path':str(p.relative_to(R)),'catalogue_sha256':catalogue_hash,'raw_available':bool(f.get('decompiled') and raw.is_file() and raw.stat().st_size),'raw_evidence':[str(raw.relative_to(R))] if f.get('decompiled') and raw.is_file() else [],'canonical_accepted':False,'scoped_review_refs':[]})
oldp=R/'g2/research/corpus/apollo-main/ghidra/decomp';old={x['entry']:x for x in map(json.loads,(oldp/'functions.jsonl').read_text().splitlines())};harvest=jread(oldp/'HARVEST.json');assert all(digest((oldp/f).read_bytes())==h for f,h in harvest['artifacts'].items());marks=dict(re.findall(r'/\* FUN 0x([0-9a-fA-F]+).*?sha256=([0-9a-f]+) \*/',''.join(f.read_text() for f in (oldp/'bundles').glob('*.c'))))
for r in rows:
 e=f'{int(r["entry"],16):08x}'
 if r['component']=='apollo-main' and not r['raw_available'] and e in old and r['catalogue_body_sha256']==old[e]['body_sha256']==marks.get(e):r['raw_available']=True;r['raw_evidence']=[str((oldp/'HARVEST.json').relative_to(R)),str((oldp/'functions.jsonl').relative_to(R))]
# Schema normalizer. Every coordinate interpretation must match stock bytes.
def walk(x,path=()):
 yield path,x
 if isinstance(x,dict):
  for k,v in x.items():yield from walk(v,path+(str(k),))
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+(str(i),))
def ishash(v):return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None
def span(v):
 if isinstance(v,(list,tuple)) and len(v)==2:
  try:return num(v[0]),num(v[1])
  except Exception:return None
 if isinstance(v,str):
  m=re.fullmatch(r'\[?(0x[0-9a-fA-F]+)\s*[,.-]+\s*(0x[0-9a-fA-F]+)\)?\]?',v)
  if m:return int(m[1],16),int(m[2],16)
 return None
def specs(j):
 out=[]
 for path,d in walk(j):
  if not isinstance(d,dict) or any(k in path for k in ['files','literals','literal_pointers','data','references']):continue
  for k,h in d.items():
   m=re.fullmatch(r'(?:0x)?([0-9a-fA-F]{4,8})-(?:0x)?([0-9a-fA-F]{4,8})',k)
   if m and ishash(h):out.append((int(m[1],16),int(m[2],16),h,'range_key_hash'))
  h=next((d[k] for k in ['body_sha256','function_sha256','body_hash','source_byte_sha256','sha256'] if ishash(d.get(k))),None)
  if not h:continue
  for k in ['body_range','body_span','function_span','range','span','code_span','runtime_span','runtime_range','owned_span','image_span','source_range_child_file']:
   if (z:=span(d.get(k))):out.append((*z,h,'span_hash:'+'.'.join(path+(k,))));break
  else:
   a=d.get('start',d.get('entry',d.get('runtime_start')));z=d.get('end',d.get('end_exclusive',d.get('runtime_end_exclusive')))
   try:
    if a is not None and z is None and isinstance(d.get('size',d.get('bytes')),int):z=num(a)+d.get('size',d.get('bytes'))
    if a is not None and z is not None:out.append((num(a),num(z),h,'start_end_hash:'+'.'.join(path)))
   except Exception:pass
 return out
def bind_specs(sp,ims):
 out=[]
 for a,z,h,method in sp:
  matches=[]
  if z<=a:continue
  for im in ims:
   for x in {a,a+im['base']}:
    o=x-im['base'];n=z-a
    if o>=0 and o+n<=len(im['data']) and digest(im['data'][o:o+n])==h:matches.append((im['record']['id'],x,x+n,im))
  unique={(i,x,z):(im) for i,x,z,im in matches}
  if len(unique)==1:
   (i,x,z),im=next(iter(unique.items()));out.append({'image':i,'range':[x,z],'body_sha256':h,'source_sha256':im['record']['content_sha256'],'mapping_method':method})
 return out
receipt_files=sorted((P/'analysis').glob('*/*/receipt.json'));receipts={};hashindex=collections.defaultdict(list);artifact=[]
for cp in receipt_files:
 try:c=jread(cp)
 except Exception:continue
 if not isinstance(c,dict):continue
 h=digest(cp.read_bytes());hashindex[h].append(cp);receipts[cp]=(c,h)
reviewfiles=sorted(set(list((R/'reviews').glob('**/review.json'))+list((P/'reviews').glob('**/review.json'))));revs=[];families=collections.Counter();links=collections.defaultdict(list)
for f in reviewfiles:
 j=jread(f)
 if not isinstance(j,dict):continue
 statuses=[str(j[k]) for k in ['decision','status','result','verdict'] if isinstance(j.get(k),str)];label=' | '.join(statuses);low=label.lower();passed=bool(re.search(r'\bpass(?:es|ed)?\b|^pass_',low)) or low.startswith('scoped-pass');rejected=bool(re.search('revise|revision_required|reject|withdraw',low));passed=passed and not rejected
 family=('candidate='+type(j.get('candidate')).__name__+',pins='+type(j.get('pins')).__name__+',records='+str(isinstance(j.get('records'),list)))
 families[family]+=1;bound=[]
 for path,v in walk(j):
  key='/'.join(path).lower()
  if ishash(v) and 'receipt' in key and not any(t in key for t in ['prior','original_review_value','superseded']):
   for cp in hashindex.get(v,[]):bound.append(cp)
 bound=sorted(set(bound));r={'review':str(f.relative_to(R)),'review_sha256':digest(f.read_bytes()),'family':family,'decision':label,'pass_scoped':passed,'rejected_or_revision':rejected,'accepted':j.get('accepted'),'canonical_admission':j.get('canonical_admission'),'candidate_receipts':[str(p.relative_to(R)) for p in bound],'scope':j.get('scope'),'limitations':j.get('limitations'),'range_specs':specs(j)};revs.append(r)
 for cp in bound:links[cp].append(r)
for cp,(c,ch) in receipts.items():
 files={};filemap={}
 for field in ['files','outputs','artifacts']:
  if isinstance(c.get(field),dict):files.update(c[field])
 for item in c.get('artifact_manifest',[]):
  if isinstance(item,dict) and isinstance(item.get('path'),str) and ishash(item.get('sha256')):files[item['path']]=item['sha256']
 if isinstance(files,dict):
  for name,h in files.items():
   if ishash(h):filemap[name]=h
   elif isinstance(h,dict):
    hh=h.get('sha256',h.get('expected'))
    if ishash(hh):filemap[name]=hh
 pp=[(cp.parent/n,h) for n,h in filemap.items() if 'pseudocode' in n.lower() and n.endswith(('.md','.c','.txt'))];validpp=[(p,h) for p,h in pp if p.is_file() and digest(p.read_bytes())==h]
 rr=links.get(cp,[]);rec={'receipt':str(cp.relative_to(R)),'receipt_sha256':ch,'pseudocode':[{'path':str(p.relative_to(R)),'sha256':h} for p,h in validpp],'accepted':c.get('accepted'),'reviews':[r['review'] for r in rr],'ranges':[],'reason':None}
 if not validpp:rec['reason']='no_hash_bound_pseudocode';artifact.append(rec);continue
 extra=[]
 for name,h in filemap.items():
  fp=cp.parent/name
  if name.endswith(('.json','.jsonl')) and any(t in name.lower() for t in ['function','geometry','scope','body','range','pin']) and fp.is_file() and digest(fp.read_bytes())==h:
   try:extra.append([json.loads(l) for l in fp.read_text().splitlines()] if name.endswith('.jsonl') else jread(fp))
   except Exception:pass
 imhash=set(strings([c,extra]))&images.keys();ims=[images[h] for h in imhash]
 # Explicit metadata from independently pinned reviews can supply missing source hashes.
 if not ims:
  for r in rr:
   jj=jread(R/r['review'])
   for h in set(strings(jj))&images.keys():
    if images[h] not in ims:ims.append(images[h])
 if not ims:rec['reason']='no_authenticated_mapped_source_binding';artifact.append(rec);continue
 sp=specs([c,extra]);bound=bind_specs(sp,ims)
 for path,d in walk([c,extra]):
  if not isinstance(d,dict):continue
  # Explicit multipart hash: validate concatenated slices in declared order.
  for key,v in d.items():
   if not key.endswith('body_ranges') or not isinstance(v,list):continue
   hh=d.get(key[:-6]+'sha256')
   if not ishash(hh):continue
   try:ss=[span(x) for x in v];assert all(ss)
   except Exception:continue
   found=[]
   for im in ims:
    for delta in {0,im['base']}:
     spans=[(a+delta,z+delta) for a,z in ss]
     if all(a>=im['base'] and z>a and z-im['base']<=len(im['data']) for a,z in spans):
      if digest(b''.join(im['data'][a-im['base']:z-im['base']] for a,z in spans))==hh:found.append((im,spans))
   if len(found)==1:
    im,spans=found[0]
    for a,z in spans:bound.append({'image':im['record']['id'],'range':[a,z],'body_sha256':digest(im['data'][a-im['base']:z-im['base']]),'source_sha256':im['record']['content_sha256'],'mapping_method':'multipart_body_hash'})
  # Coordinate-qualified source-bound range: no separate body hash required.
  for key in ['runtime_span','image_span']:
   ss=span(d.get(key))
   if not ss:continue
   for im in ims:
    a,z=ss
    if key=='image_span':a+=im['base'];z+=im['base']
    if a>=im['base'] and z>a and z-im['base']<=len(im['data']):bound.append({'image':im['record']['id'],'range':[a,z],'body_sha256':digest(im['data'][a-im['base']:z-im['base']]),'source_sha256':im['record']['content_sha256'],'mapping_method':'explicit_'+key+'_authenticated_source'})
 # A unique catalogue body-hash match gives coordinates without interpreting prose.
 for path,h in walk(c):
  if not ishash(h) or not path or path[-1] not in ['body_sha256','body_hash','function_sha256']:continue
  matches=[]
  for im in ims:
   cmp={'apollo_main:flash':'apollo-main','apollo_bootloader:flash':'apollo-bootloader','case:flash':'case','touch:flash':'touch'}.get(im['record']['id'])
   for cat in rows:
    if cmp==cat['component'] and cat['catalogue_body_sha256']==h:
     a=min(x for x,z in cat['ranges']);z=max(z for x,z in cat['ranges'])
     if digest(im['data'][a-im['base']:z-im['base']])==h:matches.append((im,cat))
  if len(matches)==1:
   im,cat=matches[0]
   for a,z in cat['ranges']:bound.append({'image':im['record']['id'],'range':[a,z],'body_sha256':h,'source_sha256':im['record']['content_sha256'],'mapping_method':'unique_catalogue_body_hash'})
 # A hashed body artifact is an explicit analysis footprint, not proof of full semantics.
 for name,h in filemap.items():
  bp=cp.parent/name
  if name.endswith('.bin') and any(t in name.lower() for t in ['body','code']) and bp.is_file() and digest(bp.read_bytes())==h:
   b=bp.read_bytes();matches=[]
   if not b:continue
   for im in ims:
    off=im['data'].find(b)
    if off>=0 and im['data'].find(b,off+1)<0:matches.append((im,off))
   if len(matches)==1:
    im,off=matches[0];bound.append({'image':im['record']['id'],'range':[off+im['base'],off+im['base']+len(b)],'body_sha256':h,'source_sha256':im['record']['content_sha256'],'mapping_method':'unique_hash_pinned_body_artifact','artifact':str(bp.relative_to(R))})
 for r in rr:
  if r['pass_scoped']:bound+=bind_specs(r['range_specs'],ims)
 # Last conservative route: verified address/bytes rows are evidence footprint only.
 for name,h in filemap.items():
  ip=cp.parent/name
  if not (name.endswith(('.json','.jsonl')) and any(t in name.lower() for t in ['instruction','disassembly']) and ip.is_file() and digest(ip.read_bytes())==h):continue
  try:ij=[json.loads(l) for l in ip.read_text().splitlines()] if name.endswith('.jsonl') else jread(ip)
  except Exception:continue
  inst=[]
  for path,d in walk(ij):
   if not isinstance(d,dict) or not isinstance(d.get('bytes'),str) or not ('mnemonic' in d or 'mn' in d):continue
   try:a=num(d.get('address',d.get('pc')));bb=bytes.fromhex(d['bytes'])
   except Exception:continue
   if not bb:continue
   matches=[]
   for im in ims:
    for x in {a,a+im['base']}:
     off=x-im['base']
     if off>=0 and im['data'][off:off+len(bb)]==bb:matches.append((im,x))
   if len(matches)==1:
    im,x=matches[0];inst.append((im['record']['id'],x,x+len(bb),im))
  for iid in {x[0] for x in inst}:
   im=next(x[3] for x in inst if x[0]==iid)
   for a,z in union([[x[1],x[2]] for x in inst if x[0]==iid]):bound.append({'image':iid,'range':[a,z],'body_sha256':digest(im['data'][a-im['base']:z-im['base']]),'source_sha256':im['record']['content_sha256'],'mapping_method':'pinned_instruction_evidence_footprint','artifact':str(ip.relative_to(R))})
 seen=set()
 for b in bound:
  key=(b['image'],*b['range'])
  if key in seen:continue
  seen.add(key);b['scoped_pass_reviews']=[r['review'] for r in rr if r['pass_scoped']];b['revision_reviews']=[r['review'] for r in rr if r['rejected_or_revision']];b['review_status']='scoped_pass' if b['scoped_pass_reviews'] and not b['revision_reviews'] else ('conflicting_or_revision' if b['revision_reviews'] else 'not_reviewed');rec['ranges'].append(b)
 rec['reason']='mapped_evidence_footprint' if rec['ranges'] else 'hash_bound_pseudocode_but_no_supported_range_binding';artifact.append(rec)
# The recent app-facing batches are analysis, not independently reviewed campaign work.
mainim=next(im for im in images.values() if im['record']['id']=='apollo_main:flash')
mainrows={num(r['entry']):r for r in rows if r['component']=='apollo-main'}
for vp in sorted((R/'g2/analysis').glob('*/validation.json')):
 v=jread(vp);ps=list(vp.parent.glob('*.pseudocode.c'))
 if not ps:continue
 ar={'receipt':str(vp.relative_to(R)),'receipt_sha256':digest(vp.read_bytes()),'pseudocode':[{'path':str(pp.relative_to(R)),'sha256':digest(pp.read_bytes()),'binding':'observed companion, not producer-pinned'} for pp in ps],'accepted':False,'reviews':[],'ranges':[],'reason':'app_batch_hash_bound_function_targets_not_independent_review'}
 for f in v.get('functions',[]):
  if not isinstance(f,dict):continue
  try:entry=num(f.get('entry',f.get('address')))
  except Exception:continue
  cat=mainrows.get(entry);h=f.get('sha256',f.get('body_sha256'))
  if not cat or not ishash(h):continue
  a=min(x for x,z in cat['ranges']);z=max(z for x,z in cat['ranges']);data=mainim['data'][a-mainim['base']:z-mainim['base']]
  if digest(data)!=h:continue
  for x,y in cat['ranges']:ar['ranges'].append({'image':'apollo_main:flash','range':[x,y],'body_sha256':h,'source_sha256':mainim['record']['content_sha256'],'mapping_method':'app_batch_function_target_association','scoped_pass_reviews':[],'revision_reviews':[],'review_status':'not_reviewed'})
 artifact.append(ar)
comp={'apollo_main:flash':'apollo-main','apollo_bootloader:flash':'apollo-bootloader','case:flash':'case','touch:flash':'touch'}
bycomp=collections.defaultdict(list)
for a in artifact:
 for b in a['ranges']:
  if b['image'] in comp:bycomp[comp[b['image']]].append((a,b))
summary={};intervals=[]
for cohort in sorted({r['cohort'] for r in rows}):
 rr=[r for r in rows if r['cohort']==cohort];den=union([s for r in rr for s in r['ranges']]);aa=bycomp[rr[0]['component']] if rr[0]['component']!='codec' else [(a,b) for a in artifact for b in a['ranges'] if codec_cohorts.get(b['image'])==cohort];exists=intersection(den,union([b['range'] for a,b in aa]));reviewed=intersection(den,union([b['range'] for a,b in aa if b['review_status']=='scoped_pass']));declared=intersection(den,union([b['range'] for a,b in aa if b['review_status']=='scoped_pass' and b['mapping_method']!='pinned_instruction_evidence_footprint']))
 summary[cohort]={'functions':len(rr),'catalogue_unique_bytes':length(den),'raw_available':sum(r['raw_available'] for r in rr),'analysis_evidence_footprint_bytes':length(exists),'scoped_pass_footprint_bytes':length(reviewed),'scoped_pass_declared_body_bytes':length(declared),'scoped_pass_footprint_percent':100*length(reviewed)/length(den),'canonical_accepted':0}
 for kind,rs in [('analysis_evidence',exists),('scoped_pass_evidence',reviewed),('scoped_pass_declared_body',declared)]:
  for a,z in rs:intervals.append({'cohort':cohort,'metric':kind,'range':[a,z]})
 for r in rr:
  r['analysis_overlap']=intersection(r['ranges'],exists);r['scoped_pass_overlap']=intersection(r['ranges'],reviewed);r['declared_body_review_overlap']=intersection(r['ranges'],declared);r['evidence_refs']=[{'receipt':a['receipt'],'receipt_sha256':a['receipt_sha256'],'range':b['range'],'review_status':b['review_status'],'review_refs':b['scoped_pass_reviews'],'method':b['mapping_method']} for a,b in aa if intersection(r['ranges'],[b['range']])]
  r['remaining_outside_scoped_evidence']=[]
  for a,z in r['ranges']:
   cursor=a
   for x,y in intersection([[a,z]],reviewed):
    if x>cursor:r['remaining_outside_scoped_evidence'].append([cursor,x])
    cursor=y
   if cursor<z:r['remaining_outside_scoped_evidence'].append([cursor,z])
image_footprints={}
for iid in sorted({b['image'] for a in artifact for b in a['ranges']}):
 bb=[b for a in artifact for b in a['ranges'] if b['image']==iid]
 image_footprints[iid]={'analysis_evidence_bytes':length([b['range'] for b in bb]),'scoped_pass_evidence_bytes':length([b['range'] for b in bb if b['review_status']=='scoped_pass'])}
result={'image_footprints':image_footprints,'scan_started_utc':start,'scan_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target_sha256':target['bundle']['sha256'],'summary':summary,'review_families':dict(families),'review_count':len(revs),'receipt_count':len(artifact),'receipt_outcomes':dict(collections.Counter(a['reason'] for a in artifact)),'review_bound_count':sum(bool(r['candidate_receipts']) for r in revs),'method_sha256':digest(Path(__file__).read_bytes()),'limits':['Evidence footprints are not semantic completion, full paths or all branches.','accepted:false does not erase scoped semantic review; canonical acceptance is separate.','Review footprints preserve prefix/stub/static limitations; body matching alone cannot promote them to whole-function analysis.','Only same exact candidate receipt is blocked by a rejecting/revise review; cross-version semantic supersession requires adjudication.','Case short coordinates are relocated only when exact stock bytes prove the interpretation.','Codec/ARC footprints may be authenticated but not matched to a comparable catalogue here; inspect artifact-ledger.','Catalogue denominator is not proven complete executable firmware.','This pass inventories all campaign review schema families, but nonstandard unresolved scopes are explicitly uncounted.']}
for name,v in [('function-ledger.jsonl',rows),('review-ledger.jsonl',revs),('artifact-ledger.jsonl',artifact),('nonoverlapping-intervals.jsonl',intervals),('remaining-outside-scoped-evidence.jsonl',[r for r in rows if r['remaining_outside_scoped_evidence']])]:
 (O/name).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in v))
(O/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
