#!/usr/bin/env python3
"""Fail-closed object/provider audit for driver/pdm/drv_pdm.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-drv-pdm-function-map.tsv";PM=ROOT/"tools/manifests/g2-drv-pdm-provider-map.tsv";US=ROOT/"tools/manifests/g2-drv-pdm-upstream-source.tsv";CL=ROOT/"tools/manifests/g2-drv-pdm-closure.tsv"
PINS={FM:"f36f95253b9d0368fbcf335ab6f87b5672d991717402779c9d386a928b3ffb41",PM:"41403c5903b09e87934e30305cc5c7342d2f65dd182ace6021733b9b0383251c",US:"86543f2118d0b1657fe10a8c7098be71fd85ecc9830920bfc8680038052ea463",CL:"4d5c2fb07d2212937d8741d9bd3ec43644b95c24306df8a80be0897856ca0756"}
F=((0x57B704,0x57B722),(0x57B722,0x57B748),(0x57B748,0x57B770),(0x57B770,0x57B86C),(0x57B86C,0x57B940),(0x57B940,0x57B9BA),(0x57B9BA,0x57BA1E));PHYS=(0x57B704,0x57BA88);PATH_ADDR=0x714968;PATH_CELL=0x57BA3C
EASY={0x43CE9E,0x43D0CE,0x43D574};AMBIQ={0x591FAC,0x592014,0x592046,0x5920CC,0x592230,0x5922D6,0x59235E,0x592462,0x592484,0x592556,0x592584,0x5925B4,0x5925E0,0x59262C};IAR={0x43C0E4};FIRST={0x475014,0x4ABE60,0x4C31D8,0x4C3204,0x53A5BE,0x53C6D2,0x591C26}
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
 for name in ("initialize","deinitialize","power_control","configure","enable","disable","dma_start","fifo_threshold_setup","interrupt_service","interrupt_enable","interrupt_disable","interrupt_clear","interrupt_status_get","dma_get_buffer"):
  if f"am_hal_pdm_{name}(" not in header:raise c.AuditError("PDM API header changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 with US.open(newline='',encoding='utf8') as h:up=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=7 or len(up)!=14 or {int(r['stock_target'],0) for r in up}!=AMBIQ or {r['selected_commit'] for r in up}!={COMMIT}:raise c.AuditError("inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if (int(r['stock_start'],0),int(r['stock_end_exclusive'],0))!=(a,z) or len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256'] or c._uncovered((a,z),ii):raise c.AuditError("function closure changed")
  if set(ins)&set(ii):raise c.AuditError("overlap")
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if len(body)!=794 or sh(body)!="914f1ef269e626898cd0ab7d233f7de377965708ab944cf7e827d3bf5853e940" or len(ins)!=288 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="430a5f39994cfca5158dfc5190573070029cbd97dfabe8faef8c7d79a22432b8" or ind:raise c.AuditError("body closure changed")
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=106 or sh(non)!="e802c0e7bf618df4e468d95740a8a5f5c307e26d849e793d2a3032006f7d6285" or sh(c._slice(b,*PHYS))!="a863fd1454b5ba6baaffdc8e7c0ef57cef8dd5772b6c0017d5c5cb600e6b0a72":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="fc47bc960e6c1fc74af111e10092896c3dfe071ad4f056b53f58c9ca3a5aefb0" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="30d2d1be5fff2d343e2bca1e5dd8da8d93c4ad7ee319140a42274b8eaa969a4f":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,AMBIQ,IAR,FIRST)
 if len(calls)!=51 or sum(y in starts for x,y in calls)!=4 or c._pair_digest(calls)!="2cfe264aa95b37f76c4ca38dd33eac56cdd9e7b6d856fc74a2effcdf3749a040" or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(20,19,1,7):raise c.AuditError("provider closure changed")
 instruction_entries=set(ins)-starts;entries=[];strict=[];noncode=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in instruction_entries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=7 or c._pair_digest(entries)!="61b503c55ae2bcf0055f56093a412904574ac6dc89751097a37da86e5b37fb09" or strict!=[(0x67B116,0x57B70E)] or noncode:raise c.AuditError("ingress changed")
 needle=struct.pack('<I',0x57B941);stored=[c.BASE+i for i in range(len(b)) if b.startswith(needle,i)]
 if stored!=[0x438100]:raise c.AuditError("vector pointer changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\driver\pdm\drv_pdm.c":raise c.AuditError("path changed")
 refs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(refs)!=4 or c._pair_digest(refs)!="545b01be3a49cb7f6f14194e06f985cfa730f1f7e0f4a073eb9d4494dd8c63de":raise c.AuditError("path refs changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("drv_pdm.c" in x.get('path','').lower().replace('\\','/') for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"driver\pdm\drv_pdm.c","embedded_third_party_definitions":["__NVIC_EnableIRQ","__NVIC_DisableIRQ","__NVIC_SetPriority"]},"surface":{"linked_functions":7,"ghidra_discovered_functions":7,"path_anchored_functions":0,"raw_path_referencing_functions":2,"body_bytes":794,"physical_bytes":900,"outer_pool_bytes":106,"reachable_instructions":288,"direct_body_calls":51,"internal_direct_body_calls":4,"external_direct_body_calls":47,"indirect_body_calls":0,"direct_bl_entry_sites":7,"stored_function_entry_pointers":1,"strict_interior_ingress":0,"raw_noncode_pseudo_bl":1},"behavior":{"pdm0_irq_handler":True,"dma_double_buffer":True,"inactive_buffer_extract_16bit":True,"output_samples":160,"output_bytes":320},"provider_boundary":{"easylogger_calls":20,"ambiqsuite_pdm_calls":19,"ambiqsuite_pdm_apis":14,"iar_dlib_calls":1,"first_party_board_audio_calls":7,"ambiqsuite_selected_commit":COMMIT,"ambiqsuite_source_sha256":SOURCE_SHA,"ambiqsuite_source_git_blob":SOURCE_BLOB,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
