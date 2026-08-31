#!/usr/bin/env python3
"""Fail-closed object/provider audit for driver/sensor/als/als.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-als-function-map.tsv";PM=ROOT/"tools/manifests/g2-als-provider-map.tsv";CL=ROOT/"tools/manifests/g2-als-closure.tsv"
PINS={FM:"c893a36fd7584420ff5b5fd73fa5fbe63e2c90724e5b15b9422807fe7f5dcdda",PM:"8e5fb6091ed60e27a906e392a3620e6c39b73accc22010ac8923f1393877f3a0",CL:"99cabe8b2bfcffba83228626d6e123ec852f75b2c6921746c758891841c9b2dc"}
PHYS=(0x4AD9B8,0x4AEA40);PATH_ADDR=0x711CE0;PATH_CELLS=(0x4AE4D8,0x4AE9DC)
SOURCE=ROOT/"components/apollo_main/core_overlay/als.c";SOURCE_PATH="components/apollo_main/core_overlay/als.c";OVERLAY=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(28108,"97eb57e4da2bc78dc42b5391567899bb9a6041cfec5febbbb30773f820623919")
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x449376};RUNTIME={0x43C0E4,0x47CC60};FIRST={0x44A1C6,0x464D1C,0x46B44C,0x46BFE8,0x46BFF4,0x47394C,0x49BE04,0x4A5D16,0x4A6988,0x4A6998,0x509024};OPT={0x51357C,0x5135D2,0x5135E0,0x513748}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated path")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
 if easy['upstream']['selected_commit']!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms['upstreams']['cmsis_freertos']['selected_commit']!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("provider provenance changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=38 or sum(r['path_anchored']=='yes' for r in rows)!=9:raise c.AuditError("function inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256'] or c._uncovered((a,z),ii):raise c.AuditError("function closure changed")
  if set(ins)&set(ii):raise c.AuditError("overlap")
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if len(body)!=3858 or sh(body)!="e897dd73b49a41d14e891ceacccb389f8323c82c4cb4eb477a8cd33407f0c5db" or len(ins)!=1461 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="9c5e9ae441c40d23bdc60e2592ef607bcecc8adb65ab9680074659d57cfa5845" or ind!=[0x4AE7FC]:raise c.AuditError("body closure changed")
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=374 or sh(non)!="4f0e94214610db8706ec58fce18ce02e0f6cf4c2711ddaff2a0c5e393baee5ce" or sh(c._slice(b,*PHYS))!="ee176a8d9ac89fe99a9d93a263a46af28b22c2124a637da55f3309564f56c788":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="f4e282832c17627f4bcd1619ebc921e7d6195c8130258cc8a3f03bd0ae290f23" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="37c4adeb7c4dabc5ad9f396c3921d517adc86a3d2d596e1b88f73723edc8c32d":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,RUNTIME,FIRST,OPT)
 if len(calls)!=189 or sum(y in starts for x,y in calls)!=50 or c._pair_digest(calls)!="7965cd86bfde0f60dd6828c2c76041804df264f654d11daf0b4662958726e75e" or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(105,1,4,23,6):raise c.AuditError("provider closure changed")
 entries=[];strict=[];noncode=[];inter=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=60 or c._pair_digest(entries)!="0e3349e7782e555a0cf42c2055cdc0e8863834bff5bd509420e6bab3b7057aa1" or strict!=[(0x4AE09C,0x4AE6A8)] or noncode:raise c.AuditError("ingress changed")
 found=[]
 for v in starts|{a|1 for a in starts}:
  needle=struct.pack('<I',v);p=0
  while True:
   o=b.find(needle,p)
   if o<0:break
   found.append((c.BASE+o,v));p=o+1
 if sorted(found)!=[(0x6A44C4,0x4AE73D)]:raise c.AuditError("stored entries changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\driver\sensor\als\als.c":raise c.AuditError("path changed")
 refs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(refs)!=21 or c._pair_digest(refs)!="f60b6d2e9a71207de8f8a6cba2de42c925416cb86fcddd4cd3ffac8e4956a415":raise c.AuditError("path refs changed")
 opt=json.loads(__import__('subprocess').check_output([sys.executable,str(ROOT/'tools/analyze_g2_opt3007_registers.py')],text=True))
 if opt['surface']['linked_functions']!=1 or not opt['production']['production_routed']:raise c.AuditError("OPT3007 boundary changed")
 if (len(SOURCE.read_bytes()),sh(SOURCE.read_bytes()))!=SOURCE_PIN:raise c.AuditError("ALS source changed")
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH];names={x['function'] for x in leaves}
 if len(leaves)!=38 or len(names)!=38 or not names<=set(overlay['functions']) or sum(x['expected']['size'] for x in leaves)!=2216 or sum(len(x['relocations']) for x in leaves)!=82:raise c.AuditError("ALS production leaf closure changed")
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='MIT' for x in leaves):raise c.AuditError("ALS production policy changed")
 patches=[x for x in overlay['patch_sites'] if x.get('target_function') in names]
 expected_patch={(int(r['stock_start'],0),int(r['interval_bytes']),r['interval_sha256']) for r in rows}
 if len(patches)!=38 or sum(x['expected_size'] for x in patches)!=3858 or {(x['runtime_address'],x['expected_size'],x['expected_sha256']) for x in patches}!=expected_patch or any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise c.AuditError("ALS guarded replacement closure changed")
 build=json.loads(REPORT.read_text())
 validate_apollo_main_artifacts(ROOT,c.AuditError,"ALS")
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if len(built)!=38 or sum(x['placement']['size'] for x in built)!=2264 or sum(x['extraction']['size'] for x in built)!=2216 or sum(x['placement']['padding_before'] for x in built)!=30 or sum(x['extraction']['relocation_count'] for x in built)!=82:raise c.AuditError("ALS built leaf closure changed")
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];als=[x for x in main['regions'] if x.get('name','').startswith('als_')]
 if len(als)!=99 or sum(x['size'] for x in als if x.get('address_status')=='generated_source_entry_replacement')!=3858 or sum(x['size'] for x in als if x.get('address_status')=='official_blob')!=374 or sum(x['size'] for x in als if x.get('address_status')=='source_compiled')!=2264 or sum(x['size'] for x in als if x.get('address_status')=='generated_alignment')!=30:raise c.AuditError("ALS manifest tiling changed")
 plan_bytes=FLASH_PLAN.read_bytes();plan=json.loads(plan_bytes)
 blocker='hardware validation is blocked by unavailable physical evidence; future qualification requires authorized G2 hardware and either a component-specific calibrated-lux/OPT3007 fixture or an authenticated golden OPT3007 capture'
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"driver\sensor\als\als.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":38,"ghidra_discovered_functions":22,"path_anchored_functions":9,"restored_non_anchor_functions":29,"body_bytes":3858,"physical_bytes":4232,"outer_pool_bytes":374,"reachable_instructions":1461,"direct_body_calls":189,"internal_direct_body_calls":50,"external_direct_body_calls":139,"indirect_body_calls":1,"bounded_first_party_indirect_calls":1,"direct_bl_entry_sites":60,"stored_function_pointers":1,"strict_interior_ingress":0,"unaligned_pseudo_bl":1},"behavior":{"opt3007_register_specification":"TI SBOS864","adaptive_brightness_calibration":True,"display_driver_interface_dispatch":True},"provider_boundary":{"easylogger_calls":105,"cmsis_freertos_delay_calls":1,"runtime_calls":4,"closed_first_party_calls":23,"opt3007_adapter_calls":6,"opt3007_adapter_production_routed":True,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","public_opt3007_software_commit":None},"production":{"source_inventory_available":True,"production_routed":True,"candidate":SOURCE_PATH,"source_functions":38,"compiled_text_bytes":2216,"compiled_rodata_bytes":48,"generated_alignment_bytes":30,"guarded_redirects":38,"ownership_bytes":3858,"retained_compatibility_bytes":374,"strict_relocations":82,"hardware_validation":"blocked by unavailable physical evidence","hardware_blocker":blocker}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
