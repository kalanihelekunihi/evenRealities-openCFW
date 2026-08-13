#!/usr/bin/env python3
"""Fail-closed object/provider audit for even_ai_animation.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-even-ai-animation-function-map.tsv";PM=ROOT/"tools/manifests/g2-even-ai-animation-provider-map.tsv";CL=ROOT/"tools/manifests/g2-even-ai-animation-closure.tsv"
PINS={FM:"25020605663ad80063cec5040a85259a0113d176bd74e894202192cb8c0e523c",PM:"9804689d908df360f067d2f3df00c3860bd233a454292d42faf72ec2e4b20668",CL:"407ffd01cd0707775fc263dcbe84431046eea0aba11856871cbbafed87005bb1"}
PHYS=(0x5537CC,0x554080);PATH_CELLS=(0x553FFC,)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};LVGL={0x43DED4,0x43DFA4};CMSIS={0x4490CC}
FIRST={0x45A568,0x463E9A,0x463EA6,0x463EEE,0x463F34,0x463F5C,0x463FA4,0x464BB2}
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
 if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 if cmsis["upstreams"]["cmsis_5"]["selected_commit"]!="2b7495b8535bdcb306dac29b9ded4cfb679d7e5c":raise c.AuditError("CMSIS_5 changed")
 linked=(ROOT/"tools/manifests/cmsis-freertos-v10.5.1-linked-function-map.tsv").read_text()
 if "osKernelGetTickCount\t0x004490CC\t0x004490E2\t22\te71b740a75cc5b6be604febe03034833fd10def82df65b66e453bcca1402564d\t144\tpublic CMSIS-RTOS2 API" not in linked:raise c.AuditError("CMSIS linked seam changed")
 iar=(ROOT/"docs/research/iar-dlib-runtime-census.md").read_text()
 if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:raise c.AuditError("IAR changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=5 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2036 or sh(body)!="66add97130c741ac0826510fbf2e682bd282a24b64898dbfbf8c278eaeb4cdea" or len(ins)!=765 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="e4192d83de1e0111f216f7d2ad1387315b156a6dcfbfadfe773693cc30034a31" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=192 or sh(non)!="39dce3a251349bfb46a19339dbeb2babf2d6b60e06eaa708d426d4e709c7731a" or sh(c._slice(b,*PHYS))!="f88181d5c3a1904f72fd7294e76e60b4a990eb6ad279adbae0dbc6110e09e7e6":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="cd8debf19b133e94742ee82a64e0713d1b84cb279a2de6fffd885f2a3be97f18" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="45677d983407186d40529164b5e20b593586f5d14f5838d158b3c6ff6a935ff7":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,CMSIS,FIRST)
 if len(calls)!=80 or sum(y in starts for x,y in calls)!=1 or c._pair_digest(calls)!="a5e00b9e71398b68f2d0fddfeed723b2a5df5a990a3c1cfe2bca1bdd902dd206" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(60,1,2,1,15):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=28 or c._pair_digest(entries)!="544de840db04adf151ab6b86e63a2573f70b535fdc71ca6e66061c342d2a512f" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior:raise c.AuditError("stored/interior ingress changed")
 pairs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(pairs)!=12 or c._pair_digest(pairs)!="9bd2692118d8d11e5b66e1607e04692da842f70160b00047a84204cfa60ca471":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("even_ai_animation" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenAI\even_ai_animation.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":5,"ghidra_discovered_functions":2,"restored_functions":3,"path_anchored_functions":2,"body_bytes":2036,"physical_bytes":2228,"noncode_bytes":192,"reachable_instructions":765,"direct_body_calls":80,"internal_direct_body_calls":1,"external_direct_body_calls":79,"indirect_body_calls":0,"direct_bl_entry_sites":28,"stored_function_entry_pointers":0,"raw_instruction_word_interior_collisions":0,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":60,"iar_dlib_calls":1,"lvgl_calls":2,"first_party_calls":15,"cmsis_freertos_calls":1,"cmsis_freertos_seams":["osKernelGetTickCount"],"freertos_kernel_calls":0,"historical_even_ai_animation_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
