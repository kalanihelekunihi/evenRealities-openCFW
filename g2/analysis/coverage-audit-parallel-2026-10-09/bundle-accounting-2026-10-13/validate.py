from pathlib import Path
import json,hashlib,struct,gzip,base64
R=Path.cwd();O=Path(__file__).parent;F=json.loads((O/'full-v3.json').read_text());C=json.loads((O/'compact-v3.json').read_text());T=json.loads((O/'compact-v3-transport.json').read_text());E=json.loads((O/'compact-v3-packed.json').read_text());B=(R/F['bundle']['filename']).read_bytes();assert len(B)==F['bundle']['bytes'] and hashlib.sha256(B).hexdigest()==F['bundle']['sha256'];cats=F['bundle']['categories'];total={k:0 for k in cats};cursor=0
for a,b,i in F['bundle']['exclusiveRuns']:
 assert a==cursor and b>a and b<=len(B);total[cats[i]]+=b-a;cursor=b
assert cursor==len(B) and total==F['bundle']['exclusiveTotals'] and sum(total.values())==len(B)
for ci in F['componentsExclusive']:
 seg=next(s for s in F['bundle']['segments'] if s.get('component')==ci['component']);data=B[seg['range'][0]:seg['range'][1]];assert len(data)==ci['bytes'] and hashlib.sha256(data).hexdigest()==seg['sha256'];counts={k:0 for k in cats};cursor=0
 for a,b,i in ci['runs']:assert a==cursor and b>a;counts[cats[i]]+=b-a;cursor=b
 assert cursor==ci['bytes'] and counts==ci['totals']
for x in F['orthogonalResourceEvidence']:
 seg=next(s for s in F['bundle']['segments'] if s.get('component')==x['component']);a,b=x['payloadRange'];assert hashlib.sha256(B[seg['range'][0]+a:seg['range'][0]+b]).hexdigest()==x['sha256']
for raw,encoded in zip(C['components'],T['components']):
 for field in ['runs','exclusiveRuns']:
  cursor=0;decoded=[]
  for n,k in encoded[field]:assert n>0;decoded.append([cursor,cursor+n,k]);cursor+=n
  assert decoded==raw[field] and cursor==raw['payloadBytes']
p=gzip.decompress(base64.b64decode(E['data']));assert hashlib.sha256(p).hexdigest()==E['uncompressedSha256'] and json.loads(p)==T
assert F['bundle']['overheadBytes']==176+6*128==944;assert len(F['nestedImages'])==33;assert len(F['checksums'])==6 and all(x['valid'] for x in F['checksums']);assert not any(x['kind']=='contradictory confirmed classification' for x in F['classificationConflicts']);print('PASS independent bundle/component closure, resource hashes,33nested images,6CRCs and lossless transport decode')
