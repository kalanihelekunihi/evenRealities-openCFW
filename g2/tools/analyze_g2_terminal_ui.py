#!/usr/bin/env python3
"""Fail-closed object/provider audit for terminal_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-terminal-ui-function-map.tsv";CL=ROOT/"tools/manifests/g2-terminal-ui-closure.tsv";PM=ROOT/"tools/manifests/g2-terminal-ui-provider-map.tsv"
PINS={FM:"3dbb5352e86492dfe5ef5bdef6c2bb1e79cad5d22bc4c3503e3fc9ea6a776387",PM:"8e16ed91f688213f5cd4cec64380c6ceddcda6a4907fc8850374cceee81918df",CL:"75c6f0b4dff00b686322859f6b6633156d9eaa8f0e77a4ecb16e05ab02cd4211"}
PHYS=(0x5E47CC,0x5E7EA4);PATH_CELLS=(0x5E547C,0x5E6000,0x5E6B8C,0x5E72B8,0x5E7E18)
RAW_MUL_COLLISIONS=[(0x5E1CE0,0x5E52F2),(0x5E1CF6,0x5E5308),(0x5E1D16,0x5E5336),(0x5E1D2C,0x5E534C)]
OPEN_BLX=0x5E7CC2
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};CMSIS={0x4490CC}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43E2EA,0x43F09A,0x43F4C0,0x43F506,0x43F6B8,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x441246,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x44146A,0x441488,0x44E498,0x44E4BC,0x44E75E,0x44EA04,0x450500,0x498680,0x49942E,0x49954C,0x597EA6,0x597EE0,0x597F10,0x597F52}
FIRST={0x45A568,0x464C36,0x47D8CE,0x54F380,0x54F50E,0x58966C,0x5896B4,0x5897E0,0x58C426,0x597110,0x597124,0x597318,0x59731E,0x59732A,0x597344,0x5973D4,0x5973DC,0x5973E4,0x597446,0x597452,0x5974D4,0x597544,0x59758E,0x597596,0x597652,0x59769C,0x5CEC72,0x5CED38,0x5CEE08,0x5CEE8C,0x5CEFFA,0x5CF0BA,0x5CF134,0x5E43D2,0x5E7EC4,0x5E7ED4,0x5E7F26,0x5E7F6E,0x5E7FC0,0x5EA2A8,0x5EA30C,0x5EA342,0x5EADD4,0x5EAE2C,0x5EAE94,0x5EB47A,0x5EB4F6,0x5EB576,0x5EB61E,0x5EB646,0x5EB8DA,0x5EBB96,0x5EBBC6,0x5EBD0E,0x5EBFAE,0x5EBFE0,0x5EBFF8,0x5EC190,0x5EC268,0x5EC446,0x5EC73C,0x5EC770,0x5EC82A,0x5EC9C0,0x5ECA32,0x5ECAFA,0x5ECEB2,0x5ED0B8,0x5ED152}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS changed")
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
 if len(F)!=99 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=13200 or sh(body)!="7db84621a6a39b04527a926d9962b4a0ad76f09fe93f35100acf335e1437fef1" or len(ins)!=4858 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="0c2baf9a826518ab10fc4ed9bf72b779e5ea92a8f47261284b9e581135b84c61" or ind!=[OPEN_BLX]:raise c.AuditError("instruction closure changed")
 i=ins[OPEN_BLX]
 if i.mnemonic!="blx" or i.op_str!="r2":raise c.AuditError("open dispatch encoding changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=840 or sh(non)!="fec5543d3061a60c83f7a213cbdbd239c8f585e0dc5153f53994f3165c025ca8" or sh(c._slice(b,*PHYS))!="c1bdc758e4d8353cd31df4328927e81a91b0a8d5fd90358e34ac2022de9dadee":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="960a43363600ca4faf8773ee710efe988c2ff94bb12ded404668d9bace8f579f" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="34d3a0b505d32b7d6fc828b0453bb4479bbb70730c3e5e55e9c242c5abcb88c0":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,CMSIS,FIRST)
 if len(calls)!=808 or sum(y in starts for x,y in calls)!=163 or c._pair_digest(calls)!="37e01924ad81bfa486038b8bcd2752335c368e33e855c8e70d5b6d7202a388cb" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(275,142,9,3,216):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=197 or sum(not(PHYS[0]<=s<PHYS[1]) for s,_ in entries)!=34 or c._pair_digest(entries)!="8da340421db4abbd85d44714e468ed52987c2300aac6b8e509671cc59f9a10b4" or unknown or strict!=RAW_MUL_COLLISIONS:raise c.AuditError("BL ingress changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 for site,target in RAW_MUL_COLLISIONS:
  j=next(decoder.disasm(c._slice(b,site-2,site+2),site-2),None)
  if j is None or j.size!=4 or j.mnemonic!="mul" or site!=j.address+2:raise c.AuditError("unaligned raw-BL collision proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];pseudo=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=135 or c._pair_digest(stored)!="9a440438e4de67483c29d68ac0d4c90a82d68eedd7107cdb3e0fbc8f0967b119" or pseudo:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x706D44)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_ui.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=55 or c._pair_digest(pairs)!="11ad056e47e07b699ec892830b07fe89a8ee4efb5463b4b320b1e11efc814139":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().replace("\\","/").endswith("terminal/terminal_ui.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\terminal\terminal_ui.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":99,"ghidra_discovered_functions":23,"restored_functions":76,"path_anchored_functions":2,"body_bytes":13200,"physical_bytes":14040,"noncode_bytes":840,"reachable_instructions":4858,"direct_body_calls":808,"internal_direct_body_calls":163,"external_direct_body_calls":645,"indirect_body_calls":1,"bounded_local_callback_targets":0,"open_heap_dispatch_sites":1,"direct_bl_entry_sites":197,"external_direct_bl_entry_sites":34,"stored_function_entry_pointers":135,"raw_unaligned_interior_bl_collisions":4,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":275,"lvgl_calls":142,"iar_dlib_calls":9,"cmsis_freertos_calls":3,"first_party_calls":216,"cmsis_freertos_seams":["osKernelGetTickCount"],"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
