from pathlib import Path
import json,hashlib,copy
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();data=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(data)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';target='f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa';lock='7312f4b855ff41ec823cc977485a8cc5e59a7235f834880b2217bf1f3ab138ff'
class Rejected(Exception):pass
def need(v,label):
 if not v:raise Rejected(label)
def check(rows):
 seen=set();spans=[]
 for r in rows:
  need(r['image_id']=='apollo_main:flash','image identity');need(r['target_sha256']==target and r['target_lock_sha256']==lock,'locked target');need(r['accepted'] is False and r['status']=='draft_partial','draft status');need(r['path_root']==str(b) and r['path_root_kind']=='repository_relative_campaign','path root');need(h((b/r['direct_input']['path']).read_bytes())==r['direct_input']['sha256'],'predecessor hash');need(r['stable_id'] not in seen,'duplicate identity');seen.add(r['stable_id']);need(len(r['ranges'])==len(r['image_spans'])==1,'single range');a,z=r['ranges'][0];off,end=r['image_spans'][0];need(a<z and off==a-0x438000 and end==z-0x438000 and 0<=off<end<=len(data),'address mapping');raw=data[off:end];need(h(raw)==r['source_bytes_sha256'],'source span hash');spans.append((a,z))
  if 'value_evidence' in r:
   ev=r['value_evidence'];p=b/ev['path'];need(h(p.read_bytes())==ev['sha256'],'value evidence hash');table=json.loads(p.read_text());need(len(table)==12 and z-a==480,'table dimensions');cursor=a
   for row in table:
    rb=bytes.fromhex(row['raw']);need(row['address']==cursor and len(rb)==40,'table tiling');need(rb==data[cursor-0x438000:cursor-0x438000+40],'table raw bytes');need(row['words']==[int.from_bytes(rb[j:j+4],'little') for j in range(0,40,4)],'table U32 values');cursor+=40
   need(cursor==z,'table end')
  else:
   need(len(raw)==4 and r['raw_hex']==raw.hex() and r['value_u32']==int.from_bytes(raw,'little'),'literal value')
   for consumer in r['candidate_consumers']:
    refs=json.loads((b/consumer/'references.json').read_text());need(any(x.get('address')==a for x in refs),'literal reference')
 for left,right in zip(sorted(spans),sorted(spans)[1:]):need(left[1]<=right[0],'data ownership overlap')
 return sum(z-a for a,z in spans)
paths=[b/'analysis/queue-candidate-ledger-16290/002/data.jsonl',b/'analysis/clock-candidate-ledger-16294/002/data.jsonl'];results=[]
for p in paths:
 rows=[json.loads(x) for x in p.read_text().splitlines()];total=check(rows);mutations=[('target',lambda r:r[0].update(target_sha256='0'*64)),('spanhash',lambda r:r[0].update(source_bytes_sha256='0'*64)),('mapping',lambda r:r[0]['image_spans'][0].__setitem__(0,r[0]['image_spans'][0][0]+1)),('duplicate',lambda r:r.append(copy.deepcopy(r[0]))),('admission',lambda r:r[0].update(accepted=True))]
 if 'value_evidence' in rows[0]:mutations.append(('tablepin',lambda r:r[0]['value_evidence'].update(sha256='0'*64)))
 else:mutations.extend([('literalvalue',lambda r:r[0].update(value_u32=r[0]['value_u32']^1)),('rawvalue',lambda r:r[0].update(raw_hex='00'*4))])
 negatives=[]
 for name,mutate in mutations:
  candidate=copy.deepcopy(rows);mutate(candidate)
  try:check(candidate)
  except Rejected as e:negatives.append(dict(case=name,rejected=str(e)))
  else:raise AssertionError(name)
 results.append(dict(path=str(p.relative_to(b)),sha256=h(p.read_bytes()),records=len(rows),bytes_checked=total,negative_cases=negatives))
o=Path('reviews/P2-15901-data-ledger-validator-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'validator.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='diagnostic',results=results,limitations=['Exact-value evidence consistency only; no global noncode ownership or reviewadmission','Consumer references are discovery leads not reachability proof','No C freeze gates']),indent=2)+'\n');print('PASS7 datarecords504bytes13rejections')
