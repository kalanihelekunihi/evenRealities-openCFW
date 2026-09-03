#!/usr/bin/env python3
"""Fail-closed object/provider audit for service_android_notify.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_json_parser as j
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-service-android-notify-function-map.tsv';PM=ROOT/'tools/manifests/g2-service-android-notify-provider-map.tsv';CL=ROOT/'tools/manifests/g2-service-android-notify-closure.tsv'
PINS={FM:'f2af15a903db38d81711f46415c918d01658d6768dc695c8d675f11b66f6c04f',PM:'6abf544547139777ec733111e6e741488e8e845d2b4389a696a9eb2293253830',CL:'459c7a2721c92223188a80d42a090cef7fa4d78e5e8fd189cb0555a9fd076dd9'}
PHYS=(0x48E484,0x48E8D4);PATH_ADDR=0x6DE554;CELL=0x48E858
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4,0x44B5A0};ANCC={0x4972A2,0x497960};PROF={0x4BF8AC};WL={0x4D67B8};SYNC={0x464D1C};JSONP={0x4D79FA,0x4D7F7E,0x4D83AA}
STORED=[(0x48E878,0x48E495),(0x6A46C4,0x48E485)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());ancc=json.loads((ROOT/'third_party/ambiqsuite-ancc-profile/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or ancc['upstream']['selected_commit']!='de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f':raise c.AuditError('provider provenance changed')
 cjson=j.analyze()
 if (cjson['identity']['upstream_version_interval']!='v1.7.9 through v1.7.12' or
     not cjson['provider_boundary']['new_version_discriminator'] or
     not cjson['production']['production_routed'] or
     cjson['production']['routed_functions']!=21 or
     cjson['production']['entry_patch_sites']!=21 or
     cjson['production']['undefined_symbols']!=0 or
     cjson['production']['hardware_operations']):
  raise c.AuditError('cJSON production provider changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=5 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort()
 if len(body)!=972 or sh(body)!='a9bf133fb5373a878631649a198c89dc7cc93f84bda634303c6986ff77049332' or len(ins)!=366 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='a283b855130bd18466a51c2ca74b971c6b315e7d639ee2cb3dff82043a8aa405' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=132 or sh(non)!='3ba5eb71cd272fc966cb22c951a9e073311f76546746eefbd488d47b57e2bc8f' or sh(c._slice(b,*PHYS))!='2f616de55b9ab66aa67f3baedd840d68a1a0bd13abb2c1f07be7b3cf7dbc6971':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='6b05ee1404f88d1b3377c454469f5b8b862ce999df08c7999f6dbd84c21bddf6' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='f43654c5569de689da66634b983544b2565a43d57195398096d52ee12eb1b1a6':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,ANCC,PROF,WL,SYNC,JSONP)
 if len(calls)!=67 or sum(y in starts for x,y in calls)!=2 or c._pair_digest(calls)!='6d5717a18a88b0d3bb2ff034a5c55ce9839265b1ac312a3d39b3558a1db1afac' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(40,7,2,1,1,1,13):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[];ientries=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in ientries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=3 or c._pair_digest(entries)!='95566dc110fe47d8e3a9f5606799e55b3095c59154f2d3e4c107abb3ee212a97' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in ientries]
 if stored!=STORED or interior:raise c.AuditError('stored ingress changed')
 o=PATH_ADDR-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0 or b[o:e].decode('ascii')!=r'D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_android_notify.c':raise c.AuditError('path changed')
 refs=t.literal_references(b,CELL);pairs=[(CELL,x) for x in refs]
 if len(refs)!=8 or c._pair_digest(pairs)!='6de13f26a5420703467f7dc8015be868e19016bd976acd82f0cbb45cf5ce618d':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('service_android_notify' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':2,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\service\message_notify\service_android_notify.c','embedded_third_party_definitions':['production-routed DaveGamble cJSON v1.7.9-v1.7.12 parse provider at 0x004D79FA,0x004D7F7E,0x004D83AA, shared with closed service_whitelist.c; maintained baseline v1.7.12 at 3c8935676a97c7c97bf006db8312875b4f292f6c']},'surface':{'linked_functions':5,'ghidra_discovered_functions':3,'restored_functions':2,'path_anchored_functions':3,'body_bytes':972,'physical_bytes':1104,'noncode_bytes':132,'reachable_instructions':366,'direct_body_calls':67,'internal_direct_body_calls':2,'external_direct_body_calls':65,'indirect_body_calls':0,'direct_bl_entry_sites':3,'external_direct_bl_entry_sites':1,'stored_function_entry_pointers':2,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':40,'iar_dlib_calls':7,'closed_ancc_service_calls':2,'closed_ambiqsuite_ancc_profile_calls':1,'closed_whitelist_service_calls':1,'closed_sync_interface_calls':1,'source_routed_json_parser_calls':13,'cmsis_freertos_calls':0,'freertos_kernel_calls':0,'embedded_json_parser_version_interval':'v1.7.9 through v1.7.12','new_version_discriminator':True,'json_parser_production_routed':True},'production':{'production_routed':False,'software_boundary':'blocked by unavailable proprietary inputs','hardware_validation':'blocked by unavailable physical evidence','hardware_operations':[]}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
