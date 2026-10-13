#!/usr/bin/env python3
"""Idempotently extract/verify explicit authenticated non-executable resource extents.
Never executes payloads, mutates inputs, or overwrites conflicting output bytes.
"""
from pathlib import Path
import json,hashlib,argparse,collections
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
def safe(root,name):
 p=(root/name).resolve();assert p.is_relative_to(root.resolve()),'path escapes declared root';return p
def verify(catalog,extract=False):
 j=json.loads(catalog.read_text());assert j['schema']=='opencfw-byte-exact-resources-v1';out=catalog.parent;bundle=safe(R,j['targetBundle']).read_bytes();assert len(bundle)==j['bundleBytes'] and sha(bundle)==j['bundleSha256'];data={}
 for k,s in j['sources'].items():
  b=safe(R,s['path']).read_bytes();assert len(b)==s['bytes'] and sha(b)==s['sha256'];data[k]=b
 extents=collections.defaultdict(list);blobCount=set()
 for s in j['segments']:
  a,b=s['range'];assert 0<=a<b<=len(data[s['source']]);raw=data[s['source']][a:b];assert len(raw)==s['length'] and sha(raw)==s['sha256'];p=safe(out,s['blob']);blobCount.add(p);extents[s['source']].append((a,b))
  if extract and not p.exists():
   p.parent.mkdir(parents=True,exist_ok=True)
   try:
    with p.open('xb') as stream:stream.write(raw)
   except FileExistsError:pass
  assert p.read_bytes()==raw,'existing resource differs; refusing overwrite'
 for x in extents.values():
  x.sort();assert all(a[1]<=b[0] for a,b in zip(x,x[1:]))
 for r in j['records']:
  a,b=r['sourceRange'];s=r['sharedSlice'];raw=safe(out,s['blob']).read_bytes()[s['offset']:s['offset']+s['length']];assert raw==data[r['source']][a:b] and len(raw)==r['length'] and sha(raw)==r['sha256']
 result={'pass':True,'recordsVerified':len(j['records']),'sourceSegmentCount':len(j['segments']),'uniqueBlobFiles':len(blobCount),'storedUniqueBlobBytes':sum(p.stat().st_size for p in blobCount),'sourceDomainUnionBytes':j['counts']['sourceDomainUnionBytes'],'manifestSha256':sha(catalog.read_bytes()),'bundleSha256':sha(bundle),'noSourceMutation':True,'allExtentsVerbatim':True,'overlapDuplication':False};return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=R/'resources/g2/s200-v2.2.6.10/manifest.json');p.add_argument('--verify',action='store_true');a=p.parse_args();result=verify(a.manifest.resolve(),not a.verify);(a.manifest.parent/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
