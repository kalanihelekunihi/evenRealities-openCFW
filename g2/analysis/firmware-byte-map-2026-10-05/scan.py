#!/usr/bin/env python3
"""Conservative stored-byte map. End offsets exclusive; no RAM expansion counted."""
from pathlib import Path
import hashlib,json,struct,collections,importlib.util
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
target=json.loads((ROOT/'g2/workflow/target.json').read_text());bundle=(ROOT/'g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin').read_bytes();assert sha(bundle)==target['bundle']['sha256'] and len(bundle)==4301227
spec=importlib.util.spec_from_file_location('formats',ROOT/'g2/tools/open_cfw.py');formats=importlib.util.module_from_spec(spec);import sys;sys.modules['formats']=formats;spec.loader.exec_module(formats);formats.validate_evenota_image(bundle,json.loads((ROOT/'g2/manifests/g2-2.2.6.10.json').read_text()))
claims=[];payloads={}
def claim(a,z,c,sub,e):
 assert 0<=a<z<=len(bundle);claims.append(dict(start=a,end_exclusive=z,classification=c,subtype=sub,evidence=e))
claim(0,176,'metadata','EVENOTA header/TOC/trailer','open_cfw.validate_evenota_image PASS')
for i,component in enumerate(target['components']):
 eid,offset,size,crc=struct.unpack_from('<IIII',bundle,64+16*i);assert eid==component['entry_id'];start=offset+128;data=(ROOT/component['local_payload_path']).read_bytes();assert sha(data)==component['sha256'] and bundle[start:offset+size]==data
 payloads[component['id']]={'bundle_start':start,'size':len(data),'sha256':sha(data),'path':component['local_payload_path']};claim(offset,start,'metadata','EVENOTA entry header','validated TOC + component identity')
for name in ['codec-review.json','small-payload-review.json']:
 fp=OUT/name
 if not fp.exists():continue
 j=json.loads(fp.read_text())
 if name=='codec-review.json':
  for row in j['definitely_non_code_disjoint_spans']:
   base=payloads['codec']['bundle_start'];a,z=row['start'],row['end_exclusive'];assert sha(bundle[base+a:base+z])==row['sha256'];category='metadata' if any(x in row['classification'] for x in ['metadata','record','padding','alignment']) else 'noncode';claim(base+a,base+z,category,row['classification'],row)
  # Accelerator command role is proven; its opcode semantics are not. Kept unresolved rather than a CPU instruction lower bound.
 else:
  for comp in j['components']:
   for row in comp['regions']:
    status=row['classification_status']
    if not status.startswith('definite_non_code'):continue
    base=payloads[comp['component']]['bundle_start'];a,z=row['start'],row['end_exclusive'];assert sha(bundle[base+a:base+z])==row['sha256'];category='metadata' if 'container' in status else 'noncode';claim(base+a,base+z,category,row.get('subtype',''),row)
main=payloads['apollo_main'];b=bundle[main['bundle_start']:main['bundle_start']+main['size']];base=0x437fe0
refs=collections.defaultdict(list)
for off in range(0,len(b)-3,4):refs[struct.unpack_from('<I',b,off)[0]].append(off)
assets=[]
for off in range(0,len(b)-27,4):
 magic,cf,flags,w,h,stride,r2,size,ptr,r0,r1=struct.unpack_from('<BBHHHHHIIII',b,off)
 if magic==25 and cf==6 and flags==r2==r0==r1==0 and 0<w<2049 and 0<h<2049 and stride==w and size==stride*h and base<=ptr and ptr-base+size<=len(b):
  assets.append(dict(descriptor_payload_offset=off,descriptor_runtime=base+off,data_payload_range=[ptr-base,ptr-base+size],data_runtime_range=[ptr,ptr+size],width=w,height=h,stride=stride,pixel_sha256=sha(b[ptr-base:ptr-base+size]),pointer_reference_payload_offsets=refs[base+off],classification='unresolved structured image candidate',limit='Typed header + pointer refs; decoder callback closure not fully established. Not subtracted from unresolved.'))
dump('display-image-candidates.json',assets)
spec=importlib.util.spec_from_file_location('assets',ROOT/'g2/tools/assetgen_lvgl_image.py');mod=importlib.util.module_from_spec(spec);sys.modules['assets']=mod;spec.loader.exec_module(mod)
replays=[]
for a in assets[:3]:
 off=a['descriptor_payload_offset'];x,z=a['data_payload_range'];assert mod.pack_header('L8',a['width'],a['height'],a['stride'])==b[off:off+12];rows=mod.decode('L8',a['width'],a['height'],a['stride'],b'',b[x:z]);assert bytes(p[0] for row in rows for p in row)==b[x:z];replays.append({'descriptor_runtime':a['descriptor_runtime'],'pixel_sha256':a['pixel_sha256'],'header_and_pixel_roundtrip':'PASS','limit':'host format replay, not firmware decoder execution'})
# Only observed original PCs from successful bounded replay are admitted as CPU code.
for folder,validation in [('execution-proof','trace-validation.json'),('display-proof','validation.json')]:
 vp=OUT/folder/validation
 if not vp.exists():continue
 v=json.loads(vp.read_text());producer=OUT/('trace_existing_angle.py' if folder=='execution-proof' else 'verify_display_family.py');assert sha(producer.read_bytes())==v.get('replay_script_sha256',v.get('script_sha256'));tp=OUT/folder/'executed-instructions.jsonl';assert sha(tp.read_bytes())==v['executed_trace_sha256'] and v['firmware_sha256']==main['sha256']
 for line in tp.read_text().splitlines():
  row=json.loads(line);a,z=row['payload_range'];bb=bytes.fromhex(row['instruction_bytes']);assert row['runtime_pc']==base+a and z-a==len(bb) and b[a:z]==bb and sha(bb)==row['sha256'];claim(main['bundle_start']+a,main['bundle_start']+z,'code','observed original CPU instruction',dict(trace=str(tp.relative_to(ROOT)),trace_sha256=sha(tp.read_bytes()),validation=str(vp.relative_to(ROOT)),validation_sha256=sha(vp.read_bytes()),row=row))
vp=OUT/'display-proof/validation.json'
if vp.exists():
 v=json.loads(vp.read_text());assert v['firmware_sha256']==main['sha256'] and v['script_sha256']==sha((OUT/'verify_display_family.py').read_bytes())
 for f in v['family']:
  a=f['asset'];x,z=a['data_payload_range'];assert sha(b[x:z])==a['pixel_sha256'];e={'validation':str(vp.relative_to(ROOT)),'sha256':sha(vp.read_bytes()),'constructor_literal_load':f['load_pc'],'constructor_direct_call':f['call_pc'],'descriptor':a['descriptor_runtime'],'limit':'Attributed variable-source L8 storage; renderer pixel access not executed.'};claim(main['bundle_start']+x,main['bundle_start']+z,'noncode','consumer-attributed L8 image storage',e)
  x=a['descriptor_payload_offset'];claim(main['bundle_start']+x,main['bundle_start']+x+28,'noncode','consumer-attributed image descriptor',e)
  x=f['literal_runtime']-base;assert b[x:x+4].hex()==f['literal_bytes'] and struct.unpack_from('<I',b,x)[0]==a['descriptor_runtime'];claim(main['bundle_start']+x,main['bundle_start']+x+4,'noncode','image source pointer literal',e)

if vp.exists():
 admitted={f['asset']['descriptor_runtime'] for f in v['family']}
 for a in assets:
  if a['descriptor_runtime'] in admitted:a['classification']='consumer-attributed image storage';a['limit']='Static constructor literal/direct BL plus original decoder admission and geometry/storage construction; rendering not executed.'
 dump('display-image-candidates.json',assets)
# Partition by claim boundaries; uncovered bytes stay unresolved; conflicting claims remain explicit.
points=sorted({0,len(bundle),*(x for c in claims for x in [c['start'],c['end_exclusive']])});intervals=[]
for a,z in zip(points,points[1:]):
 cs=[c for c in claims if c['start']<=a and z<=c['end_exclusive']];kinds={c['classification'] for c in cs};kind=next(iter(kinds)) if len(kinds)==1 else 'conflict' if kinds else 'unresolved';p=next((name for name,p in payloads.items() if p['bundle_start']<=a and z<=p['bundle_start']+p['size']),None);intervals.append({'bundle_start':a,'bundle_end_exclusive':z,'bytes':z-a,'sha256':sha(bundle[a:z]),'classification':kind,'payload':p,'payload_range':[a-payloads[p]['bundle_start'],z-payloads[p]['bundle_start']] if p else None,'claims':cs})
assert sum(i['bytes'] for i in intervals)==len(bundle);assert all(x['bundle_end_exclusive']==y['bundle_start'] for x,y in zip(intervals,intervals[1:]));counts=collections.Counter();[counts.update({i['classification']:i['bytes']}) for i in intervals]
(OUT/'interval-map.jsonl').write_text(''.join(json.dumps(i)+'\n' for i in intervals))
summary={'bundle_sha256':sha(bundle),'bundle_bytes':len(bundle),'payloads':payloads,'classified_bytes':dict(counts),'confirmed_cpu_executable_lower_bound_bytes':counts['code'],'possible_executable_upper_bound_bytes':counts['unresolved']+counts['conflict']+counts['code'],'executable_completion_percent':None,'asset_candidate_count':len(assets),'referenced_asset_candidates':sum(bool(a['pointer_reference_payload_offsets']) for a in assets),'tests':{'bundle_validation':'PASS','six_payload_hashes':'PASS','no_gaps_overlaps_doublecount':'PASS','bounded_asset_replays':replays},'limits':['Only byte-matched actually observed PCs from successful synthetic execution are admitted as CPU code; full bodies are not.','Existing byte-matched instruction exports are candidates, not independently proven executable classification.','Accelerator command stream remains code-bearing unresolved, never weight data.','Unresolved includes obvious code candidates, image candidates and compressed initializers.','Runtime RAM/BSS sizes are not stored bytes and are excluded from this partition.','Code-only metric intersections are recorded separately; no semantic completion implied.']};summary['consumer_attributed_asset_count']=sum(a['classification']=='consumer-attributed image storage' for a in assets)
dump('summary.json',summary)
subtypes=collections.Counter()
for r in intervals:
 if r['classification']=='noncode':subtypes[r['claims'][0]['subtype']]+=r['bytes']
breakdown={'confirmed_cpu_executable':counts['code'],'confirmed_noncode_by_type':dict(subtypes),'confirmed_noncode_total':counts['noncode'],'metadata_excluding_separately_proven_padding':counts['metadata']-4,'padding':4,'unresolved':counts['unresolved'],'conflicts':counts['conflict'],'total':len(bundle),'executable_denominator_bound':[counts['code'],counts['unresolved']+counts['conflict']+counts['code']],'note':'Summary metadata includes4-byte proven padding. Only actually observed original PCs admitted. Synthetic execution proves code role, not hardware behavior.'}
assert sum(subtypes.values())==counts['noncode'];dump('classification-breakdown.json',breakdown)
print(json.dumps(summary,indent=2))
