#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for service_input_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-service-input-manager-function-map.tsv';PM=ROOT/'tools/manifests/g2-service-input-manager-provider-map.tsv';CL=ROOT/'tools/manifests/g2-service-input-manager-closure.tsv'
PINS={FM:'09e2a5abb58e556fd20e5ee2b8b8050f1b86df31a4fdc6817922f13db777212c',PM:'16a0cf8bcfe6677346f57a9ab038fae36200769eb664d611804b88bc2467bc49',CL:'57f5973ea39b7d076b61af0ae5ccb5db0cbbed6002c7ac875bf45b02c6285ed6'}
PHYS=(0x4C5886,0x4C6240);PATH=0x6F5E5C;CELL=0x4C6180
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC};RUNTIME={0x439BE4,0x43C0E4};NANOPB={0x48EB32};ABS={0x509694}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());nano=json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or nano['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=10 or sum(r['path_anchored']=='yes' for r in rows)!=5:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un or len(body)!=2242 or sh(body)!='60e280c02dd41f77f916e95403ba42136c6f422626569981a37d3e16942b3552' or len(ins)!=827 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='dd1bdbc1f134ea2fa54b8918c35ab3896b4a2c64cf2e986ddfded2c21dad5f92' or dyn:raise c.AuditError('body closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=248 or sh(outer)!='aa0c0edb1137b722407992a3d75d3a2435f74613f5df6362ab3f19843bd22583' or sh(c._slice(b,*PHYS))!='65653e98aca3ba889d207651cb6da4e7dd40408aec6cb147003fa4150149e577':raise c.AuditError('physical closure changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-EASY-CMSIS-RUNTIME-NANOPB-ABS
 if len(calls)!=118 or sum(t in starts for _,t in calls)!=15 or c._pair_digest(calls)!='92d2b09ad50b443fe6be76bc0c237f6ece2b4ac437d161b5a6fbf5175a28cca2' or tuple(sum(ext[t] for t in s) for s in (EASY,CMSIS,RUNTIME,NANOPB,ABS,first))!=(85,2,2,2,1,11):raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=29 or c._pair_digest(entries)!='aa272005537ab5c6b15d6af5d026009223269b0aced63b6b179b87ef612db23a' or strict or non or wide or ws:raise c.AuditError('branch ingress changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((c.BASE+off,v,t))
   if t in starts and (c.BASE+off)%4==0 and v&1:stored.append((c.BASE+off,v))
 if len(raw)!=3 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='53cfac87b6728cd3c46ab495a817f19cd683653dfa69de9af5ffe1a31a976941' or len(stored)!=2 or c._pair_digest(stored)!='86ef6b312894fcf386e19f4e6d34599fee3a62295a25d62c2a6b45c5340885f0':raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\platform\input\service_input_manager.c':raise c.AuditError('path changed')
 refs=sorted((CELL,a) for a in th.literal_references(b,CELL))
 if len(refs)!=17 or c._pair_digest(refs)!='9908ceaf9826b029035e38aeff7c13c0f8281f25566a4f10fca7de7453238cd6':raise c.AuditError('path refs changed')
 routed=any('service_input_manager' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\input\service_input_manager.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':10,'path_anchored_functions':5,'body_bytes':2242,'physical_bytes':2490,'outer_pool_bytes':248,'reachable_instructions':827,'direct_body_calls':118,'internal_direct_body_calls':15,'external_direct_body_calls':103,'indirect_body_calls':0,'direct_bl_entry_sites':29,'stored_function_pointers':2},'provider_boundary':{'easylogger_calls':85,'cmsis_freertos_calls':2,'runtime_calls':2,'nanopb_calls':2,'bounded_abs_calls':1,'first_party_calls':11,'historical_input_manager_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
