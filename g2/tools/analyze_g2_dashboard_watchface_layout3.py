#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_watchface_layout3.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-dashboard-watchface-layout3-function-map.tsv';PM=ROOT/'tools/manifests/g2-dashboard-watchface-layout3-provider-map.tsv';CL=ROOT/'tools/manifests/g2-dashboard-watchface-layout3-closure.tsv'
PINS={FM:'02840b3decb0f14700863c934d5d02f0146f7181011054641e7280df80310003',PM:'e858dfb81ac0dab1957febe87a7fa9b99b10ebb3cdfc35128b9d71bce688618f',CL:'3d139952a26e88bb9e44747cc4115e96ece4a2886fc220a13b50de343c76b795'}
PHYS=(0x5B9CEC,0x5BAB2C);PSEUDO=[(0x4CA3A4,0x5BA55C,0x4CA3A2),(0x4CA44E,0x5BA606,0x4CA44C),(0x4CA46A,0x5BA622,0x4CA468),(0x4CA4C8,0x5BA680,0x4CA4C6),(0x4CA4E4,0x5BA69C,0x4CA4E2)]
EASY={0x43CE9E,0x43D0CE,0x43D574};LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6AC,0x43FDDA,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x441254,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x44140E,0x44142E,0x44143E,0x44146A,0x44D7B8,0x498668,0x498680,0x499416,0x49942E};IAR={0x43C0E4,0x44B728};PRINTF={0x4B4728};FIRST={0x44A19A,0x45FFFE,0x460084,0x46650C,0x466512,0x47D8CE,0x47D9C4,0x47D9CC,0x48BA78,0x48BA92,0x49C5BC,0x509F8E}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 if 'd3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e' not in (ROOT/'components/apollo_main/core_overlay/EVIDENCE.md').read_text():raise c.AuditError('printf changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=19 or sum(r['source_path_anchor']=='yes' for r in rows)!=1:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=3254 or sh(body)!='0f455cc5915bb902d5a1864b107901a615ded49e883caf2b20d0c902e52923cc' or len(ins)!=1201 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='b425e8793cf33cdc625ce770da660dea930aa5b65ac504179f24b74d35679930' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=394 or sh(non)!='44031ec263aae1e5059066d3e0fe82f4d981184fe4353344d406bfbbb6f67b48' or sh(c._slice(b,*PHYS))!='0a2b91f3b73f6471416ba057802b028a7dff2a09e46ff66e9b12c820ba31ea43':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='2f0d8191203ebed03f61e51ea7f8dfb5549310b538c01f3d6008706d61b43cdb' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='d29cf653e182d075e9082dd22a8c4649cd3a3ce24ddcf6862ea56564689d6d7a':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,PRINTF,FIRST)
 if len(calls)!=199 or sum(y in starts for x,y in calls)!=26 or c._pair_digest(calls)!='d890ebc7170f9500b91147c7b55d2045a00c67cbbc45b291df5b82e28161bdbb' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(20,125,10,2,16):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=28 or c._pair_digest(entries)!='a7666db6c949a9711b13faaee86470f7be9f6c03c797273bceb3d7f8929bbeeb' or strict!=[(a,y) for a,y,s in PSEUDO]:raise c.AuditError('BL ingress changed')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 for a,y,s in PSEUDO:
  i=next(D.disasm(c._slice(b,s,s+4),s),None)
  if i is None or i.size!=4 or i.mnemonic!='sdiv' or a!=s+2:raise c.AuditError('pseudo BL changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=9 or c._pair_digest(stored)!='75a14fcc7741463ffc7bb8c03363fcd4ce4f72c034eb414396f96ea0bfedbe26' or interior:raise c.AuditError('stored ingress changed')
 pairs=[(0x5BAAB0,x) for x in t.literal_references(b,0x5BAAB0)]
 if len(pairs)!=4 or c._pair_digest(pairs)!='5a845a54281a2ce5bf9ecdff77ba00b124d3ea04a091a5f90e404f29d9dd3014':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('dashboard_watchface_layout3' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\dashboard_watchface_layout3.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':19,'ghidra_discovered_functions':12,'restored_functions':7,'path_anchored_functions':1,'body_bytes':3254,'physical_bytes':3648,'noncode_bytes':394,'reachable_instructions':1201,'direct_body_calls':199,'internal_direct_body_calls':26,'external_direct_body_calls':173,'indirect_body_calls':0,'direct_bl_entry_sites':28,'stored_function_entry_pointers':9,'raw_overlapping_pseudo_bl_sites':5,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':20,'lvgl_calls':125,'iar_dlib_calls':10,'mpaland_printf_calls':2,'first_party_calls':16,'historical_layout3_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
