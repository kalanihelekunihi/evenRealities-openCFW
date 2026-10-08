from pathlib import Path
import json,hashlib,copy
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists());HERE=Path(__file__).resolve().parent

def validate_partitions(rows):
 groups={}
 for r in rows:
  a,z=r['range'];assert 0<=a<z and r['bytes']==z-a;groups.setdefault((r['context'],r['payload']),[]).append(r)
 for rs in groups.values():
  rs.sort(key=lambda r:r['range'][0]);assert rs[0]['range'][0]==0
  assert all(a['range'][1]==b['range'][0] for a,b in zip(rs,rs[1:]))

def validate_contracts(rows):
 for r in rows:assert r['bytes']==0 and r['extent'] is None

rows=[json.loads(s) for s in (HERE/'address-ledger.jsonl').read_text().splitlines()];contracts=json.loads((HERE/'call-contracts.json').read_text());validate_partitions(rows);validate_contracts(contracts)
for r in json.loads((HERE/'mapped-functions.json').read_text()):
 for pathfield,hashfield in [('source_path','source_sha256'),('object_path','object_sha256')]:assert hashlib.sha256((ROOT/r[pathfield]).read_bytes()).hexdigest()==r[hashfield]
 # Authenticated original-coordinate mapping, never a linked-size denominator.
 b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();a,z=r['range'];assert hashlib.sha256(b[a:z]).hexdigest()==r['sha256']
 assert r['original_address_start']==0x410000+a and r['original_address_end']==0x410000+z
mapped=json.loads((HERE/'mapped-functions.json').read_text());summary=json.loads((HERE/'validation.json').read_text());assert len(mapped)==20 and sum(r['bytes'] for r in mapped)==summary['source_defined_mapped_bytes']==4932
for r in mapped:
 if 'validation_receipt' in r:
  receipt=ROOT/r['validation_receipt'];assert hashlib.sha256(receipt.read_bytes()).hexdigest()==r['validation_receipt_sha256'];j=json.loads(receipt.read_text());assert j['status'].startswith('PASS') and j['candidate_sha256']==r['candidate_sha256']
negative=[]
def reject(name,fn,data):
 try:fn(data)
 except AssertionError:negative.append(name);return
 raise AssertionError('accepted invalid ledger: '+name)
x=copy.deepcopy(rows);x[1]['range'][0]+=1;reject('gap_or_overlap',validate_partitions,x)
x=copy.deepcopy(rows);x[0]['bytes']+=1;reject('false_byte_denominator',validate_partitions,x)
x=copy.deepcopy(contracts);x[0]['bytes']=218;reject('reference_counted_as_embedded_code',validate_contracts,x)
x=copy.deepcopy(contracts);x[-1]['extent']=[0,1];reject('modeled_call_invented_extent',validate_contracts,x)
print(json.dumps(dict(status='PASS',mapped_functions=len(json.loads((HERE/'mapped-functions.json').read_text())),negative_tests=negative)))
