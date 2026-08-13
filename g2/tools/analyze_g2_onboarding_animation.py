#!/usr/bin/env python3
"""Fail-closed object/provider audit for onboarding_animation.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-onboarding-animation-function-map.tsv";PM=ROOT/"tools/manifests/g2-onboarding-animation-provider-map.tsv";CL=ROOT/"tools/manifests/g2-onboarding-animation-closure.tsv"
PINS={FM:"695e78fc72f2af43b08579343a3a2a79803cb0e3c2943bc34a3bf7299e196165",PM:"8c36f43b312fcf04bdb43de0a77b3a1f4bc24d750ae76b8632984f1053ed24ff",CL:"5ac9bfc3f65bd2e6134f39d56070bc46d4c60e0d8b1cbe4c878a35ee958e4b83"}
PHYS=(0x50F8CC,0x5100A0);PATH_CELLS=(0x50FEB8,);THUNK=(0x51009C,0x474D16)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4};NANOPB={0x48949C};HEAP={0x474CD2}
LVGL={0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F6B8,0x44104C,0x44CF98,0x44D0F0,0x44E3CA,0x4515D2}
FIRST={0x463C68,0x463E1C,0x463E9A,0x463EA6,0x463EEE,0x463F34,0x541B74}
RAW_ENTRY=(0x631937,0x50FF0E);INTERIOR=[(0x630155,0x50FCCF),(0x63033E,0x50FCDF),(0x630BC8,0x50FDFF),(0x6319FC,0x50FF0D)]
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
 tlsf=(ROOT/"third_party/tlsf/README.openCFW.md").read_text()
 if "a1f743ffac0305408b39e791e0ffb45f6d9bc777" not in tlsf or "deff9ab509341f264addbd3c8ada533678591905" not in tlsf:raise c.AuditError("TLSF interval changed")
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
 if len(F)!=11 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[];tails=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  if a==THUNK[0]:
   dec=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);tt=list(dec.disasm(raw,a))
   if len(tt)!=1 or tt[0].mnemonic!="b.w" or tt[0].size!=4 or tt[0].op_str!="#0x474d16":raise c.AuditError("heap-free tail thunk changed")
   ins[a]=tt[0];tails.append((a,THUNK[1]))
  else:
   ii,cc,dd=q._recover_function(b,a,z);uncovered+=c._uncovered((a,z),ii);ins.update(ii);calls+=cc;ind+=dd
  inter.update(range(a+2,z,2));body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=1598 or sh(body)!="11261a6d2b40d3320a29b41512e33f5affcbcf09b01cee8a0be0870647f65dc0" or len(ins)!=630 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="c42fcca326d89c34a9f311521717165a7729290517b28378cb5a924750b1a717" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=406 or sh(non)!="78e2fe8a2a72474afba2cbb2a27056592812e0a98b3f56eb03eea044457e715e" or sh(c._slice(b,*PHYS))!="7155c3ddac6eaaf4dd5b03bdb3ace7ed1b969c112020dbe486af72d4633aa2c6":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="4c0bca887a2399fa82fe7174a760699901e0ef1e1fc796fe68877de4c0fa5b4c" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="bcb22da9ebf583ac63124e0dc8df691f8679227aeaef06ce089fbc77cf105577":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,NANOPB,HEAP,FIRST)
 if len(calls)!=83 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!="0e5a7b302680c3e1b3c88d5bc7454f609b2e559882843b5a0d6f745163b5731d" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(30,11,21,1,1,16):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=35 or c._pair_digest(entries)!="bdf8a8fb68675cde41840849a3113e705b2d505ef1d2124cbf3e9aa66ff6347c" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=[RAW_ENTRY] or c._pair_digest(stored)!="f6c16f44d2d56ec7f87559f6f6d23d680e10e99262a4b2cbc89c223ebc8e7609" or RAW_ENTRY[0]%2!=1:raise c.AuditError("stored entry closure changed")
 if interior!=INTERIOR or c._pair_digest(interior)!="f9ad6d8c28a8b57252bbf4c0be4320b8f55fd14a9364c392ef54bc944f4c4d51":raise c.AuditError("interior collision closure changed")
 pairs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(pairs)!=6 or c._pair_digest(pairs)!="8c0d2332af5885f3a82c5965d52fb83c94b658104718935778db438bc735e687":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("onboarding_animation" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\onboarding\onboarding_animation.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":11,"ghidra_discovered_functions":4,"restored_functions":7,"path_anchored_functions":4,"body_bytes":1598,"physical_bytes":2004,"noncode_bytes":406,"reachable_instructions":630,"direct_body_calls":83,"internal_direct_body_calls":3,"external_direct_body_calls":80,"indirect_body_calls":0,"tail_branch_sites":1,"direct_bl_entry_sites":35,"stored_function_entry_pointers":0,"raw_instruction_word_entry_collisions":1,"raw_instruction_word_interior_collisions":4,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":30,"iar_dlib_calls":11,"lvgl_calls":21,"nanopb_calls":1,"source_owned_heap_wrapper_calls":2,"first_party_calls":16,"cmsis_freertos_calls":0,"freertos_kernel_calls":0,"historical_onboarding_animation_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
