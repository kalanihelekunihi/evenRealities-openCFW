from pathlib import Path
import json,hashlib,copy
O=Path(__file__).resolve().parent;R=next(p for p in O.parents if (p/'AGENTS.md').exists());H=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest();blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
def check(rows):
 assert len(rows)==29 and sum(r['bytes'] for r in rows)==8574
 ordered=sorted(rows,key=lambda r:r['range']);assert all(a['range'][1]<=z['range'][0] for a,z in zip(ordered,ordered[1:]))
 for r in rows:
  a,z=r['range'];assert r['bytes']==z-a and r['sha256']==hashlib.sha256(blob[a:z]).hexdigest();assert H(r['source_path'])==r['source_sha256'];assert H(r['object_path'])==r['object_sha256']
  for p in r.get('supporting_sources',[])+r.get('supporting_objects',[]):assert H(p['path'])==p['sha256']
  if 'validation_receipt' in r:assert H(r['validation_receipt'])==r['validation_receipt_sha256']
rows=json.loads((O/'mapped-functions.json').read_text());check(rows)
for kind in ['false-byte-count','overlap','source-hash']:
 m=copy.deepcopy(rows)
 if kind=='false-byte-count':m[-1]['bytes']+=1
 elif kind=='overlap':m[-1]['range']=m[-2]['range'][:]
 else:m[-1]['source_sha256']='0'*64
 try:check(m)
 except AssertionError:pass
 else:raise AssertionError(('negative control accepted',kind))
parts=[json.loads(x) for x in (O/'address-ledger.jsonl').read_text().splitlines()]
for context,payload in {(r['context'],r['payload']) for r in parts}:
 rs=sorted([r for r in parts if (r['context'],r['payload'])==(context,payload)],key=lambda r:r['range']);assert rs[0]['range'][0]==0 and all(a['range'][1]==b['range'][0] for a,b in zip(rs,rs[1:]));assert all(r['bytes']==r['range'][1]-r['range'][0] for r in rs)
contracts=json.loads((O/'call-contracts.json').read_text());assert all(r['bytes']==0 and r['extent'] is None for r in contracts)
print('PASS29mapped bodies8574B, exact identities, contiguous partitions,3 rejected controls')
