#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-dashboard-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-provider-map.tsv"
PINS={FM:"2996f4d3f50ed5151881fd938c1d17a18471de49521fbc1f99ab57bd6620df64",PM:"acb0652dc4730e9d2343a1fdb6e050f15f7924c62d62c5b807fb961a1e461415",CL:"12101bc4376334fc9830236a70c76ad4c45bf92cd82b73a19d15d80c5392513c"}
PHYS=(0x49C070,0x49EAD8);PATH_CELLS=(0x49CB2C,0x49CE00,0x49DB50,0x49E440,0x49EA64)
EMBEDDED_POOLS={0x49CE14:[(0x49DB46,0x49DB5C),(0x49DBF6,0x49DC10)]}
ZERO_INGRESS={0x49E144}
RAW_BL_COLLISION=(0x4A5BBC,0x49C1CC,0x4A5BBA)
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43E2BC,0x44102E,0x44104C,0x441068,0x44127E,0x44129E,0x4412EC,0x4413CE,0x4413DE,0x4413FE,0x44140E,0x44BDEA,0x44DCE2,0x44DDEA,0x488F6A,0x498B50}
IAR={0x439BE4,0x43C0E4,0x44B5A0};CMSIS={0x44971C,0x4497B6,0x44981C};NANOPB={0x48949C}
FIRST={0x443484,0x4434D0,0x44A19A,0x44A1C6,0x45A568,0x45A570,0x45AACA,0x464BB2,0x464F76,0x466010,0x466016,0x466500,0x46B44C,0x47121C,0x4974D4,0x49BE04,0x4ABCC6,0x4ABD14,0x4AEA56,0x4AEAA4,0x4E1A5E,0x4E1AAC,0x4E7712,0x4E8000,0x4E814C,0x4E8DEC,0x4E923C,0x4E9E06,0x4E9E32,0x4E9FDE,0x4ED80A,0x4EFA78,0x4F4F3C,0x4F509A,0x4FB1F2,0x4FDF08,0x4FDF74,0x4FE318,0x4FEC98,0x4FEDCC,0x4FF09C,0x4FF98A,0x4FFA70,0x4FFBD8,0x4FFE14,0x500378,0x500396,0x500660,0x501066}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
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
 if len(F)!=24 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  if c._uncovered((a,z),ii)!=EMBEDDED_POOLS.get(a,[]):raise c.AuditError("flow coverage changed")
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 emb=b''.join(c._slice(b,a,z) for a,z in EMBEDDED_POOLS[0x49CE14])
 if len(body)!=10040 or sh(body)!="ac002d7d0009ef47bf8c5d46fe419dcb21ac53887b780e86a304d80175ece98d" or len(emb)!=48 or sh(emb)!="aecaf6e22841dc6756c0931db1f780239ca17148a3a8215e57ebfee97c1e0f65" or len(ins)!=3580 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="98dc39221ec4f9827a1a13462b24282ab976cfe2501124d38c124b284bc0b72c" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=816 or sh(non)!="24504891c1168d813eb65f47819f626c9de2fbb23c0fe863b2f175e933e7ded1" or sh(c._slice(b,*PHYS))!="1c8d1e7f68067e7c12aaab9dc5561d47150492bea6a362034c4ade39ecf23497":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="eab423064db5b0a2d08f3b106a5af9b54888d00478c416bfebbb2763b703b5d9" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="7466a1bda4cac083e733a87a3826b6aeb5bfe9bd1f571b375d0a5439e3f26ec5":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,CMSIS,NANOPB,FIRST)
 if len(calls)!=617 or sum(y in starts for x,y in calls)!=19 or c._pair_digest(calls)!="ff8dd08a812811c408402e79e291b47ed4047734633e060f628dfd56ecda8566" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(370,43,48,13,1,123):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=35 or sum(not(PHYS[0]<=s<PHYS[1]) for s,_ in entries)!=16 or c._pair_digest(entries)!="659fd916ea588ec7165ac1d66e36babda864910d2365b3652d18144087887843" or unknown or strict!=[RAW_BL_COLLISION[:2]]:raise c.AuditError("BL ingress changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(decoder.disasm(c._slice(b,RAW_BL_COLLISION[2],RAW_BL_COLLISION[2]+4),RAW_BL_COLLISION[2]),None)
 if i is None or i.size!=4 or i.mnemonic!="udiv" or RAW_BL_COLLISION[0]!=i.address+2:raise c.AuditError("unaligned raw-BL collision proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];pseudo=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=6 or c._pair_digest(stored)!="f98845728741f544614e563721f758f88f6842debd5ed2f7b4c31628841a97e6" or len(pseudo)!=6 or c._pair_digest(pseudo)!="ec2020c7b44b0c5b51da206c3c7add6e6570d5a2beab77571913a7acecc6e79e" or any(a%4==0 for a,v in pseudo):raise c.AuditError("stored entry closure changed")
 if any(y in ZERO_INGRESS for x,y in entries) or any((v&~1) in ZERO_INGRESS for a,v in stored):raise c.AuditError("zero-ingress function gained an entry")
 if cstring(b,0x701624)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=74 or c._pair_digest(pairs)!="4ad6867d9f1acf6dd3493acf0fc2823551cf93f81901d2a8c3c82df7683b8ce6":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().replace("\\","/").endswith("dashboard/dashboard.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\dashboard.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":24,"ghidra_discovered_functions":3,"restored_functions":21,"path_anchored_functions":2,"zero_ingress_recovered_functions":1,"body_bytes":10040,"physical_bytes":10856,"noncode_bytes":816,"embedded_literal_pool_regions":2,"embedded_literal_pool_bytes":48,"reachable_instructions":3580,"direct_body_calls":617,"internal_direct_body_calls":19,"external_direct_body_calls":598,"indirect_body_calls":0,"direct_bl_entry_sites":35,"external_direct_bl_entry_sites":16,"stored_function_entry_pointers":6,"unaligned_stored_interior_pseudo_pointers":6,"raw_unaligned_interior_bl_collisions":1,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":370,"lvgl_calls":43,"iar_dlib_calls":48,"cmsis_freertos_calls":13,"nanopb_calls":1,"first_party_calls":123,"cmsis_freertos_seams":["osMutexNew","osMutexAcquire","osMutexRelease"],"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
