from pathlib import Path
import json,hashlib,collections,sys,re,datetime
R=Path('/Users/kalani/Repo/evenRealities-openCFW');P=R/'g2/build/pseudocode-first/20260930T190500Z'
def sha(b):return hashlib.sha256(b).hexdigest()
def lines(p):return list(map(json.loads,p.read_text().splitlines()))
def walk(x):
 yield x
 if isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def union(rs):
 out=[]
 for a,z in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],z)
  else:out.append([a,z])
 return out
def length(rs):return sum(z-a for a,z in union(rs))
def match(a,b,ims):
 found=set()
 for i,im in ims.items():
  for x in {a,a+im['base']}:
   off=x-im['base']
   if off>=0 and im['data'][off:off+len(b)]==b:found.add((i,x,x+len(b)))
 return next(iter(found)) if len(found)==1 else None

def fixture():
 im={'a':{'base':100,'data':b'abcdef'}}
 assert match(101,b'bc',im)==('a',101,103)
 assert match(101,b'XX',im) is None
 assert match(101,b'bc',{**im,'b':im['a']}) is None
 assert match(999,b'bc',im) is None
 assert length([[1,4],[1,4],[3,6]])==5
 return 5

records=lines(P/'inventory/images.jsonl');meta={x['id']:x for x in records};images={}
for x in records:
 path=Path(x['content_path']);path=path if path.is_absolute() else R/path;data=path.read_bytes();assert sha(data)==x['content_sha256'];maps=[m for s in x.get('address_spaces',[]) for m in s.get('mappings',[]) if 'loaded_start' in m and 'image_start' in m];base=maps[0]['loaded_start']-maps[0]['image_start'] if len(maps)==1 else 0
 images[x['id']]={'base':base,'data':data,'sha256':x['content_sha256']}
for p in (R/'g2/research/corpus/codec/ghidra/open-2026-09-29').glob('*/RUN.json'):
 run=json.loads(p.read_text())
 for im in images.values():
  if im['sha256']==run['image_sha256']:im['base']=int(run['base'],0)
def offset(i):
 im=meta[i];assert im['transform']['kind']=='identity';a,z=im['source_span'];assert z-a==im['size'];return a+(offset(im['parent_image_id']) if im.get('parent_image_id') else 0)
def scan(snapshot,dest):
 ranges=collections.defaultdict(list);ledger=[];outcomes=collections.Counter();seen=set();manifest=[]
 for art in lines(snapshot/'artifact-ledger.jsonl'):
  rp=R/art['receipt']
  if not rp.is_file() or sha(rp.read_bytes())!=art['receipt_sha256']:outcomes['receipt_hash_mismatch']+=1;continue
  receipt=json.loads(rp.read_text());strings={s for s in walk(receipt) if isinstance(s,str)};ims={i:im for i,im in images.items() if im['sha256'] in strings};files=receipt.get('files',{})
  if not isinstance(files,dict):outcomes['unsupported_file_manifest_schema']+=1;continue
  for name,h in files.items():
   if not isinstance(h,str) or not name.endswith(('.json','.jsonl')) or not any(t in name.lower() for t in ['instruction','disassembly']):continue
   fp=rp.parent/name
   if not fp.is_file() or sha(fp.read_bytes())!=h:outcomes['instruction_artifact_hash_mismatch']+=1;continue
   key=(str(fp.relative_to(R)),h)
   if key in seen:continue
   seen.add(key);manifest.append({'path':key[0],'sha256':h,'bytes':fp.stat().st_size,'mtime_ns':fp.stat().st_mtime_ns,'receipt':art['receipt'],'receipt_sha256':art['receipt_sha256']})
   if not ims:outcomes['no_authenticated_source_image']+=1;continue
   try:j=[json.loads(s) for s in fp.read_text().splitlines()] if name.endswith('.jsonl') else json.loads(fp.read_text())
   except Exception:outcomes['unparseable_instruction_artifact']+=1;continue
   for v in walk(j):
    if not isinstance(v,dict) or not isinstance(v.get('bytes'),str) or not ('mnemonic' in v or 'mn' in v):continue
    try:a=v.get('address',v.get('pc'));a=int(a,0) if isinstance(a,str) else int(a);bb=bytes.fromhex(v['bytes'])
    except Exception:outcomes['malformed_instruction_row']+=1;continue
    mn=v.get('mnemonic',v.get('mn',''))
    if not bb or not mn or mn.startswith('.') or mn in ['(bad)','???','invalid']:outcomes['data_or_invalid_decode_row']+=1;continue
    matched=match(a,bb,ims)
    if not matched:outcomes['wrong_or_ambiguous_instruction_bytes']+=1;continue
    iid,a,z=matched
    try:o=offset(iid)
    except AssertionError:outcomes['nonidentity_source_projection']+=1;continue
    pa=a-images[iid]['base']+o;pz=z-images[iid]['base']+o;pay=meta[iid]['payload_id'];ranges[pay].append([pa,pz]);ledger.append({'payload':pay,'image':iid,'payload_range':[pa,pz],'instruction_range':[a,z],'bytes_sha256':sha(bb),'image_sha256':images[iid]['sha256'],'artifact':key[0],'artifact_sha256':h});outcomes['matched_instruction_rows']+=1
 dest.mkdir(exist_ok=True);(dest/'instruction-ledger.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ledger));(dest/'instruction-artifact-manifest.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in manifest));counts={p:length(r) for p,r in ranges.items()};n=4301227;result={'snapshot':str(snapshot),'measured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipt_pinned_json_instruction_bytes':sum(counts.values()),'per_payload':counts,'outcomes':dict(outcomes),'artifact_count':len(manifest),'percent':100*sum(counts.values())/n,'limits':['Existing instruction exports only; no new disassembly generated.','Source-byte matching authenticates instruction rows, not code/data classification or decoder semantics.','Includes ignored generated campaign paths, independent of git status.','Only receipt-pinned instruction/disassembly JSON formats counted; unpinned/text exports have separate limits.']};(dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return result,ranges
if __name__=='__main__':
 assert fixture()==5
 out=Path(sys.argv[1]);a=json.loads((Path('/Users/kalani/Documents/Codex/OpenCFW/audits/2026-10-05T0013Z-status/instruction-metrics.json')).read_text())['current_receipt_pinned_json'];b,br=scan(out,out/'instructions-current')
 # The standalone ARC export is authenticated now; no baseline file pin was saved.
 p=R/'g2/research/corpus/em9305/objdump/open-2026-09-29';obj=p/'em9305-0x302400-0x335BC8.s';pins={name:h for h,name in (s.split(None,1) for s in (p/'SHA256SUMS').read_text().splitlines())};assert sha(obj.read_bytes())==pins[obj.name] and sha((p/'RUN.json').read_bytes())==pins['RUN.json'];im=images['ble_em9305:record-3'];arc=[];outcomes=collections.Counter()
 for line in obj.read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\s*([0-9a-f ]+)\t+([^\s]+)',line)
  if not m:continue
  a0=int(m[1],16);tokens=m[2].split();mn=m[3]
  if mn.startswith('.') or mn in ['(bad)','???','invalid']:outcomes['data_or_invalid_decode']+=1;continue
  try:bb=b''.join(bytes.fromhex(t)[::-1] for t in tokens)
  except ValueError:outcomes['invalid_bytes']+=1;continue
  z=match(a0,bb,{'ble_em9305:record-3':im})
  if not z:outcomes['unmatched_bytes']+=1;continue
  iid,a0,z0=z;o=offset(iid);arc.append([a0-im['base']+o,z0-im['base']+o]);outcomes['matched_rows']+=1
 combined={k:union(v) for k,v in br.items()};combined['ble_em9305']=union(combined.get('ble_em9305',[])+arc)
 counts={k:length(v) for k,v in combined.items()};result={'baseline_receipt_pinned_json':a,'current_receipt_pinned_json':b,'comparable_json_delta_bytes':b['receipt_pinned_json_instruction_bytes']-a['receipt_pinned_json_instruction_bytes'],'current_arc_text_export':{'path':str(obj.relative_to(R)),'sha256':sha(obj.read_bytes()),'source_sha256':im['sha256'],'matched_bytes':length(arc),'outcomes':dict(outcomes),'baseline_comparison':'Unavailable: prior audit did not capture standalone text export hash; not counted as newly generated.'},'current_combined_instruction_export_bytes':sum(counts.values()),'per_payload_current_combined':counts,'bundle_bytes':4301227,'current_combined_percent':100*sum(counts.values())/4301227,'fixtures_passed':5}
 (out/'instruction-metrics.json').write_text(json.dumps(result,indent=2)+'\n');(out/'instruction-payload-intervals.jsonl').write_text(''.join(json.dumps({'payload':k,'range':v})+'\n' for k,vs in combined.items() for v in vs));print(json.dumps(result,indent=2))
