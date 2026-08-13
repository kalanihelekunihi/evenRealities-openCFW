#!/usr/bin/env python3
"""Fail-closed object/provider audit for terminal_session_list_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-terminal-session-list-ui-function-map.tsv";CL=ROOT/"tools/manifests/g2-terminal-session-list-ui-closure.tsv";PM=ROOT/"tools/manifests/g2-terminal-session-list-ui-provider-map.tsv"
PINS={FM:"e2ca41220df2ad9c59e26136b29e79a292b0dda347e409f2bd2765ee903bbd75",PM:"e0937a61479f482942d262c5f960a9fd37fe2c20c2ee0e12a97e1f78d9cb8e92",CL:"85038ab2ac1aa9736cdacea3292a69858a0d21e8dff8706c8d344e6ff3ae94ea"}
PHYS=(0x5ED1EC,0x5EDA64);PATH_CELL=0x5ED9D8
EASY={0x43CE9E,0x43D0CE,0x43D574};LVGL={0x43DED4,0x43DFA4}
FIRST={0x59732A,0x5973B2,0x5973D4,0x5973DC,0x597572,0x59758E,0x5CEE8C,0x5CEF14,0x5CEF8C,0x5E43D2,0x5E5442,0x5E5484,0x5E57C6,0x5EAE2C,0x5EBBC6,0x5EC268,0x5EC770,0x5EC9C0,0x5ECA3E,0x5ECA44,0x5ECA64,0x5ECAAC,0x5ECC1A,0x5ECE4C,0x5ECEB2,0x5ECEF6,0x5ED1D6}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=10 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=1966 or sh(body)!="562ef9adb9ccbf670331bc46e1c78c120c2e67adcc1b448ef97812e0ca73cb06" or len(ins)!=738 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="6541d40cad974ef3f22d8edfa6761afeacab852a0f84980fec40433d8e1d19db" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=202 or sh(non)!="e30a060b0c491fd1438d3a4d76b160690702f8a3f39b30b83e2ee7950aced5c9" or sh(c._slice(b,*PHYS))!="f264eaf19cf21354df052ec9e891a0f37d1edfe397195f846247841e6e7fb9a5":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="2e5d13e0dfc12dc33838699c27af7d0ad6c627bffca602e3d25b293d2620ea03" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="45c4dd1e6d0f57a119670756a2753e3337b6cd050a1fc26314b2979b0d0244fc":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,FIRST)
 if len(calls)!=134 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!="6c4abe31a97553a804d5848380857223517cadcffc8e15adc920d56fff3fcf94" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(70,5,56):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=3 or sum(not(PHYS[0]<=s<PHYS[1]) for s,_ in entries)!=0 or c._pair_digest(entries)!="0f84ca4a50c55908c8b7f93c0512ad678d5749800070c952e7537ca679a10e7c" or unknown or strict:raise c.AuditError("BL ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];pseudo=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=25 or c._pair_digest(stored)!="449fdf2afe1b876b4a3322b6f403c488a71f306160128b56abb1b1a5bb10f076" or pseudo:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6F0498)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_session_list_ui.c":raise c.AuditError("path changed")
 pairs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=14 or c._pair_digest(pairs)!="d673da17439f70a8c3c1ae3548ae50143ac951ca8cca963c177785ced6fe7875":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().replace("\\","/").endswith("terminal/terminal_session_list_ui.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\terminal\terminal_session_list_ui.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":10,"ghidra_discovered_functions":2,"restored_functions":8,"path_anchored_functions":2,"body_bytes":1966,"physical_bytes":2168,"noncode_bytes":202,"reachable_instructions":738,"direct_body_calls":134,"internal_direct_body_calls":3,"external_direct_body_calls":131,"indirect_body_calls":0,"direct_bl_entry_sites":3,"external_direct_bl_entry_sites":0,"stored_function_entry_pointers":25,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":70,"lvgl_calls":5,"first_party_calls":56,"cmsis_freertos_calls":0,"freertos_kernel_calls":0,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
