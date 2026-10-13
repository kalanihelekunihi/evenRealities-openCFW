from pathlib import Path
import json,hashlib,struct,zlib,collections
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();j=json.loads((O/'resources-full.json').read_text());baseline=json.loads((O.parent/'full-accounting.json').read_text());m=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());p={c['name']:(R/'g2'/c['provider']['path']).read_bytes() for c in m['components']};checked=0
assert j['baselineExclusiveTotals']==baseline['bundle']['exclusiveTotals'];assert sum(j['baselineExclusiveTotals'].values())==4301227
for r in j['resources']:
 a,b=r['payloadRange'];assert sha(p[r['component']][a:b])==r['sha256'];assert b-a==r['length'];checked+=1
# Validate static/decoded font-root hashes in their own coordinate domains.
images={x['id']:x for x in map(json.loads,(R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines())}
rootChecked=0
for f in j['customFontCandidates']:
 for root in f.get('fontRootRecords',[]):
  if root['domain']=='apollo_main:flash':data=p['apollo_main']
  else:
   im=images[root['domain']];path=Path(im['content_path']);path=path if path.is_absolute() else R/path;data=path.read_bytes();assert sha(data)==im['content_sha256']
  a,b=root['range'];assert sha(data[a:b])==root['sha256'];assert struct.unpack_from('<II',data,a)==(0x4b26a5,0x4b239d);assert struct.unpack_from('<I',data,a+24)[0]==f['address'];rootChecked+=1
for tile in j.get('fontConsumerEvidence',{}).get('tiles',[]):
 a,b=tile['payloadRange'];assert sha(p['apollo_main'][a:b])==tile['sha256']
ranges=[]
for f in j['customFontCandidates']:
 for s in f.get('validatedSpans',[]):
  a,b=s['payloadRange'];assert sha(p['apollo_main'][a:b])==s['sha256'];ranges.append((a,b));checked+=1
 for sample in f.get('samples',[]):assert sha((R/sample['file']).read_bytes())==sample['sha256']
merged=[]
for a,b in sorted(ranges):
 if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
 else:merged.append([a,b])
counts=collections.Counter();main=next(x for x in baseline['componentsExclusive'] if x['component']=='apollo_main')
for a,b in merged:
 for c,d,k in main['runs']:
  n=max(0,min(b,d)-max(a,c));counts[baseline['bundle']['categories'][k]]+=n
for s in j['samples']:
 assert sha((R/s['samplePath']).read_bytes())==s['sha256']
for f in O.glob('*.png'):
 b=f.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';o=8
 while o<len(b):
  n=struct.unpack_from('>I',b,o)[0];assert zlib.crc32(b[o+4:o+8+n])&0xffffffff==struct.unpack_from('>I',b,o+8+n)[0];o+=12+n
 assert o==len(b)
receipt={'pass':True,'resourceAndFontSliceHashesVerified':checked,'baselinePartitionUnchanged':True,'fontRootHashesAndCallbacksVerified':rootChecked,'newStrongFontCandidateUnionBytes':sum(b-a for a,b in merged),'fontUnionPriorExclusiveClasses':dict(counts),'fontUnionIntervals':merged,'imagePGMSamplesVerified':len(j['samples']),'fontPNGSampleCount':sum(len(f.get('samples',[])) for f in j['customFontCandidates']),'errors':[],'artifacts':{str(f.relative_to(R)):{'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(O.iterdir()) if f.is_file() and f.name!='validation.json'}};(O/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ('artifacts','fontUnionIntervals')},indent=2))
