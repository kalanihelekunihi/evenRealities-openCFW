#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_watchface_layout1.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-dashboard-watchface-layout1-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-watchface-layout1-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-watchface-layout1-provider-map.tsv"
PINS={FM:"e0ebe7c531c815da7ff5a017edd27b753e40b67150aafa0895ca780f5cba3a42",PM:"802342efe73ec375a09d62f8fe3fa3e983d11c383417a19338f891029eebff8e",CL:"5fadfaea43d43966d178dd3afcbfb66e6b45f24410bf70c44f2bb9ebc86b10cd"}
PHYS=(0x5B7934,0x5B873C);PATH_CELL=0x5B849C
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F6AC,0x43F6D6,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x441254,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x44140E,0x44142E,0x44143E,0x44146A,0x44D7B8,0x498668,0x498680,0x499416,0x49942E}
IAR={0x43C0E4,0x44B728};PRINTF={0x4B4728}
FIRST={0x44A19A,0x45FFFE,0x460084,0x47D8CE,0x47D9C4,0x47D9CC,0x48BA78,0x48BA92,0x49C5BC,0x509F8E,0x50F810,0x5B8BC8,0x5B8D20}
CALLBACK_CELLS={0x5B89E0:0x5B84AD,0x5B89E4:0x5B86D3}
RAW_INTERIOR_COLLISION=(0x43A802,0x5B8045)
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e" not in (ROOT/"components/apollo_main/core_overlay/EVIDENCE.md").read_text():raise c.AuditError("printf changed")
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
 if len(F)!=19 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=3500 or sh(body)!="5b376d7c2f4fb058464115a6114eee614e699220d5133d33e5e3529b339e5834" or len(ins)!=1301 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="ae063293b582f657daccf5444de8430e8884d93d627239adc3a83a8741ffce50" or ind!=[0x5B847A,0x5B8490]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=92 or sh(non)!="ee44670edd084a0fab1eac89a01d1e5b36fdb47c0f977a190041085341892076" or sh(c._slice(b,*PHYS))!="d5d1535ce241a8b254d5f8442fbbf9ece69106108b9fe0f7209de67b36023c01":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="4116212778eb2dd27137ceda66073d8169779b6511083d8861b171b03f1380a3" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="3c36fe8468ecee131780fbcba479e48ac2080c93a621b10869d080e3bd3c3279":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,PRINTF,FIRST)
 if len(calls)!=231 or sum(y in starts for x,y in calls)!=16 or c._pair_digest(calls)!="0c44f08012369940128d61ef2c4b6103b315d3ddebad0bccbca61d8fdb217ece" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(20,154,13,10,18):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=20 or c._pair_digest(entries)!="7930f1907466c66d32723ae2927dd4b86fe870db993b7d051331100ee4b5648f" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=13 or c._pair_digest(stored)!="ed551242d7d1d7b3dc5f7cf317fe1895221cb19bfa68474e09f6de3e70f98a07" or interior!=[RAW_INTERIOR_COLLISION]:raise c.AuditError("stored entry closure changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(decoder.disasm(c._slice(b,0x43A800,0x43A804),0x43A800),None)
 if i is None or i.size!=4 or i.mnemonic!="bmi.w" or RAW_INTERIOR_COLLISION[0]!=i.address+2:raise c.AuditError("unaligned raw-word collision proof changed")
 for cell,value in CALLBACK_CELLS.items():
  if struct.unpack_from('<I',b,cell-c.BASE)[0]!=value:raise c.AuditError("callback binding changed")
 if cstring(b,0x6E72E8)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout1.c":raise c.AuditError("path changed")
 pairs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=4 or c._pair_digest(pairs)!="97e119455baa6b16674132f77dd351767f1ba54040faabb581ca4cf4a6a49c6a":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("dashboard_watchface_layout1" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\dashboard_watchface_layout1.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":19,"ghidra_discovered_functions":9,"restored_functions":10,"path_anchored_functions":2,"body_bytes":3500,"physical_bytes":3592,"noncode_bytes":92,"reachable_instructions":1301,"direct_body_calls":231,"internal_direct_body_calls":16,"external_direct_body_calls":215,"indirect_body_calls":2,"bounded_local_callback_targets":2,"direct_bl_entry_sites":20,"stored_function_entry_pointers":13,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":20,"lvgl_calls":154,"iar_dlib_calls":13,"mpaland_printf_calls":10,"first_party_calls":18,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
