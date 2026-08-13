#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-conversate-ui-function-map.tsv';PM=ROOT/'tools/manifests/g2-conversate-ui-provider-map.tsv';CL=ROOT/'tools/manifests/g2-conversate-ui-closure.tsv'
PINS={FM:'a4d639d355b959a4d3bc6738a0c36433230e8ccb8ed37efed76765e00cc30438',PM:'4d8f922cfa3f6f670abf8c7f4e96ce2d8d653b558dd3fd509217b2ef7801364b',CL:'5aa345a720dcdd3f468da9ecae60b1b62e886d193da6f9abb6f218c2c7ea7a9a'}
PHYS=(0x5B0B58,0x5B1B4C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F4C0,0x43F6D6,0x44104C,0x441180,0x4411AA,0x44122A,0x441238,0x441246,0x441254,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x44132A,0x441386,0x4413CE,0x44140E,0x44143E,0x44145A,0x44146A,0x441488,0x44D7B8,0x44DCE2,0x44DDEA,0x44E368,0x44E498,0x4503D6,0x450408,0x450500,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
FIRST={0x45A568,0x45FFFE,0x460084,0x464C36,0x48BA78,0x48BA92,0x58966C,0x5896B4,0x5897EE,0x589892,0x58BFB2,0x5B0AC4,0x5B2642,0x5B2652,0x5B3CBA,0x5B3D04,0x5B3D86,0x5B5886,0x5B5DE4,0x5B7060}
TABLE=0x686920;TABLE_WORDS=294;TABLE_POOL=0x5B1B20;RAW_WORD=(0x5D041E,0x5B0C01)
CLOSED_HANDLERS={0x5B2642,0x5B2652,0x5B29BC,0x5B2A64,0x5B2B74,0x5B2C68,0x5B2D64,0x5B30C8,0x5B32B4,0x5B3398,0x5B34A0,0x5B34B4,0x5B5886,0x5B58E8,0x5B59FA,0x5B5B96,0x5B5BF0,0x5B5DE4,0x5B5ED2,0x5B5EF6,0x5B5F44,0x5B6426,0x5B6688,0x5B68D6,0x5B6F8E,0x5B7138,0x5B74BA,0x5B7556}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=23 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=3774 or sh(body)!='925b9294cd57e596046d56df1bd6e6518d64384915acaa976b0a9b02b2c83bc1' or len(ins)!=1452 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='03b47bebc5aa357d7ad2574139e0eb7a9a7d931bad740925f19ea752e364fd17' or ind!=[0x5B18C0]:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=310 or sh(non)!='29c589af17f8396b95da57932c4f1ac73d15574784ec3d5be2b39769b7996cd9' or sh(c._slice(b,*PHYS))!='e5f73d182e296f7c72a6c0550a0f94f3bdc011c8193c161fe03cb0cfef47ef60':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='af8bb002cf279c9bb53e4d3fa5240cc01a6dbab5414bf7ca2a54d1bdf893360c' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='b59c07d5f3db89e27a88d7193073f647d9e9333d156b833381fc1e83374b1523':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,FIRST)
 if len(calls)!=240 or sum(y in starts for x,y in calls)!=19 or c._pair_digest(calls)!='63ff5c5a74ff62d7ff3803be6a53d6ad7508ec555f6f72ae77c24443d47dc245' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(100,2,84,35):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=74 or c._pair_digest(entries)!='67e31bc0577bd825d8187f1de01ba924c8e778c87ff25518cbc2bd36637f090f' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=11 or c._pair_digest(stored)!='e1e6fec2a6bbbfe0501348a23687af65ec73010d81894fed7fd14d5f62ed2d88' or interior!=[RAW_WORD]:raise c.AuditError('stored ingress changed')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);ii=list(D.disasm(c._slice(b,RAW_WORD[0],RAW_WORD[0]+4),RAW_WORD[0]))
 if len(ii)!=2 or any(i.size!=2 for i in ii):raise c.AuditError('instruction-word collision proof changed')
 if struct.unpack_from('<I',b,TABLE_POOL-c.BASE)[0]!=TABLE:raise c.AuditError('handler table base changed')
 table=struct.unpack_from(f'<{TABLE_WORDS}I',b,TABLE-c.BASE)
 if sh(c._slice(b,TABLE,TABLE+TABLE_WORDS*4))!='9c5500318d2374dc1aa3d71c8857165ce65529dec6b1270aa9489878eb06cd7f':raise c.AuditError('handler table changed')
 callbacks={table[2*k+1] for k in range(147)}
 if sum(table[2*k+1]!=0 for k in range(147))!=50 or {v&~1 for v in callbacks if v}-(starts|CLOSED_HANDLERS):raise c.AuditError('handler table targets changed')
 chk=list(D.disasm(c._slice(b,0x5B1732,0x5B1736),0x5B1732))+list(D.disasm(c._slice(b,0x5B17E6,0x5B17EA),0x5B17E6))
 if [i.mnemonic for i in chk]!=['cmp','blt','cmp','blt'] or chk[0].op_str!='r0, #0x15' or chk[2].op_str!='r0, #7':raise c.AuditError('dispatch range checks changed')
 if cstring(b,0x6F956C)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui.c':raise c.AuditError('path changed')
 pairs=[(cell,x) for cell in (0x5B15CC,0x5B1ADC) for x in t.literal_references(b,cell)]
 if len(pairs)!=21 or c._pair_digest(pairs)!='14bada2e5b15593eb94c95f9722dd2a49063a72a8d2ac4f2e12aa0714b667152':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('conversate_ui' in x.get('path','').lower() and 'conversate_ui_' not in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\conversate\conversate_ui.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':23,'ghidra_discovered_functions':8,'restored_functions':15,'path_anchored_functions':4,'body_bytes':3774,'physical_bytes':4084,'noncode_bytes':310,'reachable_instructions':1452,'direct_body_calls':240,'internal_direct_body_calls':19,'external_direct_body_calls':221,'indirect_body_calls':1,'bounded_event_handler_table_entries':147,'direct_bl_entry_sites':74,'stored_function_entry_pointers':11,'raw_instruction_word_interior_collisions':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':100,'iar_dlib_calls':2,'lvgl_calls':84,'first_party_calls':35,'historical_conversate_ui_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
