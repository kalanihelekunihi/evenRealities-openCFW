from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,subprocess
b=Path('g2/build/pseudocode-first/20260930T190500Z');root=b/'analysis';h=lambda x:hashlib.sha256(x).hexdigest();ip=b/'inventory/images.jsonl';iraw=ip.read_bytes();images=[json.loads(x) for x in iraw.splitlines() if x.strip()];spaces=[];imagepins=[]
for im in images:
 p=Path(im['content_path']);d=p.read_bytes();assert h(d)==im['content_sha256'] and len(d)==im['size'];imagepins.append(dict(id=im['id'],path=str(p),sha256=h(d),size=len(d)))
 for space in im['address_spaces']:spaces.append((im['id'],space['id'],space['mappings'],d))
 for route in im.get('mapping_model',{}).get('routes',[]):
  ex=route.get('expected_execution') or {};span=ex.get('span');ims=ex.get('image_span')
  if isinstance(span,list) and isinstance(ims,list) and len(span)==len(ims)==2 and all(isinstance(x,int) for x in span+ims) and span[1]-span[0]==ims[1]-ims[0]:
   spaces.append((im['id'],'conditional-route:'+route['route_id'],[dict(image_start=ims[0],image_end=ims[1],loaded_start=span[0],loaded_end=span[1])],d))
paths=sorted(Path(x) for x in subprocess.check_output(['rg','--files',str(root),'-g','instructions.json'],text=True).splitlines());records=[];excluded=[];totals=Counter();ambiguous=0
for p in paths:
 raw=p.read_bytes()
 try:
  obj=json.loads(raw)
  if isinstance(obj,dict) and obj.get('operation')=='BX LR' and isinstance(obj.get('entries'),list):
   begin=obj['start'];end=obj['end'];buf=bytes.fromhex(obj['bytes']);assert end-begin==len(buf) and obj['entries']==list(range(begin,end,2)) and buf==b'\x70\x47'*len(obj['entries']);obj=[{'instructions':[dict(address=a,bytes='7047') for a in obj['entries']]}]
  if isinstance(obj,dict) and isinstance(obj.get('regions'),list):obj=obj['regions']
  if isinstance(obj,dict) and isinstance(obj.get('instructions'),list):obj=[obj]
  if not isinstance(obj,list):raise ValueError('unsupported top level')
  if obj and all(isinstance(x,dict) and ('address' in x or 'pc' in x) for x in obj):obj=[{'instructions':obj}]
  rows=[]
  for block in obj:
   if not isinstance(block,dict) or not isinstance(block.get('instructions'),list):raise ValueError('unsupported block shape')
   for row in block['instructions']:
    addr=row.get('address',row.get('pc'));addr=int(addr,0) if isinstance(addr,str) else addr
    field=next((k for k in ['source_bytes_hex','source_bytes','bytes_hex','bytes','encoding'] if k in row),None)
    if field is None:raise ValueError('no supported byte field')
    value=row[field];value=''.join(value) if isinstance(value,list) else value;v=bytes.fromhex(value);assert v;rows.append((addr,v))
  if not rows:raise ValueError('empty instruction list')
  matches=[]
  for image,space,mm,data in spaces:
   variants=['as_recorded','each_halfword_byte_swapped'] if all(len(v)%2==0 for addr,v in rows) else ['as_recorded']
   matched_variants=set()
   for variant in variants:
    offsets=[];encoded=[]
    for addr,rawbytes in rows:
     v=rawbytes if variant=='as_recorded' else b''.join(rawbytes[j:j+2][::-1] for j in range(0,len(rawbytes),2))
     possible=[m['image_start']+addr-m['loaded_start'] for m in mm if m['loaded_start']<=addr and addr+len(v)<=m['loaded_end']]
     valid=[off for off in possible if data[off:off+len(v)]==v]
     if len(valid)!=1:break
     offsets.append([valid[0],valid[0]+len(v)]);encoded.append(v)
    else:
     key=b''.join(encoded)
     if key not in matched_variants:matches.append(dict(image_id=image,address_space_id=space,recorded_byte_interpretation=variant,image_spans=offsets));totals[image]+=1;matched_variants.add(key)
  if not matches:raise ValueError('no whole-file candidate image byte match')
  if len(matches)>1:ambiguous+=1
  pseudo=p.parent/'pseudocode.md';records.append(dict(path=str(p),sha256=h(raw),pseudocode_path=str(pseudo) if pseudo.exists() else None,pseudocode_sha256=h(pseudo.read_bytes()) if pseudo.exists() else None,candidate_matches=matches,qualification='candidate byte match only; no ownership or semantics admission'))
 except (ValueError,KeyError,TypeError,AssertionError) as e:excluded.append(dict(path=str(p),sha256=h(raw),reason=str(e) or 'empty raw instruction bytes'))
o=Path('reviews/P2-15883-private-image-index-compact-record-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'index.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records));(o/'excluded.json').write_text(json.dumps(excluded,indent=2)+'\n');(o/'conditional-route-models.json').write_text(json.dumps([dict(image_id=im['id'],mapping_model=im['mapping_model']) for im in images if 'mapping_model' in im],indent=2)+'\n');(o/'images.json').write_text(json.dumps(imagepins,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());result=dict(accepted=False,status='diagnostic',inventory_sha256=h(iraw),images=len(images),instruction_files=len(paths),matched_files=len(records),ambiguous_files=ambiguous,excluded_files=len(excluded),candidate_file_counts_by_image=dict(totals),excluded_reasons=dict(Counter(x['reason'] for x in excluded)),limitations=['Supported instructionJSON formats/bytefields and two explicit byte-order hypotheses only; no ISA decode validation; allrevisions retained','Byte matching candidate ownership is not authoritative ownership; conditional-route candidates retain full model and do not establish guard satisfaction','Counts overlap images/revisions and cannot be summed as coverage','No pseudocode review or architectural validity proven by bytes','No canonical admission freeze gates']);(o/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
