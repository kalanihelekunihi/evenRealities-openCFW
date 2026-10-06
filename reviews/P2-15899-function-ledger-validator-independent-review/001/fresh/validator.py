from pathlib import Path
import json,hashlib,copy,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';raw=src.read_bytes();pin='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';assert h(raw)==pin
target=json.loads(Path('g2/workflow/target.json').read_text());targetpin='f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa';lockpin='7312f4b855ff41ec823cc977485a8cc5e59a7235f834880b2217bf1f3ab138ff';assert target['bundle']['sha256']==targetpin and h(Path('g2/workflow/target.json').read_bytes())==lockpin
class Rejected(Exception):pass
def require(condition,message):
 if not condition:raise Rejected(message)
def check(rows):
 ids=set();spans=[]
 for r in rows:
  require(r['image_id']=='apollo_main:flash' and r['component']=='apollo_main' and r['address_space']=='loaded' and r['isa_mode']=='Thumb','image identity')
  require(r['target_sha256']==targetpin and r['target_lock_sha256']==lockpin,'bundle target binding')
  require(r['path_root_kind']=='repository_relative_campaign' and r['path_root']==str(b),'path root')
  require(h((b/r['direct_input']['path']).read_bytes())==r['direct_input']['sha256'],'direct input hash')
  require(r['image_sha256']==pin,'image hash')
  require(r['accepted'] is False and r['status']=='draft_partial','draft status')
  require(r['stable_id']==f"apollo_main:flash:loaded:{r['entry']:08x}:Thumb",'stable identity')
  require(r['stable_id'] not in ids,'duplicate identity');ids.add(r['stable_id'])
  require(len(r['body_ranges'])==len(r['image_spans'])==1,'supported single-range scope')
  start,end=r['body_ranges'][0];off,z=r['image_spans'][0];require(start==r['entry'] and start<end and off==start-0x438000 and z==end-0x438000 and 0<=off<z<=len(raw),'address mapping')
  require(h(raw[off:z])==r['source_bytes_sha256'],'source span hash');spans.append((start,end))
  blobs={}
  for key in ['instructions','pseudocode']:
   p=b/r[key]['path'];v=p.read_bytes();require(h(v)==r[key]['sha256'],key+' hash');blobs[key]=v
  blocks=json.loads(blobs['instructions']);require(len(blocks)==1,'instruction block scope');block=blocks[0];require(block['start']==start and block['end']==end,'instruction extent');cursor=start;calls=[]
  for instruction in block['instructions']:
   v=bytes.fromhex(instruction['bytes']);require(v and instruction['address']==cursor,'instruction tiling');require(raw[cursor-0x438000:cursor-0x438000+len(v)]==v,'instruction source bytes');cursor+=len(v)
   if instruction['mnemonic'] in ['bl','blx']:
    m=re.match(r'([0-9a-f]{6,8})\b',instruction['operands']);calls.append((instruction['address'],int(m[1],16) if m else None))
  require(cursor==end,'instruction end');require(calls==[(x['call_site'],x['target']) for x in r['callees']],'call references')
 for left,right in zip(sorted(spans),sorted(spans)[1:]):require(left[1]<=right[0],'overlapping function ownership')
 return len(rows)
inputs=[b/'analysis/queue-candidate-ledger-16290/002/functions.jsonl',b/'analysis/clock-candidate-ledger-16294/002/functions.jsonl'];results=[]
for path in inputs:
 rows=[json.loads(x) for x in path.read_text().splitlines()];count=check(rows);negative=[]
 cases=[('bundle_hash',lambda r:r[0].update(target_sha256='0'*64)),('lock_hash',lambda r:r[0].update(target_lock_sha256='0'*64)),('path_root',lambda r:r[0].update(path_root='other/campaign')),('input_hash',lambda r:r[0]['direct_input'].update(sha256='0'*64)),('image_hash',lambda r:r[0].update(image_sha256='0'*64)),('identity',lambda r:r[0].update(image_id='apollo_bootloader:flash')),('entry',lambda r:r[0].update(entry=r[0]['entry']+2)),('mapping',lambda r:r[0]['image_spans'][0].__setitem__(0,r[0]['image_spans'][0][0]+2)),('source_hash',lambda r:r[0].update(source_bytes_sha256='0'*64)),('pseudocode_hash',lambda r:r[0]['pseudocode'].update(sha256='0'*64)),('instruction_hash',lambda r:r[0]['instructions'].update(sha256='0'*64)),('duplicate',lambda r:r.append(copy.deepcopy(r[0]))),('admission_flag',lambda r:r[0].update(accepted=True))]
 for name,mutate in cases:
  candidate=copy.deepcopy(rows);mutate(candidate)
  try:check(candidate)
  except Rejected as error:negative.append(dict(case=name,rejected=str(error)))
  else:raise AssertionError('accepted malformed '+name)
 results.append(dict(path=str(path.relative_to(b)),sha256=h(path.read_bytes()),functions_verified=count,negative_cases=negative))
o=Path('reviews/P2-15899-function-ledger-validator-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'validator.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='diagnostic',image_sha256=pin,results=results,limitations=['Single-range Apollo main Thumb draft schema only','Byte/evidence consistency not decoder or semantic correctness','No independent review binding physical contracts full corpus coverage admission or gates']),indent=2)+'\n');print('PASS20 records26 rejectioncases')
