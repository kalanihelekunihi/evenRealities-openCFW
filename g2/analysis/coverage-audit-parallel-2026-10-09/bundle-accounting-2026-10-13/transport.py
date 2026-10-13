from pathlib import Path
import json,gzip,base64,hashlib
O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();C=json.loads((O/'compact-v3.json').read_text());D=json.loads(json.dumps(C));D['transportSchema']='opencfw-v3-lossless-length-partitions';D['runEncoding']=['lengthBytes','stageBitmask'];D['exclusiveRunEncoding']=['lengthBytes','classificationIndex'];D['bundle'].pop('exclusiveRuns');D['bundle']['exclusiveRunDerivation']='Translate each component exclusive partition by component_payload.segment.bundleStart; add metadata/header segments as confirmed_data; sort, requiring adjacency to EOF.'
for c in D['components']:
 c['runs']=[[b-a,m] for a,b,m in c['runs']];c['exclusiveRuns']=[[b-a,k] for a,b,k in c['exclusiveRuns']]
# Exact transport validation: all raw ranges recover from cumulative lengths, with no sampling.
for raw,enc in zip(C['components'],D['components']):
 for key in ['runs','exclusiveRuns']:
  got=[];a=0
  for n,k in enc[key]:got.append([a,a+n,k]);a+=n
  assert got==raw[key] and a==raw['payloadBytes']
raw=json.dumps(D,separators=(',',':')).encode();(O/'compact-v3-transport.json').write_bytes(raw);z=gzip.compress(raw,9,mtime=0);e={'schema':'opencfw-v3-gzip-length-envelope','encoding':'gzip-base64','uncompressedBytes':len(raw),'uncompressedSha256':sha(raw),'gzipBytes':len(z),'gzipSha256':sha(z),'data':base64.b64encode(z).decode(),'decodeContract':'gzip decode JSON; each component runs/exclusiveRuns is [length,classOrMask], beginning at0. Restore start/end cumulatively. Derive bundle runs using exact bundle segments. Full raw runs remain in full-v3.json. No gaps or downsampling.'};(O/'compact-v3-packed.json').write_text(json.dumps(e,separators=(',',':')));assert gzip.decompress(base64.b64decode(e['data']))==raw;v=json.loads((O/'package-validation.json').read_text());v.update({'transportJsonBytes':len(raw),'packedCompactFileBytes':(O/'compact-v3-packed.json').stat().st_size,'packedCompactSha256':sha((O/'compact-v3-packed.json').read_bytes()),'transportJsonSha256':sha(raw),'lengthPartitionDecodeEqualsEveryOriginalRun':True});(O/'package-validation.json').write_text(json.dumps(v,indent=2)+'\n');print('transport',len(raw),'gzip',len(z),'packed',(O/'compact-v3-packed.json').stat().st_size)
