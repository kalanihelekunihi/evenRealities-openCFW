#!/usr/bin/env python3
"""Fail-closed object/provider audit for drv_pdm_production.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-drv-pdm-production-function-map.tsv";PM=ROOT/"tools/manifests/g2-drv-pdm-production-provider-map.tsv";US=ROOT/"tools/manifests/g2-drv-pdm-production-upstream-source.tsv";CL=ROOT/"tools/manifests/g2-drv-pdm-production-closure.tsv"
PINS={FM:"acf072c425691441eeb7c08a176560addd0a1906feed00a767e61da371384578",PM:"72b7e5c6a0a6a097179bf1b9330f4cb39de27e817f30cdcc3f5f7d5ad4dd6e37",US:"8078ab41523e23a982beee7dfa4e59d3c097651ce7dce5ef2fa7ee4cc4eba4ad",CL:"cf97d9cb6a1e483c220a105b242809a14e7d3024703306f94890391eb61884c8"}
F=((0x57B444,0x57B460),(0x57B460,0x57B484),(0x57B484,0x57B4A8),(0x57B4A8,0x57B586),(0x57B586,0x57B640),(0x57B640,0x57B6A6));PHYS=(0x57B444,0x57B704);PATH_ADDR=0x7025D0;PATH_CELL=0x57B6C4
EASY={0x43CE9E,0x43D0CE,0x43D574};AMBIQ={0x591FAC,0x592014,0x592046,0x5920CC,0x592230,0x5922D6,0x59235E,0x592462,0x592556,0x592584,0x5925B4,0x59262C};IAR={0x43C0E4};FIRST={0x4C31D8,0x4C3204,0x53A5BE,0x475014}
COMMIT="5efc0228528a8adce5eae0d226fac85d2551eb3b";SOURCE_SHA="a4d6a2acdcb8414afcfb940d1c97e5aff6530aa972d72640be48ac216c7e2d8c";SOURCE_BLOB="23a440bfd6121509b0586f0afe1990fcf59dd8fb"
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 amb=json.loads((ROOT/"third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text());easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-core/PROVENANCE.json").read_text())
 if amb['upstream']['selected_commit']!=COMMIT or easy['upstream']['selected_commit']!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms['upstream']['selected_commit']!="d23a6949a0331ca96853bcd98b0fdcc4db47184c":raise c.AuditError("provider provenance changed")
 header=(ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_pdm.h").read_text()
 for name in ("initialize","deinitialize","power_control","configure","enable","disable","dma_start","fifo_threshold_setup","interrupt_enable","interrupt_disable","interrupt_clear","dma_get_buffer"):
  if f"am_hal_pdm_{name}(" not in header:raise c.AuditError("PDM API header changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 with US.open(newline='',encoding='utf8') as h:up=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=6 or len(up)!=12 or {int(r['stock_target'],0) for r in up}!=AMBIQ or {r['selected_commit'] for r in up}!={COMMIT}:raise c.AuditError("inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if (int(r['stock_start'],0),int(r['stock_end_exclusive'],0))!=(a,z) or len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256'] or c._uncovered((a,z),ii):raise c.AuditError("function closure changed")
  if set(ins)&set(ii):raise c.AuditError("overlap")
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if len(body)!=610 or sh(body)!="ec9551ebfd3a8cfae0bcb151a5bb1725962fc352e162680c7d76ab7e489b5862" or len(ins)!=237 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="e44ac0a1287a70c180e5caa596ed256dbda1cc0289259b464d548d970d7920a2" or ind:raise c.AuditError("body closure changed")
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=94 or sh(non)!="798575d54b193d2ba2b514c43e5d46fb2112c4164e932b6f851990c8039e7dc6" or sh(c._slice(b,*PHYS))!="c929ee1f49bcdb103b59810bc301080ea28d8b5e64578fe21f6274d7ca28f0dc":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="4099675b03e5460499d81c17f5f5ecc882609cde780cd5883244d90133032e02" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="697c44ef8c21632be2213189ae78e11a28af57451f47bde5e90c27418b0732d8":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,AMBIQ,IAR,FIRST)
 if len(calls)!=41 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!="331cace5c49615d30b83da0d6351942cb9a077fda01331c510c2d4ac086b9077" or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(20,13,1,4):raise c.AuditError("provider closure changed")
 instruction_entries=set(ins)-starts;entries=[];strict=[];noncode=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in instruction_entries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=6 or c._pair_digest(entries)!="7e9d43d25bedbdbdf84d87d9c994a8ab34d234781a1204c599fb4f813de845a1" or strict or noncode:raise c.AuditError("ingress changed")
 enc=starts|{a|1 for a in starts};interior=set(ins)-starts
 if any(v in enc or ((v&1) and (v&~1) in interior) for o in range(len(b)-3) for v in [struct.unpack_from('<I',b,o)[0]]):raise c.AuditError("stored pointer changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\driver\pdm\drv_pdm_production.c":raise c.AuditError("path changed")
 refs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(refs)!=4 or c._pair_digest(refs)!="e04b8c7051cac28161aa1608301cdea0815095cf5e4644d27850798ccc30f27e":raise c.AuditError("path refs changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("drv_pdm_production" in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"driver\pdm\drv_pdm_production.c","embedded_third_party_definitions":["__NVIC_EnableIRQ","__NVIC_DisableIRQ","__NVIC_SetPriority"]},"surface":{"linked_functions":6,"ghidra_discovered_functions":6,"path_anchored_functions":0,"raw_path_referencing_functions":2,"body_bytes":610,"physical_bytes":704,"outer_pool_bytes":94,"reachable_instructions":237,"direct_body_calls":41,"internal_direct_body_calls":3,"external_direct_body_calls":38,"indirect_body_calls":0,"direct_bl_entry_sites":6,"stored_function_entry_pointers":0,"strict_interior_ingress":0},"behavior":{"pdm0_init_deinit":True,"dma_double_buffer":True,"inactive_buffer_extract_16bit":True,"output_samples":1600,"output_bytes":3200},"provider_boundary":{"easylogger_calls":20,"ambiqsuite_pdm_calls":13,"ambiqsuite_pdm_apis":12,"iar_dlib_calls":1,"first_party_board_cache_calls":4,"ambiqsuite_selected_commit":COMMIT,"ambiqsuite_source_sha256":SOURCE_SHA,"ambiqsuite_source_git_blob":SOURCE_BLOB,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
