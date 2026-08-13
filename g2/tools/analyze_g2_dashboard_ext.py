#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard/dashboard_ext.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-dashboard-ext-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-ext-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-ext-provider-map.tsv"
PINS={FM:"7b606194c62048c836c73ae2962cb2cd7b24dc82dc7ddac98ceacdf04dff9f5a",CL:"ced28c8a087c26ad71862da7e3bbf850d1ad2a915faed300405a23adfefddd71",PM:"77022839cebbe492b9fc0ca90b1ad598f1fe89ce1841532fd5682fed93e5120b"}
PHYS=(0x50083E,0x5026BC);PATH_CELLS=(0x501184,0x501D18,0x502628)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44B5A0};FILE={0x474550,0x4745F4,0x474634,0x474682,0x474814,0x474870,0x47498C,0x474A02};NANOPB={0x48949C,0x48F49C,0x490120,0x4905F4,0x490C32};FREERTOS={0x454B4C}
FIRST={0x45A568,0x45BCA0,0x464CBA,0x465480,0x475B14,0x475C1A,0x500824,0x558376,0x558632,0x55876A}
PSEUDO=[(0x544611,0x5011FB),(0x55C09D,0x5011FB),(0x5EF5C3,0x5020F9),(0x644997,0x501FFF),(0x77699E,0x502007),(0x777706,0x502007),(0x77C176,0x502007),(0x77C18E,0x502007),(0x77CCB6,0x502007),(0x785CFA,0x502007),(0x785DDA,0x502007),(0x785FEA,0x502007),(0x78892A,0x502007)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 pins=[("easylogger","a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"),("littlefs","0494ce7169f06a734a7bd7585f49a9fa91fa7318"),("nanopb","98bf4db69897b53434f3d0ba72e0a3ab1a902824"),("freertos-kernel","def7d2df2b0506d3d249334974f51e427c17a41c")]
 for name,commit in pins:
  j=json.loads((ROOT/f"third_party/{name}/PROVENANCE.json").read_text())
  if j["upstream"]["selected_commit"]!=commit:raise c.AuditError(f"{name} changed")
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
 if len(F)!=16 or sum(r['source_path_anchor']=='yes' for r in rows)!=6:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=5904 or sh(body)!="6a209b6a1c7a301cfd977c9e635f7a7615fdb61b5c68573904f233273ae5abaa" or len(ins)!=2142 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="1018cdc7256520190080871549b9e3e6476e05d7a22da6572ec1781d3bddc88c" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=1902 or sh(non)!="e30190413a23e6c9e8f3288bd02b1ab266dacd79f29eb2f44cd596e15c3fdd97" or sh(c._slice(b,*PHYS))!="686e26de89cc4d7649365f048d5fa7319f38b76b7b352adb20a8f4cb834dd76f":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="e3ef031ac2e178d5f5d6da98f210f3ae7e9367e9b8807a5d8cb5db90d7aa5a09" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="53a96c6cb22abcbba02b38d201bc4f32ea00fba5b40b42f2fb324ea55e69b2f0":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,FILE,NANOPB,FREERTOS,FIRST)
 if len(calls)!=315 or sum(y in starts for x,y in calls)!=24 or c._pair_digest(calls)!="b82f51a2e05ef687e468e259927afa59e47e6dff85c0539459dbc69835d6c736" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(220,18,16,5,3,29):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=32 or c._pair_digest(entries)!="943176ddbd0594a9977c8bd6976167486afc69ac9e9fb100fb57fdb824b4e654" or strict:raise c.AuditError("BL ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior!=PSEUDO or c._pair_digest(interior)!="805d75689852310bdd8424c339ec7706b6fbc2a29fcaf15273b21f02b7d2f589":raise c.AuditError("stored-word closure changed")
 if any((v&~1) not in ins for a,v in PSEUDO):raise c.AuditError("pseudo-pointer target changed")
 if cstring(b,0x6F9914)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_ext.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=56 or c._pair_digest(pairs)!="150cd74304d2483de415975e04d9775a15d4151a36b5db03873ffe2570963f9a":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("dashboard_ext" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\dashboard_ext.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":16,"ghidra_discovered_functions":6,"restored_functions":10,"path_anchored_functions":6,"body_bytes":5904,"physical_bytes":7806,"noncode_bytes":1902,"reachable_instructions":2142,"direct_body_calls":315,"internal_direct_body_calls":24,"external_direct_body_calls":291,"indirect_body_calls":0,"direct_bl_entry_sites":32,"stored_function_entry_pointers":0,"unaligned_word_pseudo_pointers":13,"strict_interior_ingress":0},"behavior":{"dashboard_message_dispatch":True,"peer_role_transfer":True,"file_lifecycle_and_transport":True,"nanopb_record_processing":True,"dashboard_resource_lookup":True},"provider_boundary":{"easylogger_calls":220,"iar_dlib_calls":18,"source_owned_file_runtime_calls":16,"nanopb_calls":5,"freertos_calls":3,"first_party_calls":29,"nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
