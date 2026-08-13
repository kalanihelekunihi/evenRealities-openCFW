#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for ota_transport.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ota-transport-function-map.tsv';PM=ROOT/'tools/manifests/g2-ota-transport-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ota-transport-closure.tsv'
PINS={FM:'8ca8cf7a770d279caa9a01bfddf4c0b7c73eb56224fde9b93ac41fd50bd2dcbc',PM:'5caf3a01a4ea5da99a02ab490cd915f46a4392b035fbf38f833a8fc95456a6cd',CL:'3f09a7287a0938cdf3f87400b32767702b6d889ca9c6d6241d4e91002aec58d7'}
PHYS=(0x48D8D8,0x48E1CC);PATH=0x6E9070;CELL=0x48E0B4
EASY={0x43CE9E,0x43D0CE,0x43D574};RUNTIME={0x439BE4,0x43C0E4};OTA={0x44871A,0x44874C};CRC={0x49ACD4};HEAP={0x474D16}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or 'deff9ab509341f264addbd3c8ada533678591905' not in (ROOT/'third_party/tlsf/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=3 or sum(r['path_anchored']=='yes' for r in rows)!=2:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un or len(body)!=2004 or sh(body)!='ebe0b51a92c8ea7583650e826080dc55a04839c453a6cf907c804639de660111' or len(ins)!=772 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='fab37f208f10dc7df576bacb6749c9f69815274999b31566b531fafd8b14d3fc' or dyn!=[0x48D9CA,0x48DC26,0x48DDEC,0x48E012]:raise c.AuditError('body/indirect closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=288 or sh(outer)!='f42a618d48b8bdc0d146a1c34177e214144830650171db346898e9248d40b35b' or sh(c._slice(b,*PHYS))!='97806abc785106ad053e699cd02fcfc72c3a0a2a90a55fe91dcffca7b58a4aa3':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='1c60b7a45b29a658b4694ad6ea1637698290218cbfcb60a47d84f01b524d2ca2' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='7a361a59fe1fa6980be7e2907c890295ce1a004113bcff8503f0d37fdcbd30fa':raise c.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-EASY-RUNTIME-OTA-CRC-HEAP
 if len(calls)!=86 or sum(t in starts for _,t in calls)!=0 or c._pair_digest(calls)!='ad62d85989d3a0403e4b110698e9378c836128ab579cd953a7bc62f75f081099' or tuple(sum(ext[t] for t in s) for s in (EASY,RUNTIME,OTA,CRC,HEAP,first))!=(60,8,5,4,6,3):raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=6 or c._pair_digest(entries)!='391d6b7c50949d90a341331749a6cfbee8f10401bf3b2c78016e8369e14f72ec' or strict or non or wide or ws:raise c.AuditError('branch ingress changed')
 raw=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:raw.append((c.BASE+off,v,t))
 if raw:raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ota_service\ota_transport.c':raise c.AuditError('path changed')
 refs=sorted((CELL,a) for a in th.literal_references(b,CELL))
 if len(refs)!=13 or c._pair_digest(refs)!='569dd9696f52ef82ed99e1e11e25c5edc357a0d756ab9d200ba4b9a427fe9917':raise c.AuditError('path refs changed')
 routed=any('ota_transport' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\protocols\ota_service\ota_transport.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':3,'path_anchored_functions':2,'body_bytes':2004,'physical_bytes':2292,'outer_pool_bytes':288,'reachable_instructions':772,'direct_body_calls':86,'internal_direct_body_calls':0,'external_direct_body_calls':86,'indirect_body_calls':4,'indirect_call_sites':dyn,'direct_bl_entry_sites':6,'stored_function_pointers':0},'provider_boundary':{'easylogger_calls':60,'runtime_calls':8,'ota_service_calls':5,'crc16_calls':4,'heap_wrapper_calls':6,'first_party_calls':3,'registered_callback_calls':4,'callback_slots':['0x20003058','0x2000305C'],'historical_ota_transport_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
