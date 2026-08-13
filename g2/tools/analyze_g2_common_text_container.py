#!/usr/bin/env python3
"""Fail-closed object/provider audit for EvenHub common_text_container.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-common-text-container-function-map.tsv";CL=ROOT/"tools/manifests/g2-common-text-container-closure.tsv";PM=ROOT/"tools/manifests/g2-common-text-container-provider-map.tsv"
PINS={FM:"b91c7c6c5c599e98e15ce19c201d3a488acd7207eb17c99561f15abb79bc7a20",CL:"a19e8189c979af9588411effd5e9373529b44b04fedc1b782349317a27d11ce8",PM:"15e050212d6df72baeef80c9435dff7f339d3f127ec95f9eaade2bc321f9dc3a"}
PHYS=(0x4DEE64,0x4E0CA0);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4,0x44A43C,0x44B5A0};HEAP={0x474CD2,0x474D16};FIRST={0x509C1C,0x509C96,0x509CA2,0x509DFA,0x509E14,0x509F52}
LVGL={0x43DE82,0x43DFA4,0x43E2EA,0x43F0E0,0x43F142,0x43F506,0x43F568,0x43F66C,0x43FCE0,0x43FDDA,0x44104C,0x441164,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44140E,0x44143E,0x44145A,0x44146A,0x44D7B8,0x44E368,0x44E3CA,0x44E498,0x44E4AA,0x44E4BC,0x44EA04,0x4503D6,0x450408,0x450500,0x450566,0x4506CE,0x499416,0x49942E,0x499678}
PATH_CELLS={
 0x4DFA08:[0x4DEECA,0x4DEF32,0x4DEF92,0x4DEFEE,0x4DF04A,0x4DF0A6,0x4DF100,0x4DF15A,0x4DF1B4,0x4DF218,0x4DF282,0x4DF2FC,0x4DF348,0x4DF398,0x4DF464,0x4DF518,0x4DF5D0,0x4DF6AC,0x4DF70E,0x4DF754,0x4DF7C4,0x4DF81E,0x4DF88C,0x4DF92C],
 0x4DFFF0:[0x4DF9DA,0x4DFA4A,0x4DFAA6,0x4DFB18,0x4DFBB0,0x4DFC5C,0x4DFCDE,0x4DFD32,0x4DFD8E,0x4DFDFC,0x4DFE90,0x4DFEE8,0x4DFF36],
 0x4E0B2C:[0x4E002E,0x4E0086,0x4E0100,0x4E016E,0x4E01C0,0x4E0236,0x4E0364,0x4E03BA,0x4E0422,0x4E0476,0x4E04DE,0x4E0526,0x4E058A,0x4E05D8,0x4E063C,0x4E06A2,0x4E0710,0x4E077C,0x4E07FC,0x4E0856,0x4E08B6,0x4E092E,0x4E0978,0x4E09B8,0x4E0A00,0x4E0A54,0x4E0AAE,0x4E0AF0],
}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
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
 if len(F)!=13 or sum(r['source_path_anchor']=='yes' for r in rows)!=11:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(z-a) or sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=6966 or sh(body)!="bc00496fb30d1269f56f8768d1469b8faf8d50bfc4700a4d1a951a3588421139" or len(ins)!=2509 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="9f8743232b1ed12cbfc63aa9973076e5c89150f371e6d8a550a48480fca5ee55" or ind!=[0x4E074E,0x4E07BA,0x4E0890,0x4E08EE]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=774 or sh(non)!="15ae7cae877dec8a1feec453b4a30f1e6379eabb1bba1aacee349bd4f3609cd9" or sh(c._slice(b,*PHYS))!="4dc0f08df67d24201fb4788966ec9a9ddce6d1e5ed953db146a89b20dbb915d2":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x4DEE54,PHYS[0]))!="8f9545779b9393ef844584effb84e2862ba0aa8fb364ab530b363d79464f2c08" or sh(c._slice(b,PHYS[1],0x4E0CB0))!="a953d8ea264e4315d4d55d62aec920f6eacb7633eb391980af2125f219370cea":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,HEAP,FIRST)
 if len(calls)!=445 or sum(y in starts for x,y in calls)!=19 or c._pair_digest(calls)!="ba03b8bcb35dac805ce68e4aeea98ef7c617802e5a3c1bbe092b1a0c1eaa22de" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(325,78,5,6,12):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=24 or c._pair_digest(entries)!="1c415b8893c46ac72c4c90b9e157499cdeb606f24e42de3381781ade5ddcb313" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x4E02E4,0x4DF9A3),(0x4E02EC,0x4DFA2D),(0x4E0B20,0x4DFCC1)]:raise c.AuditError("stored entries changed")
 constructors=[x for x in entries if x[1]==0x4DEE96]
 if constructors!=[(0x495252,0x4DEE96),(0x495BBE,0x4DEE96)] or struct.unpack_from('<I',b,0x49559C-c.BASE)[0]!=0x494A79 or struct.unpack_from('<I',b,0x49642C-c.BASE)[0]!=0x494A79:raise c.AuditError("callback constructor closure changed")
 cb,cc,ci=q._recover_function(b,0x494A78,0x494B38)
 if len(cb)!=73 or ci or c._uncovered((0x494A78,0x494B38),cb) or sh(c._slice(b,0x494A78,0x494B38))!="946b25b25e16a7da7c9009dd8b91da3c99b84ac247898d4fff3884e83aae6549" or c._instruction_digest(sorted((a,i.size) for a,i in cb.items()))!="6c774f5f25c979a2cc8600db7b70d465e7789824a1ed8ba4cdd319317cdb36c1" or c._pair_digest(sorted(cc))!="b6d3571ae95780485f31b79f9e6c16343322fd54833786f79507ff6400b88110":raise c.AuditError("callback body changed")
 if cstring(b,0x6F22FC)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_text_container.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("common_text_container" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenHub\common_text_container.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":13,"ghidra_discovered_functions":10,"restored_functions":3,"path_anchored_functions":11,"body_bytes":6966,"physical_bytes":7740,"noncode_bytes":774,"reachable_instructions":2509,"direct_body_calls":445,"internal_direct_body_calls":19,"external_direct_body_calls":426,"indirect_body_calls":4,"bounded_indirect_targets":1,"direct_bl_entry_sites":24,"stored_entry_pointers":3,"strict_interior_ingress":0},"behavior":{"text_object_construction":True,"style_and_layout_configuration":True,"scroll_animation":True,"queue_driven_navigation":True,"bounded_navigation_callback":True},"provider_boundary":{"easylogger_calls":325,"lvgl_calls":78,"iar_dlib_calls":5,"source_owned_heap_wrapper_calls":6,"first_party_calls":12,"navigation_callback_calls":4,"navigation_callback_target":"0x00494A78","lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
