#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/translate/translate_fsm.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-translate-fsm-function-map.tsv';PM=ROOT/'tools/manifests/g2-translate-fsm-provider-map.tsv';CL=ROOT/'tools/manifests/g2-translate-fsm-closure.tsv'
PINS={FM:'8909d5eb11aabc1768634d4418d663fd038db6c7a03ddac67b432e9738fb7bf7',PM:'d8cf14f699c152a204e48cacfe9853dfaf2ade35615673c7a9f7dc924219932c',CL:'271237c2b5a4b3eaab1a7840783d80b480321569718134c260381dfed0f91fda'}
PHYS=(0x596B00,0x5970A8);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};NANOPB={0x48EB32};FIRST={0x443504,0x45A568,0x45A8EE,0x54F380,0x54F50E,0x59D9D4,0x59DB5C,0x59DB66,0x59E6D0,0x59E9E2,0x59EC28}
STORED=[(0x773B8C,0x596C99),(0x773B90,0x596EF5),(0x773B94,0x596F03),(0x773B98,0x596F11),(0x773B9C,0x596F49),(0x773BA0,0x596F9F)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=8 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1304 or sh(body)!='4f23df354f78ed688239a370dc3649d06aadefa191ec75f0e02c8d13f34e01aa' or len(ins)!=506 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='c97f6d8288a2dcb5e053ed1ff45e88f3c0b52711cb1470169f499fdcecd55445':raise c.AuditError('instruction closure changed')
 if ind!=[0x596C48]:raise c.AuditError('indirect dispatch changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=144 or sh(non)!='694b8de7b370734b736ae4fe3a8e3a2e0e6e764ad993e9bcf1eafcdd40e7bfdc' or sh(c._slice(b,*PHYS))!='58a900867e063e34a3b943e878a12f13cf16b2e036c4b32620623b0aca166fa2':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='adb1d8488654f6354d89bcd66635e6a27a0cc06dd2ea61a8dadd1e1c0067d165' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='d3d7c608109a0a0409d82ad9da68ff979af8a7d630764c33db30979086c3b4e4':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,NANOPB,FIRST)
 if len(calls)!=90 or sum(y in starts for x,y in calls)!=4 or c._pair_digest(calls)!='b6d66b95c1f2eea10aaf2a8b43e9493d1fc9ac1ed96dfffcc5e7b25089204348' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(55,4,3,24):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=11 or c._pair_digest(entries)!='908c15e3e223b68db8dab4b568ab7aaf7a1b4f05041e0f97e8cabe83e3cc6d9d' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or c._pair_digest(stored)!='3fee330a51363752e71e181f14a223a341c292ebd5d0f1afcfb857bf9e0f2b78' or interior:raise c.AuditError('stored ingress changed')
 if {v&~1 for a,v in STORED}-starts:raise c.AuditError('state table escapes object')
 pairs=[(0x597024,x) for x in t.literal_references(b,0x597024)]
 if len(pairs)!=11 or c._pair_digest(pairs)!='0682e931ff4f27f3fcd3c7e05660d98373ccff43287a6f638f1faa55fca478f0':raise c.AuditError('path refs changed')
 off=0x6FE5DC-c.BASE
 if b[off:b.find(b'\0',off)].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_fsm.c':raise c.AuditError('retained path changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('translate_fsm' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\translate\translate_fsm.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':8,'ghidra_discovered_functions':2,'restored_functions':6,'path_anchored_functions':4,'body_bytes':1304,'physical_bytes':1448,'noncode_bytes':144,'reachable_instructions':506,'direct_body_calls':90,'internal_direct_body_calls':4,'external_direct_body_calls':86,'indirect_body_calls':1,'indirect_dispatch_bounded_by_stored_state_table':6,'direct_bl_entry_sites':11,'stored_function_entry_pointers':6,'raw_instruction_word_interior_collisions':0,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':55,'iar_dlib_calls':4,'nanopb_calls':3,'first_party_calls':24,'historical_translate_fsm_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
