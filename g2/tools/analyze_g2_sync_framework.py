#!/usr/bin/env python3
"""Fail-closed object/provider audit for framework/sync/sync_framework.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-sync-framework-function-map.tsv";CL=ROOT/"tools/manifests/g2-sync-framework-closure.tsv";PM=ROOT/"tools/manifests/g2-sync-framework-provider-map.tsv"
PINS={FM:"974afc55304b6d549a0bf2a0b50471f37c8c2e5545276cee30584575d806b075",CL:"a1758ff8a99d7873a480b1a90ed50c726661dae265bec6676fcc5d87a7d16fe7",PM:"a5fbc5032d02cac6a86141284f373f7c96fc03c101a9c2c1dfbd724ebfa00614"}
PHYS=(0x45A578,0x45EC7C);PATH_CELLS=(0x45B0FC,0x45BC84,0x45C00C,0x45CD74,0x45D7CC,0x45E010,0x45E8BC,0x45EC20)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4};HEAP={0x474CD2,0x474D16}
CMSIS={0x4490E2,0x4493B0,0x449498,0x4494D8,0x449522,0x4495E4,0x44971C,0x4497B6,0x44981C,0x44989A,0x44994E,0x4499B8,0x449A32,0x449ABE,0x449B3C}
FREERTOS={0x454B4C,0x5FA0A4};TINYFRAME={0x4917D2,0x491962,0x491B9A,0x49225A,0x492266,0x492278,0x492280,0x492288}
AMBIQ={0x480F0C,0x480F8A};NANOPB={0x48949C};THREAD_POOL={0x491184,0x49137A};DELAY={0x4910F4}
FIRST={0x442524,0x442BA8,0x442D64,0x4441EC,0x4442D0,0x4443CC,0x4444B8,0x4445A4,0x45A558,0x45A568,0x460424,0x464B2E,0x464BB2,0x464C36,0x464CBA,0x465748,0x46B334,0x46B44C,0x46C630}
EXPECTED_IND=[0x45ADF0,0x45D6F4,0x45D7BA,0x45D9A4,0x45DA7E,0x45DC0C,0x45DD2E,0x45DEBC,0x45DFC6,0x45E1F4,0x45E308,0x45E41A,0x45E528,0x45E64C]
EXPECTED_STORED=[(0x45B130,0x45A6D1),(0x45B148,0x45A80B),(0x45B6DC,0x45A9E7),(0x45B848,0x45ABC5),(0x45CD84,0x45BC07),(0x45DC74,0x45C059),(0x45DD4C,0x45D303),(0x45DFF4,0x45ADE9),(0x45EB88,0x45ADE9),(0x45EBD4,0x45E025),(0x45EBD8,0x45E5A5),(0x45EBE8,0x45DAA1),(0x45EBEC,0x45DC85),(0x45EBF0,0x45D7E5),(0x45EBF4,0x45D9CD),(0x45EBF8,0x45DD69),(0x45EBFC,0x45DF25),(0x45EC00,0x45D555),(0x45EC04,0x45D711),(0x45EC34,0x45B14D),(0x45EC38,0x45B589),(0x45EC3C,0x45B6E5),(0x45EC5C,0x45ADF5),(0x45EC60,0x45B851)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def selected(path,*keys):
 x=json.loads(path.read_text())
 for k in keys:x=x[k]
 return x
def provenance():
 if selected(ROOT/"third_party/easylogger/PROVENANCE.json","upstream","selected_commit")!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if selected(ROOT/"third_party/cmsis-freertos/PROVENANCE.json","upstreams","cmsis_freertos","selected_commit")!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 if selected(ROOT/"third_party/tinyframe/PROVENANCE.json","upstream","selected_commit")!="eb75483e035916ef9f3e9fce0d2ae389cb09785f":raise c.AuditError("TinyFrame changed")
 if selected(ROOT/"third_party/ambiqsuite-apollo510/PROVENANCE.json","upstream","selected_commit")!="5efc0228528a8adce5eae0d226fac85d2551eb3b":raise c.AuditError("AmbiqSuite changed")
 if selected(ROOT/"third_party/nanopb/PROVENANCE.json","upstream","selected_commit")!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
 if "deff9ab509341f264addbd3c8ada533678591905" not in (ROOT/"third_party/tlsf/README.openCFW.md").read_text():raise c.AuditError("TLSF changed")
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
 if len(F)!=43 or sum(r['source_path_anchor']=='yes' for r in rows)!=23:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];interval=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("function interval changed")
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;interval+=raw
 calls.sort();ind.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(interval)!=16960 or sh(interval)!="4226c1a64194a2f199441f1660cd8a459ba2eecdad13c742625598391a1942f7" or len(code)!=16816 or sh(code)!="453c42d6ead8de2e161854dfa6154e1544a9b03fb8d52591eae7f916b7b95550" or len(ins)!=6083 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="3a52b947a96b0a4cdb987202b3a0399cc61bda5c1bccdd733756bbb18871f735" or ind!=EXPECTED_IND:raise c.AuditError("instruction closure changed")
 mask=bytearray(PHYS[1]-PHYS[0])
 for a,i in ins.items():
  for j in range(i.size):mask[a-PHYS[0]+j]=1
 rawphys=c._slice(b,*PHYS);non=bytes(v for v,m in zip(rawphys,mask) if not m)
 if len(non)!=1364 or sh(non)!="7c8585692ea553a730e01bc474cc7c4ef3d9cc58f4090c44cfd6f6dc782a1487" or sh(rawphys)!="d8b6f57b8f37d3b36f0a0cabca37cf674524b4a5b4edc22ac1dd6dfbd2a1b7f9":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="14d494d05a0b2c2083b5515d33096198ea0f6ee0aee4c4f37331ee216a3a96fb" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="3bcd2db4ab8aad79a5475243a8ec8fde47924c1cb8bf74e3ef78dc56dff66129":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,TINYFRAME,AMBIQ,NANOPB,IAR,HEAP,THREAD_POOL,DELAY,FIRST)
 if len(calls)!=1070 or sum(y in starts for x,y in calls)!=19 or c._pair_digest(calls)!="d3e9a8d8f6711bb88492ef2d3749d9ca1727b63151793118e85c9ed86e5c921c" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(825,35,4,26,2,1,17,86,18,1,36):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=79 or c._pair_digest(entries)!="d08ceb6fa8569007c79a3dfa41c92d7406b11550507ffb7f3e160a33c752e066" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=EXPECTED_STORED:raise c.AuditError("stored entries changed")
 if cstring(b,0x705FB8)!=r"D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_framework.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=165 or c._pair_digest(pairs)!="d89ca32c8e70661259181ff29649d33b7f385e541a30ff65e740c1d3dc38c98f":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().endswith("sync_framework.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"framework\sync\sync_framework.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":43,"ghidra_discovered_functions":23,"restored_functions":20,"path_anchored_functions":23,"function_interval_bytes":16960,"body_bytes":16816,"physical_bytes":18180,"noncode_bytes":1364,"reachable_instructions":6083,"direct_body_calls":1070,"internal_direct_body_calls":19,"external_direct_body_calls":1051,"indirect_body_calls":14,"direct_bl_entry_sites":79,"stored_entry_pointers":24,"strict_interior_ingress":0},"behavior":{"role_and_gpio_selection":True,"tinyframe_listener_dispatch":True,"multipart_transport":True,"schedule_and_timeout_management":True,"cmsis_thread_timer_queue_and_sync_use":True,"bounded_callback_tables":True},"provider_boundary":{"easylogger_calls":825,"cmsis_freertos_calls":35,"freertos_kernel_calls":4,"tinyframe_calls":26,"ambiqsuite_calls":2,"nanopb_calls":1,"iar_dlib_calls":17,"source_owned_heap_wrapper_calls":86,"thread_pool_calls":18,"delay_wrapper_calls":1,"first_party_calls":36,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","tinyframe_commit":"eb75483e035916ef9f3e9fce0d2ae389cb09785f","ambiqsuite_commit":"5efc0228528a8adce5eae0d226fac85d2551eb3b","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
