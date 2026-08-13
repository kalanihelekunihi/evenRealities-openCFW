#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/Silent_Mode/silent_mode.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import analyze_g2_ui_even_ai as u
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-silent-mode-function-map.tsv";CL=ROOT/"tools/manifests/g2-silent-mode-closure.tsv";PM=ROOT/"tools/manifests/g2-silent-mode-provider-map.tsv"
PINS={FM:"e62e2a4031ffa7a119c5eda94e185143950c6a809c420a03b493fc5242eb3671",CL:"2ffa189fb89b682ae25ad4bc60e5b0ef33bfec6de701c64355d39e4da8d707ab",PM:"2c27359488cbc2c213fbc03b59de1654f965b296820679b05feccdd53a896dc6"}
F=((0x46916c,0x46919e),(0x46919e,0x4691bc),(0x4691bc,0x46921c),(0x46921c,0x469388),(0x469388,0x46946e),(0x46946e,0x469470),(0x469470,0x46949a),(0x46949a,0x469576),(0x469580,0x469ae2),(0x469ae2,0x469b2e));PHYS=(0x46916c,0x469bf4)
EASY={0x43ce9e,0x43d0ce,0x43d574};IAR={0x43c0e4};RTOS={0x454b4c}
FIRST={0x443484,0x44349c,0x4434b4,0x45a568,0x45a8ee,0x45fffe,0x460084,0x46410a,0x4641b6,0x464bb2,0x464c36,0x464f76,0x46b44c,0x49bf24}
PATH_REFS=[0x4691ee,0x469240,0x4692a2,0x469356,0x4693c0,0x46943e,0x4694dc,0x4695a8,0x469916,0x46999c,0x4699f4,0x469a4a,0x469a8e,0x469afe]
ENTRIES=[(0x442d76,0x469ae2),(0x462478,0x46919e),(0x46719c,0x46921c),(0x469276,0x46919e),(0x469394,0x46919e),(0x4694ac,0x46919e),(0x46956c,0x4691bc),(0x46965e,0x46916c),(0x4696a4,0x46916c),(0x46981a,0x46916c),(0x469860,0x46916c),(0x469abe,0x4691bc),(0x469ad4,0x46946e),(0x49835e,0x469ae2),(0x4983e6,0x469ae2),(0x498426,0x469ae2),(0x4c5a52,0x469388),(0x583b6c,0x4691bc),(0x583b74,0x4691bc)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cs(b,a):
 o=a-c.BASE;e=b.find(b'\0',o);return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=10:raise c.AuditError("inventory changed")
 starts=set();inter=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=q._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);inter.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=6 or len(body)!=2488 or sh(body)!="686a948586452d3559a9346ebd25e87c47302bb1f7301c8fe9b784d5659d9d29" or code!=body or len(ins)!=957 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="5149ee976ccefd2200d74cefb72de92ba7f8a77c84bb32763fce78ba33d8e9c9" or ind:raise c.AuditError("instruction closure changed")
 non=c._slice(b,0x469576,0x469580)+c._slice(b,0x469b2e,0x469bf4)
 if sh(c._slice(b,*PHYS))!="e0cb804bfbeb52a212b4821d9f9cb3246603cd6a7d87e5026d90ab070dfc0afe" or sh(non)!="f44040e26ad6b383aaf89e282a51d752a8115e1d7953bd6b6689b6c1fe88318e":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x46915c,PHYS[0]))!="2057756185d816f89aa6d7ae23ee60079eac82f6dfa16b9774a16f00aa17b962" or sh(c._slice(b,PHYS[1],0x469c04))!="131f639064d7395f437fed53ac2672b8ec91285e35422c01ffd305d0340bbfd7":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts);lv=set(ext)&u.LVGL
 if len(calls)!=178 or sum(y in starts for _,y in calls)!=10 or c._pair_digest(calls)!="c9919864a3a0677aeec0ef0444eced5df7d8a4c93cb5e7ae60fdaee74508eb12" or set(ext)!=EASY|IAR|RTOS|lv|FIRST:raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in s) for s in (EASY,IAR,RTOS,lv,FIRST))!=(70,1,1,70,26):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if entries!=ENTRIES or c._pair_digest(entries)!="ccfd0f25a869438dec1176d8a2bcd64808e12013c4cb23727c117e17e197b112" or strict:raise c.AuditError("entry topology changed")
 enc=starts|{x|1 for x in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x6a4654,0x46949b),(0x6a4658,0x469581),(0x793d0d,0x469471)]:raise c.AuditError("stored callbacks changed")
 if t.literal_references(b,0x469b38)!=PATH_REFS or cs(b,0x6fd394)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\Silent_Mode\silent_mode.c":raise c.AuditError("path changed")
 for a,s in {0x77beb4:"SilentMode_SetStatus",0x771ce8:"SilentMode_SetStatusFromApp",0x75a464:"SilentMode_ToggleByLocalLongPress",0x7656b0:"silent_mode_common_data_handler",0x7656d0:"silent_mode_ui_event_handler",0x771d20:"get_silent_mode_ui_showing"}.items():
  if cs(b,a)!=s:raise c.AuditError("symbol changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("silent_mode" in x.get("path","").lower() for x in overlay["sources"]):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\Silent_Mode\silent_mode.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":10,"ghidra_discovered_functions":7,"restored_functions":3,"path_anchored_functions":6,"body_bytes":2488,"physical_bytes":2696,"noncode_bytes":208,"reachable_instructions":957,"direct_body_calls":178,"internal_direct_body_calls":10,"external_direct_body_calls":168,"indirect_body_calls":0,"direct_bl_entry_sites":19,"stored_entry_pointers":3},"behavior":{"common_data_record_id":0x10a,"common_data_payload_bytes":1,"settings_status_offset":0x15,"stored_ui_callbacks":3,"local_long_press_toggle":True,"role_sensitive_remote_transition":True},"provider_boundary":{"easylogger_calls":70,"lvgl_calls":70,"freertos_vtaskdelay_calls":1,"iar_memset_calls":1,"first_party_calls":26,"direct_cmsis_freertos_calls":0,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","easylogger_commit":"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
