#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_ui_prep_note_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-conversate-ui-prep-note-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-conversate-ui-prep-note-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-conversate-ui-prep-note-page-closure.tsv'
PINS={FM:'e5b1a2a78754c15b5b5332b36288d6ca74f4cc18af7bfd7aee9fc9185efcbd16',PM:'f12f41770a58515ad69aa313ad9ce97bb22a4c2c3753dc1f031761cf93cd78be',CL:'b07f3954332d977bc0eb21ce4e263793f0849fc37200698a63561c05a3860130'}
PHYS=(0x5B69D4,0x5B7684);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43F09A,0x43F0E0,0x43F4C0,0x43F66C,0x43F6AC,0x43F6D6,0x43FCE0,0x43FD9E,0x43FDDA,0x43FE16,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x4413BE,0x4413CE,0x44140E,0x44143E,0x44144C,0x44145A,0x44146A,0x44D878,0x44D90E,0x44E368,0x44E3CA,0x44E498,0x44E75E,0x44EA04,0x450286,0x451740,0x498668,0x498680,0x499416,0x49942E,0x499678}
FIRST={0x45FFFE,0x460084,0x58C238,0x58C426,0x5B02E4,0x5B476A,0x5B4770,0x5B4776,0x5B7704}
COLLISION=(0x4D2301,0x5B6E43);DATA_WORD=(0x4D2300,0x5B6E4363)
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
 if len(F)!=16 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=3114 or sh(body)!='98688b1c373bb72979a7537b2c154b8b837e9d964bdf8181be08e1427633171e' or len(ins)!=1211 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='6ddecbb0095db7d493cd80138ecb5fda938bc81943fcfd366d935ff22b9d6d31' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=134 or sh(non)!='becee15e52de4c4ad524689342ac7f4495d870652bb4c63efe7b3d779f7de6a3' or sh(c._slice(b,*PHYS))!='50bdf1c1fd5db1b35751b1d8340e072dfa7b23172cefa33fd132f8a1bdfe5078':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='f9d024cf98c9f7db9d77fddd0e6c76537a8fc06cd7a7b2f61058e8eab8b3bcd5' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='23d2fc59d127ba92589bf786475a5fe018163455de3ebc99763ce3bdee7167cc':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,FIRST)
 if len(calls)!=211 or sum(y in starts for x,y in calls)!=23 or c._pair_digest(calls)!='073377d09b7001a15e93538d83e950845413a80f4eb0378b732f9a39ce6c6429' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(40,7,123,18):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=24 or c._pair_digest(entries)!='7093435ad7673b6c29662c2380cc575d8617555c0ce87db1eb9f43ee9cccfed9' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=9 or c._pair_digest(stored)!='9fb8eb00732fd55e732eeba3104cf97bce582d0e1c6b8352124d040e49cfb60d' or interior!=[COLLISION]:raise c.AuditError('stored ingress changed')
 if COLLISION[0]&1!=1 or struct.unpack_from('<I',b,DATA_WORD[0]-c.BASE)[0]!=DATA_WORD[1] or sh(c._slice(b,0x4D22FC,0x4D230C))!='dc3000288e7962a60d1af4d9ceb72a1c4842c2ce91ab35e2fd91278eb2a494ef':raise c.AuditError('interior collision proof changed')
 if cstring(b,0x6E2C78)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_prep_note_page.c':raise c.AuditError('path changed')
 pairs=[(0x5B7610,x) for x in t.literal_references(b,0x5B7610)]
 if len(pairs)!=8 or c._pair_digest(pairs)!='3e2885b75dd2dd31de101305068d3c840256b3af0210f5d88e742c3e76658b65':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('conversate_ui_prep_note_page' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\conversate\conversate_ui_prep_note_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':16,'ghidra_discovered_functions':9,'restored_functions':7,'path_anchored_functions':2,'body_bytes':3114,'physical_bytes':3248,'noncode_bytes':134,'reachable_instructions':1211,'direct_body_calls':211,'internal_direct_body_calls':23,'external_direct_body_calls':188,'indirect_body_calls':0,'direct_bl_entry_sites':24,'stored_function_entry_pointers':9,'unaligned_interior_pointer_shaped_byte_windows':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':40,'iar_dlib_calls':7,'lvgl_calls':123,'first_party_calls':18,'historical_prep_note_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
