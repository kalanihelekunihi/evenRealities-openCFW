#!/usr/bin/env python3
"""Fail-closed object/provider audit for platform/audio/service_audio.c."""
import csv,hashlib,importlib.util,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-service-audio-function-map.tsv";PM=ROOT/"tools/manifests/g2-service-audio-provider-map.tsv";CL=ROOT/"tools/manifests/g2-service-audio-closure.tsv"
PINS={FM:"baa688b3a648a80141edfcd4a902e47723fe5c0e854510b78d2e2c0b1937d0fc",PM:"f7c4ae2b0560ae0b211c84531fd8966a757aca52357a57d1b1fb548cdff32e8b",CL:"1ed5f734158df74d30bc4b2a5fb383c30b31130ee9c29d93005f2ffb9b8c905f"}
F=((0x57A900,0x57A926),(0x57A926,0x57A940),(0x57A940,0x57AB78),(0x57AB78,0x57ACD0),(0x57ACD0,0x57ADF8),(0x57ADF8,0x57AF8C),(0x57AF8C,0x57AFBA),(0x57AFBA,0x57AFC6),(0x57AFC6,0x57B0CA),(0x57B0CA,0x57B12C),(0x57B12C,0x57B1F0),(0x57B1F4,0x57B312),(0x57B312,0x57B352),(0x57B352,0x57B378))
PHYS=(0x57A900,0x57B444);NONCODE=((0x57B1F0,0x57B1F4),(0x57B378,0x57B444));PATH_ADDR=0x7053C4;PATH_CELL=0x57B384
EASY={0x43CE9E,0x43D0CE,0x43D574,0x43DACC};IAR={0x439BE4,0x43C0E4,0x44B728};CMSIS={0x4490CC};LC3={0x590E64,0x590F78,0x591374,0x59138A};ALGO={0x5915DC,0x591BFC};FILE={0x474550,0x4745F4,0x474682};LFS={0x4CFA8A,0x4CFC5C};FIRST={0x475D78}
REG=[(0x58F6EA,0x58F5E0),(0x58F736,0x58F4E4),(0x58F7F2,0x58F5E0)];REG_LITERALS={0x58F8A0:0x58F5E1,0x58F8AC:0x58F4E5};PSEUDO=[(0x5FA9D6,0x57AD42)]
def sh(x):return hashlib.sha256(x).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());ker=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text());lfs=json.loads((ROOT/"third_party/littlefs/PROVENANCE.json").read_text());lc3=json.loads((ROOT/"third_party/liblc3/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or ker["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c" or lfs["upstream"]["selected_commit"]!="0494ce7169f06a734a7bd7585f49a9fa91fa7318" or lc3["upstream"]["selected_commit"]!="96a3af0beb5487aca3b98a4b992a539a1f6d80d1":raise c.AuditError("provider provenance changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=14 or sum(r['source_path_anchor']=='yes' for r in rows)!=7 or any(r['provenance']!='Ghidra-discovered' for r in rows):raise c.AuditError("inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];interval=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if (int(r['stock_start'],0),int(r['stock_end_exclusive'],0))!=(a,z) or len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256'] or c._uncovered((a,z),ii):raise c.AuditError("function closure changed")
  if set(ins)&set(ii):raise c.AuditError("overlapping functions")
  ins.update(ii);calls+=cc;ind+=dd;interval+=raw
 calls.sort();ind.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(interval)!=2676 or sh(interval)!="0db5547802646607e5e2bfba5dcd5527adf43fa7a5e23b3916c9d98e6db500f4" or code!=interval:raise c.AuditError("body closure changed")
 if len(ins)!=1073 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="55a017e9e0bead70f5f72cb8a8a53114c72eccb8c0ed4da23bcab5774f73eb34" or ind!=[0x57AE4A]:raise c.AuditError("instruction closure changed")
 non=b''.join(c._slice(b,*x) for x in NONCODE)
 if len(non)!=208 or sh(non)!="538de1e207f7719f8de43b064a2292e148b39292dd699a95692f06daa46de0db" or sh(c._slice(b,*PHYS))!="01864fb4fc778a70c3c50b7999c8a43b86d4f8763479e8cf5e47d7a529207193":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="22ccf8efd18ce76389cf4a458e5ea6c5595c14f850a43ac0ef2bf5b25dad9a85" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="228adbf7d252de6592988f87b5bfebde50f62cf4a046165238a8bcbf185f6522":raise c.AuditError("object boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,LC3,ALGO,FILE,LFS,FIRST)
 if len(calls)!=113 or sum(y in starts for x,y in calls)!=9 or c._pair_digest(calls)!="6f5cbdba36c0f50b3aa9b90769ba668bdaca93e7b0d2b1ef09f6e5f8044d61fe" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(76,8,3,5,2,7,2,1):raise c.AuditError("provider accounting changed")
 instruction_entries=set(ins)-starts;entries=[];strict=[];noncode=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in instruction_entries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=33 or c._pair_digest(entries)!="a20e35f1f49405b911cf91a0d24d978eda2602adbf20d51bc134d0e686b6c24d" or strict!=PSEUDO or noncode:raise c.AuditError("raw BL ingress changed")
 if any(c._slice(b,a,a+4)==b'\0'*4 for a,y in PSEUDO):raise c.AuditError("pseudo-BL evidence changed")
 words=[struct.unpack_from('<I',b,o)[0] for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};interior=set(ins)-starts
 if any(v in enc or ((v&1) and (v&~1) in interior) for v in words):raise c.AuditError("stored object pointer closure changed")
 if {a:int.from_bytes(c._slice(b,a,a+4),'little') for a in REG_LITERALS}!=REG_LITERALS or c._pair_digest(REG)!="3965eca7bc3af3b2f5101760556730ea1ae080b7a5ef0fdf877da3b6d518b834":raise c.AuditError("callback registration changed")
 if [(x,y) for x,y in entries if y==0x57AB78]!=[(x,0x57AB78) for x,y in REG]:raise c.AuditError("registration caller set changed")
 mic=load(ROOT/"tools/analyze_g2_production_mic.py","service_audio_registered_mic_callbacks").analyze()
 if mic['surface']['linked_functions']!=6 or mic['surface']['stored_entry_pointers']!=2:raise c.AuditError("registered callback provider changed")
 algo=load(ROOT/"tools/analyze_g2_service_algo.py","service_audio_closed_algo").analyze()
 if algo['surface']['linked_functions']!=10:raise c.AuditError("service_algo provider changed")
 lc3=load(ROOT/"tools/analyze_g2_liblc3.py","service_audio_liblc3").analyze()
 if lc3['stock']['direct_public_entry_calls']!=5:raise c.AuditError("liblc3 boundary changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_audio.c":raise c.AuditError("retained path changed")
 refs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(refs)!=15 or c._pair_digest(refs)!="98d44b9058379e4c447657538d5bcba69bb2217e9e49b349096c7dd96dd9ffbb":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("service_audio.c" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"platform\audio\service_audio.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":14,"ghidra_discovered_functions":14,"restored_functions":0,"path_anchored_functions":7,"body_bytes":2676,"physical_bytes":2884,"noncode_bytes":208,"reachable_instructions":1073,"direct_body_calls":113,"internal_direct_body_calls":9,"external_direct_body_calls":104,"indirect_body_calls":1,"resolved_indirect_body_calls":1,"direct_bl_entry_sites":33,"stored_function_entry_pointers":0,"registered_external_callback_entries":2,"registered_external_callback_sites":3,"raw_overlapping_pseudo_bl_sites":1,"strict_interior_ingress":0},"behavior":{"lc3_frame_encoding":True,"pcm_callback_registration":True,"fallback_ssr_tdoa_processing":True,"rotating_pcm_file_recording":True},"provider_boundary":{"easylogger_calls":76,"iar_dlib_calls":8,"cmsis_freertos_calls":3,"liblc3_calls":5,"closed_service_algo_calls":2,"source_owned_file_runtime_calls":7,"littlefs_backend_adapter_calls":2,"first_party_notification_calls":1,"registered_callback_entries":["0x0058f4e4","0x0058f5e0"],"liblc3_commit":"96a3af0beb5487aca3b98a4b992a539a1f6d80d1","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
