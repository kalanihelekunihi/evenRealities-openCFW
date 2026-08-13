#!/usr/bin/env python3
"""Fail-closed object/provider audit for ui_common_api.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ui-common-api-function-map.tsv';PM=ROOT/'tools/manifests/g2-ui-common-api-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ui-common-api-closure.tsv'
PINS={FM:'f0f91162d605d3e23e54dcf1df0e04df0c6a640aa7520a5927e90403e62d4900',PM:'f096f35ecdc14efaa961392319dff50c4536b6203dee96f0cf158ff2b88dd5c7',CL:'451ad526d12148d1619be582af28a75291fd12d6a5a74047f5de75eee2fed57d'}
F=((0x509C1C,0x509C96),(0x509C96,0x509CA2),(0x509CA2,0x509DFA),(0x509DFA,0x509E14),(0x509E14,0x509F52),(0x509F52,0x509F7A),(0x509F7A,0x509F86),(0x509F86,0x509F8E),(0x509F8E,0x509F98))
PHYS=(0x509C1C,0x509FDC);POOL=(0x509F98,0x509FDC);PATH=0x70797C;CELL=0x509FA0
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};CLOSED={0x474CD2,0x474D16,0x4974D4,0x4AD8FA}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=9 or sum(r['source_path_anchor']=='yes' for r in rows)!=3 or sum(r['ghidra_discovered']=='yes' for r in rows)!=9:raise c.AuditError('function inventory changed')
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  if set(ins)&set(ii):raise c.AuditError('overlap')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=892 or sh(body)!='d24e48c13551db17a7bd06107dfed7a26010cd1acda1bd1428d54dafbc040959' or code!=body or len(ins)!=330 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='7b1fa2d3b06cf235bf13983495a158f9c39b31d96616fbf92156218001996b04' or ind:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=68 or sh(non)!='b7e3f965b33f53cc9eec7bac60073703dfa9f2bdba373b9dac39afb8f5d877fb' or non!=c._slice(b,*POOL) or sh(c._slice(b,*PHYS))!='64a2decedde57391ba1a556c5ae30b61a00555297d211ff35061bad91d17c0a4':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='b60c5e233e4598d4655de540fe52cc6e650ddbb2483e663d0801b353670c5a2d' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='cc545be561bf09b31370a91ec08393d915e0de844268ea43e90aacfa5a31bc71':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CLOSED)
 if len(calls)!=41 or sum(y in starts for x,y in calls)!=0 or c._pair_digest(calls)!='f3b4906b6e5035114723638061c4c2c54bb61393af7b79756070c567c2a40c8c' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(35,2,4):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=182 or c._pair_digest(entries)!='ce786535f048d0048c9e7a5dd7b4064e4d8cee6a54ac945fbbf4b0673bcf45ab' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];rawcol=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or rawcol:raise c.AuditError('stored ingress changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\common\ui_common_api.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=7 or sum(any(a<=x<z for x in refs) for a,z in F)!=3 or c._pair_digest([(CELL,x) for x in refs])!='833e819bcf3b420a93c086ef3c3efba3357156583684914ca9a131d7112661e0':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any(x.get('path','').lower().endswith('ui_common_api.c') for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\common\ui_common_api.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':9,'ghidra_discovered_functions':9,'restored_functions':0,'path_anchored_functions':3,'raw_path_references':7,'body_bytes':892,'physical_bytes':960,'noncode_bytes':68,'reachable_instructions':330,'direct_body_calls':41,'internal_direct_body_calls':0,'external_direct_body_calls':41,'indirect_body_calls':0,'direct_bl_entry_sites':182,'stored_aligned_function_entry_pointers':0,'raw_interior_word_collisions':0,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':35,'iar_dlib_calls':2,'closed_first_party_calls':4,'cmsis_freertos_seams':[],'freertos_kernel_seams':[],'easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_ui_common_api_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
