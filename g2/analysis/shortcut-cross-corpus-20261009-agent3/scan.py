"""Finite registered-corpus scan; all writes stay beside this script."""
from pathlib import Path
import hashlib, json, re, struct, subprocess, collections, time, sys
OUT=Path(__file__).resolve().parent
ARC2='--arc2-only' in sys.argv
ROOT=OUT.parents[2]
CAMP=ROOT/'g2/build/pseudocode-first/20260930T190500Z'
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,x): (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
target=json.loads((ROOT/'g2/workflow/target.json').read_text())
auth=[]
for r in target['components']:
 b=(ROOT/r['local_payload_path']).read_bytes()
 assert len(b)==r['size'] and sha(b)==r['sha256']
 auth.append(dict(id=r['id'],path=r['local_payload_path'],sha256=sha(b),size=len(b)))
images=[]; seen=set()
for p in [CAMP/'inventory/images.jsonl',CAMP/'reviews/codec-canonical-images-003/images.candidate.jsonl']:
 for r in rows(p):
  q=Path(r['content_path']); q=q if q.is_absolute() else ROOT/q
  if not q.exists(): continue
  b=q.read_bytes(); assert sha(b)==r['content_sha256'],str(q)
  if sha(b) in seen: continue
  seen.add(sha(b)); images.append((r,b))
save('authentication.json',{'target':target['bundle']['sha256'],'payloads':auth,'images':[{'id':r['id'],'sha256':sha(b),'size':len(b),'path':r['content_path'],'mappings':r.get('address_spaces',[])} for r,b in images]})
# The canonical byte images are the oracle. Historical body catalogues are only ranking metadata.
ledger=rows(ROOT/'g2/analysis/rescan-2026-10-06T140235Z/function-ledger.jsonl')
def metadata(r,offset,size):
 result=[]
 for space in r.get('address_spaces',[]):
  for m in space.get('mappings',[]):
   if m['image_start']<=offset and offset+size<=m['image_end']:
    addr=m['loaded_start']+offset-m['image_start']
    comp=r['payload_id'].replace('_','-')
    for body in ledger:
     if body['component']==comp and any(a<=addr<aend for a,aend in body['ranges']):
      result.append({'entry':body['entry'],'name':body.get('name'),'scoped_pass':bool(body.get('scoped_pass_overlap')),'canonical_accepted':body['canonical_accepted']})
    return addr,result
 return None,result
def members(b):
 if not b.startswith(b'!<arch>\n'): yield '',b; return
 off=8; names=b''
 while off+60<=len(b):
  h=b[off:off+60]; n=int(h[48:58]); name=h[:16].decode().strip(); data=b[off+60:off+60+n]; off+=60+n+(n&1)
  if name=='//': names=data; continue
  if name.startswith('#1/'):
   k=int(name[3:]); name=data[:k].decode(errors='replace'); data=data[k:]
  elif name.startswith('/') and name[1:].isdigit():
   k=int(name[1:]); name=names[k:].split(b'/\n')[0].decode(errors='replace')
  if data.startswith(b'\x7fELF'): yield name.rstrip('/'),data
def funcs(b):
 if b[:6]!=b'\x7fELF\x01\x01': return
 machine=struct.unpack_from('<H',b,18)[0]
 if machine not in ((195,) if ARC2 else (40,45,93,195,252)): return
 off=struct.unpack_from('<I',b,32)[0]; ent,n,st=struct.unpack_from('<HHH',b,46)
 ss=[struct.unpack_from('<10I',b,off+i*ent) for i in range(n)]
 rel={}
 for s in ss:
  if s[1] in (4,9) and s[9]:
   rel.setdefault(s[7],[]).extend(struct.unpack_from('<II',b,s[4]+j*s[9]) for j in range(s[5]//s[9]))
 for s in ss:
  if s[1]!=2 or not s[9]: continue
  strings=ss[s[6]]; names=b[strings[4]:strings[4]+strings[5]]
  for j in range(s[5]//s[9]):
   name,val,size,info,other,idx=struct.unpack_from('<IIIBBH',b,s[4]+j*s[9])
   if info&15!=2 or idx>=len(ss) or size<24 or not(ss[idx][2]&4): continue
   sec=ss[idx]; start=(val&~1)-sec[3]
   if start<0 or start+size>sec[5]: continue
   code=b[sec[4]+start:sec[4]+start+size]
   rr=[(x-start,i&255) for x,i in rel.get(idx,[]) if start<=x<start+size]
   yield machine,names[name:].split(b'\0')[0].decode(errors='replace'),code,rr
paths=subprocess.check_output(['rg','--files','-uu','third-party'],cwd=ROOT,text=True).splitlines()
paths=[p for p in paths if '/.git/' not in p and p.endswith(('.a','.o','.elf','.axf','.c','.h','.cpp','.cc','.S','.s'))]
binary=[p for p in paths if p.endswith(('.a','.o','.elf','.axf'))]
sources=[p for p in paths if p not in set(binary)]
save('scope.json',{'binary_files':binary,'source_files':sources,'minimum_function_size':24,'machines':[40,45,93,195,252],'limitations':['ELF32 little endian sized STT_FUNC only; no executable blob attribution from arbitrary byte windows','Source strings are lexical anchors, not source production identity','C-SKY relocation masks only known types 1 and 19; masked matches are candidates until target-call validation','Historical catalogues used only for ranking; no admission or complete body proof']})
matches=[r for r in json.loads((OUT/'function-matches.json').read_text()) if r['machine']!=195] if ARC2 else []
counters=collections.Counter(); fingerprints=set(); artifacts=[]
t=time.time()
for p in binary:
 b=(ROOT/p).read_bytes(); artifacts.append({'path':p,'sha256':sha(b),'size':len(b)})
 try:
  for member,obj in members(b):
   counters['elf_members']+=1
   for machine,name,code,rr in funcs(obj):
    counters['sized_functions']+=1
    key=(machine,sha(code),tuple(rr))
    if key in fingerprints: counters['duplicate_functions']+=1; continue
    fingerprints.add(key)
    # Masking is deliberately restricted to previously independently decoded C-SKY formats.
    mask=set()
    if machine==252 and all(typ in (1,19) for pos,typ in rr):
     for pos,typ in rr: mask.update(range(pos,min(pos+4,len(code))))
    spans=[]; start=None
    for j in range(len(code)+1):
     if j<len(code) and j not in mask:
      if start is None: start=j
     elif start is not None: spans.append((start,j)); start=None
    a,z=max(spans,key=lambda x:x[1]-x[0],default=(0,0))
    if z-a<24: counters['short_anchor_rejected']+=1; continue
    if len(set(code[a:z]))<5: counters['low_entropy_rejected']+=1; continue
    needle=code[a:z]
    for image,stock in images:
     pos=stock.find(needle)
     while pos!=-1:
      at=pos-a
      if at>=0 and at+len(code)<=len(stock) and all(stock[at+x:at+y]==code[x:y] for x,y in spans):
       exact=stock[at:at+len(code)]==code
       addr,bodies=metadata(image,at,len(code))
       matches.append({'provider':p,'provider_sha256':sha(b),'member':member,'machine':machine,'symbol':name,'bytes':len(code),'function_sha256':sha(code),'image':image['id'],'image_sha256':sha(stock),'image_offset':at,'runtime':addr,'class':'exact_bytes' if exact else 'relocation_mask_candidate','relocations':rr,'masked_bytes':len(mask),'catalogue_overlaps':bodies})
      pos=stock.find(needle,pos+1)
 except (ValueError,IndexError,struct.error) as e: counters['parser_rejected']+=1
 if len(artifacts)%100==0: print('binary',len(artifacts),'matches',len(matches),'seconds',round(time.time()-t),flush=True)
save('binary-artifacts.json',artifacts); save('function-matches.json',matches)
if ARC2:
 arcrows=[x for x in matches if x['machine']==195]
 save('arc2-summary.json',{'scope':'historical ARCv2-only supplement; counts and matches exclude other architectures','counts':dict(counters),'matches':len(arcrows),'match_classes':dict(collections.Counter(x['class'] for x in arcrows)),'combined_matches_after_supplement':len(matches),'combined_match_classes_after_supplement':dict(collections.Counter(x['class'] for x in matches)),'elapsed_seconds':time.time()-t})
 print('ARC2 supplementation finished',len(matches),flush=True)
 sys.exit(0)
stockstrings={}
for r,b in images:
 for m in re.finditer(rb'[ -~]{24,}',b):
  raw=m.group(); stockstrings.setdefault(raw,[]).append({'image':r['id'],'offset':m.start()})
anchors=[]; literal=re.compile(rb'"((?:[^"\\\n]|\\.){24,})"')
for p in sources:
 b=(ROOT/p).read_bytes(); counters['source_files']+=1
 for m in literal.finditer(b):
  raw=m.group(1)
  # Decode only common harmless C escapes. Full lexical payload remains in evidence.
  value=raw.replace(b'\\n',b'\n').replace(b'\\r',b'\r').replace(b'\\t',b'\t').replace(b'\\"',b'"').replace(b'\\\\',b'\\')
  if value in stockstrings:
   anchors.append({'provider':p,'provider_sha256':sha(b),'line':b[:m.start()].count(b'\n')+1,'literal':value.decode(errors='replace'),'hits':stockstrings[value]})
save('string-anchors.json',anchors)
save('summary.json',{'counts':dict(counters),'images':len(images),'matches':len(matches),'match_classes':dict(collections.Counter(x['class'] for x in matches)),'string_anchors':len(anchors),'elapsed_seconds':time.time()-t})
print(json.dumps(json.loads((OUT/'summary.json').read_text())),flush=True)
