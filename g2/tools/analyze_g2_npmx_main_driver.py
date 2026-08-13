#!/usr/bin/env python3
"""Fail-closed object, provider, and nPMX provenance audit for npmx_main_driver.c."""
import csv,hashlib,importlib.util,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-npmx-main-driver-function-map.tsv";CL=ROOT/"tools/manifests/g2-npmx-main-driver-closure.tsv";PM=ROOT/"tools/manifests/g2-npmx-main-driver-provider-map.tsv"
PINS={FM:"5787bf60d322f1356f4a69a4c4f5ad167679d559a8cc71d76a8b768cb3edd441",CL:"ef868a03f667ed263e99ceac7dea5184ebce687dd1f933f05cd8a9bf5ae904a1",PM:"a0874b41f52caa1b48854068cf47cd82b2665af05d03245ad248edb2c154cb44",ROOT/"third_party/npmx/PROVENANCE.json":"95f857ee3280320f879ad0d01bcf2cf95fbca4e9d76833d7edaa435af88ebeb3"}
PHYS=(0x511002,0x512BC0);PATH_CELLS=(0x511954,0x512404,0x512BC0);PATH_ADDR=0x6E103C
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC};IAR={0x439C04,0x43C150};FIRST={0x4910F4,0x4AC130,0x4AC154,0x50436E,0x5044B4,0x50938E};SENSOR={0x55F74C,0x55F848,0x55F994,0x55F9A0}
NPMX={0x55EB3E,0x55ED9A,0x55EDCA,0x55EE04,0x55EE74,0x55EE7E,0x55EE8C,0x55EE96,0x55EF02,0x55EF1E,0x55EF3C,0x55EF6C,0x55EF76,0x55EF80,0x55EFF0,0x55EFFA,0x55F07A,0x55F0D8,0x55F134,0x55F1B8,0x55F25C,0x55F278,0x55F294,0x55F4F2,0x55F4FE,0x55F544,0x55F58A,0x55F654,0x55F6F0,0x55FA0E,0x55FA18,0x55FA22,0x55FA40,0x55FACE,0x55FAD8,0x55FAE2,0x55FB7C,0x55FBE4,0x55FC2C,0x55FC38,0x55FC60,0x55FC6A}
STORED=[(0x511978,0x511003),(0x51197C,0x511085),(0x511BF4,0x51124D),(0x511C10,0x511295)]
ADC=(0x55F654,0x55F6F0,"8848f2f4cd360a170d7b13ca9443ff0ec66f02050086a6b8251f0ea59be90cc2");LN=(0x58E984,0x58E9DE,"94b6d6ef12b40e552c4b7566694d6f7498684f0ae4d0ebc07ab4f452111b2897");DOUBLES=(0x58E9E0,0x58EA08,"11a46f6a70910734dae7d952d252f73ad20e45f7ddc57286677585b65ebb6d0b")
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def npmx_snapshot():
 p=ROOT/"third_party/npmx/verify_snapshot.py";s=importlib.util.spec_from_file_location("verify_npmx_snapshot",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.verify()
 if r["selected_commit"]!="e1aaec53f456887a7d7b80d82f684d1ac3cb08c8" or r["files"]!=38:return False
 return True
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 if not npmx_snapshot():raise c.AuditError("nPMX snapshot changed")
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=30 or sum(r['source_path_anchor']=='yes' for r in rows)!=11:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=6560 or sh(body)!="3d0d625389b666d0678a9647142cc51f73b6f26c399cc1fbc4e1b1aeaad3c0ff" or len(ins)!=2281 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="81fcc262dfa069906928f1f3f4ef707efc68321f2c28ac3a34942237d2d4d009" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=542 or sh(non)!="3325b2eb4885a20a237f59bd0576e7fec09f83f93db2a397fb380672ebd7091a" or sh(c._slice(b,*PHYS))!="a6e4c6d368d0ebd48f6821294b2f9d78462eb3b90748208ea2462c8623145895":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="234ebac71181a78920373be1dc04691955b8e26c96f70a4df147e9389e25a4e8" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="b78ce208235c952359c38c649b0d3fda5eea0131be23e5cf0c97965f97359b31":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(NPMX,EASY,CMSIS,IAR,FIRST,SENSOR)
 if len(calls)!=420 or sum(y in starts for x,y in calls)!=17 or c._pair_digest(calls)!="0dc9f28689a382fac9d1031aafa4e0b2f31b3c2c58d59f226d31a768b2780783" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(72,310,2,2,9,8):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];noncode=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=35 or c._pair_digest(entries)!="a5efc970e0e2997689a519b20efdde5cd387fa2d2325e7c55cf0ee59cf82991b" or strict or noncode:raise c.AuditError("BL ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 if [(a,v) for a,v in words if v in enc]!=STORED or any((v&1) and (v&~1) in inter for a,v in words):raise c.AuditError("stored entry closure changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\driver\npmx_driver_transplant\src\npmx_main_driver.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=62 or c._pair_digest(pairs)!="73b32a95bf79d4ab8e43c9ec5b6666f4d46bf41776fa38f45905966c5e1ad6bf":raise c.AuditError("path references changed")
 for a,z,h in (ADC,LN,DOUBLES):
  if sh(c._slice(b,a,z))!=h:raise c.AuditError("nPMX version discriminator changed")
 expected=struct.pack('<ddddd',0.10969,-0.729104,2.11263,-1.49278,0.6931471806)
 if c._slice(b,DOUBLES[0],DOUBLES[1])!=expected:raise c.AuditError("nPMX double constants changed")
 dec=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);ln=list(dec.disasm(c._slice(b,LN[0],LN[1]),LN[0]));mn=[(i.mnemonic,i.op_str) for i in ln]
 if sum(m=='vcvt.f64.f32' for m,o in mn)!=3 or sum(m=='vmla.f64' for m,o in mn)!=4 or sum(m=='vcvt.f32.f64' for m,o in mn)!=1:raise c.AuditError("pre-53de float promotion proof changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("npmx_main_driver" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"driver\npmx_driver_transplant\src\npmx_main_driver.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":30,"ghidra_discovered_functions":11,"restored_functions":19,"path_anchored_functions":11,"body_bytes":6560,"physical_bytes":7102,"noncode_bytes":542,"reachable_instructions":2281,"direct_body_calls":420,"internal_direct_body_calls":17,"external_direct_body_calls":403,"indirect_body_calls":0,"direct_bl_entry_sites":35,"stored_function_entry_pointers":4,"strict_interior_ingress":0},"behavior":{"npmx_core_lifecycle":True,"adc_measurement_and_calibration":True,"charger_and_vbus_policy":True,"watchdog_timer_control":True,"buck_and_ldsw_rail_control":True,"raw_backend_register_access":True},"provider_boundary":{"npmx_calls":72,"npmx_entry_targets":42,"easylogger_calls":310,"cmsis_freertos_calls":2,"iar_dlib_calls":2,"first_party_transport_delay_calls":9,"first_party_orientation_calls":8,"npmx_selected_commit":"e1aaec53f456887a7d7b80d82f684d1ac3cb08c8","npmx_describe":"v1.0.1-1-ge1aaec5","npmx_adjacent_excluded_commit":"53de7af4394382e1a21008eaa18ed9e5e1809504","exact_public_candidate":True,"exact_private_checkout_proven":False,"new_version_discriminator":True},"production":{"production_routed":False,"remaining_integration":["generated nPM1300 ADK","Apollo510 I2C backend","G2 nPM1300 configuration","interrupt wiring","rail and charger policy"]}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
