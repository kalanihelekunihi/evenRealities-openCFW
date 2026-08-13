#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_ui_main_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-conversate-ui-main-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-conversate-ui-main-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-conversate-ui-main-page-closure.tsv'
PINS={FM:'5ef28b6476b5eaef5efcee133c9d28de4cbc8ecc516ef3346a7673516f201697',PM:'57c51b046f92c476bb96e3f1b5280da38444fb84d3578e8a049b9efb0d48566b',CL:'e676740c1b5d7611f43e34aaf792b4c35868f43663736047d108a4ac316c6d1e'}
PHYS=(0x5B23E4,0x5B3570);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x44B728}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F4C0,0x43F6AC,0x43F6B8,0x43F6D6,0x43FDDA,0x44104C,0x4411AA,0x44129E,0x44131C,0x441386,0x44140E,0x44143E,0x44144C,0x44145A,0x44146A,0x441488,0x44D7B8,0x44DCE2,0x44DDEA,0x44E368,0x44EA04,0x44EA2E,0x450500,0x499416,0x49942E,0x499678}
FIRST={0x45FFFE,0x460084,0x46AE9C,0x5896FC,0x5897E0,0x58A680,0x58C238,0x58C622,0x58C6C4,0x58C7A0,0x58C84E,0x5969A4,0x5B02E4,0x5B0C18,0x5B0D86,0x5B0EDC,0x5B1072,0x5B1150,0x5B12BA,0x5B13FE,0x5B22BC,0x5B22FA,0x5B3C70,0x5B4364,0x5B43E8,0x5B4766}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=15 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=4132 or sh(body)!='8c6c2637bae404a7e96b50f32c6aa37f4e66d4d4b815b19c514f8bc30ef4d2c6' or len(ins)!=1531 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='c47af8e04636a77d61edfd09e0664471167311e8a345f78adefba1f6a2cac780' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=360 or sh(non)!='d0bd00a5e9b89f40fcb563f400a15fc646a604ce4dab90d64d305ff2781bfcbf' or sh(c._slice(b,*PHYS))!='d8039e4c2b938b16651d17d57ca86ab03856b88cba201ab8fec72ce47a53c4d0':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='93ed5c6d2973ebfadd1875f7936142d94b778f89a424dbb8e82f3e0975de15f4' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='844296d6109d08e91c0d3289a896b782db0512ae791e20e6e62f9872addd6ae4':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,FIRST)
 if len(calls)!=287 or sum(y in starts for x,y in calls)!=4 or c._pair_digest(calls)!='e50fd92f71151c8fa3f1f0ca0cf871c527ab8d045a51aac48054fc7888548d08' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(130,98,2,53):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=6 or c._pair_digest(entries)!='fa574cf446d8529ff5612286614c2c911d76f35da28e8cc9d4379b86037407db' or len(strict)!=2 or c._pair_digest(strict)!='798b740064b72e91d0f376e948c6430b7adddfde9a36effbb247c99bd8041fd5':raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if len(stored)!=21 or c._pair_digest(stored)!='6e84c214a69d7e536bd35a80fc9e3c10e67432c374f2cf5473c6c7fed71843ab' or len(interior)!=1 or c._pair_digest(interior)!='cce86ea9aaa5ebd01279a28459cceb5eb205c0a4bd543b2eb4fd36ca643e279f':raise c.AuditError('stored ingress changed')
 pairs=[]
 for cell in (0x5B2D2C,0x5B3524):pairs += [(cell,x) for x in t.literal_references(b,cell)]
 if len(pairs)!=27 or c._pair_digest(pairs)!='c2398c5e05a2ce69a15a73b35c4fa2f82c0f5d37730a726aed39d5985fd91769':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('conversate_ui_main_page' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\conversate\conversate_ui_main_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':15,'ghidra_discovered_functions':4,'restored_functions':11,'path_anchored_functions':3,'body_bytes':4132,'physical_bytes':4492,'noncode_bytes':360,'reachable_instructions':1531,'direct_body_calls':287,'internal_direct_body_calls':4,'external_direct_body_calls':283,'indirect_body_calls':0,'direct_bl_entry_sites':6,'stored_function_entry_pointers':21,'strict_interior_ingress':2,'stored_strict_interior_entries':1},'provider_boundary':{'easylogger_calls':130,'lvgl_calls':98,'iar_dlib_calls':2,'first_party_calls':53,'historical_main_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
