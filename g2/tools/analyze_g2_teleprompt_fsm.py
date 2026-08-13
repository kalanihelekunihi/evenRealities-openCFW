#!/usr/bin/env python3
"""Fail-closed object/provider audit for teleprompt_fsm.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-teleprompt-fsm-function-map.tsv";PM=ROOT/"tools/manifests/g2-teleprompt-fsm-provider-map.tsv";CL=ROOT/"tools/manifests/g2-teleprompt-fsm-closure.tsv"
PINS={FM:"b8caa1c494401cc3882ef047921801562c722886d0766c01293ceb9d4cc5b6e6",PM:"6b44618821ba50f94b3b5335132a0378d7908760971e211069bd94324554ecff",CL:"c1e0034b5302a789de5385080a3fa697692f166e4fcf9e876618c16f23614b2e"}
PHYS=(0x58C836,0x58D51C);PATH_CELLS=(0x58D2D8,0x58D500);HANDLER_TABLE=0x74EF50
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};LVGL={0x450500};NANOPB={0x48EB32}
FIRST={0x45A568,0x45A8EE,0x54F380,0x5540B2,0x5540BC,0x589B68,0x58B568,0x58BCE0,0x597EE0,0x597F52,0x597F82}
PSEUDO=(0x48BF90,0x58D144,0x48BF8E)
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
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
 if len(F)!=15 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2994 or sh(body)!="dd210db68f77f6a431561c3e1c32df1bae6d5b92ea9614b31a14bf089eec650f" or len(ins)!=1131 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="50e378c0f1afc230887b6d38b2e139b8f6b0c63a549e44efdfcf561eb807bfb7" or ind!=[0x58C9DA]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=308 or sh(non)!="628920a7de5c1e45cd3018118a39a920eaad0869844b2e049613ab8ff232322b" or sh(c._slice(b,*PHYS))!="585f9db01429cd44caafd3dba9edaf214f43dd83b3c58f1b1aa778772a6de88b":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="5df2c8965504ccb0a229de4e1c78bed33f51868b600d08d11e6c7de79eae8097" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="1b7c00d5e2be085d1c11a9a726f801b05a0c557390cbfefe668c19a9d46b86ab":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,NANOPB,FIRST)
 if len(calls)!=179 or sum(y in starts for x,y in calls)!=7 or c._pair_digest(calls)!="bcb9d05c13865c32d5b838761045b967ba32df3d6bdaaf36d462b6c9664899aa" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(140,3,1,2,26):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=29 or c._pair_digest(entries)!="1566a8c979babebb2b1a140b4f676db8d82515dac0bd2d5e2fb50979a1b92a34" or strict!=[(PSEUDO[0],PSEUDO[1])]:raise c.AuditError("raw ingress changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(decoder.disasm(c._slice(b,PSEUDO[2],PSEUDO[2]+4),PSEUDO[2]),None)
 if i is None or i.size!=4 or i.mnemonic!="mul" or PSEUDO[0]!=PSEUDO[2]+2:raise c.AuditError("pseudo-BL overlap proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=9 or c._pair_digest(stored)!="e045cf1756765951fca8c3ee0ffeca0e7a7ef4679d3521ab3b0d310bfb29fe04" or interior:raise c.AuditError("stored entry closure changed")
 table=struct.unpack_from('<9I',b,HANDLER_TABLE-c.BASE)
 if set(table)!={a|1 for a in starts if a in {0x58CA2A,0x58CEB4,0x58CEC2,0x58CF12,0x58CF50,0x58D000,0x58D0D0,0x58D228,0x58D2F4}}:raise c.AuditError("handler table changed")
 if cstring(b,0x6FD8EC)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_fsm.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=28 or c._pair_digest(pairs)!="642b9ab1867cc54b6296a98bf3249c8b0bcea2bda3dc45ac14fadaae92b1340c":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("teleprompt_fsm" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\teleprompt\teleprompt_fsm.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":15,"ghidra_discovered_functions":7,"restored_functions":8,"path_anchored_functions":3,"body_bytes":2994,"physical_bytes":3302,"noncode_bytes":308,"reachable_instructions":1131,"direct_body_calls":179,"internal_direct_body_calls":7,"external_direct_body_calls":172,"indirect_body_calls":1,"bounded_handler_table_entries":9,"direct_bl_entry_sites":29,"stored_function_entry_pointers":9,"raw_overlapping_pseudo_bl_sites":1,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":140,"iar_runtime_calls":3,"lvgl_calls":1,"nanopb_calls":2,"first_party_calls":26,"historical_fsm_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
