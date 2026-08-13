#!/usr/bin/env python3
"""Fail-closed object/provider audit for sync_info.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-sync-info-function-map.tsv';PM=ROOT/'tools/manifests/g2-sync-info-provider-map.tsv';CL=ROOT/'tools/manifests/g2-sync-info-closure.tsv'
PINS={FM:'818bf8e83fabd5216a11326a7410dd53f7e0c7b99e34c584e6be3eda65e5f4d9',PM:'8e56d681daeec63cea981f417e280e997ab43c1fe8ef5339b2bf024b760fd9f7',CL:'71b59d61a268db5351b661739a563c5bfca3ac2985b079563dfe83d53c30d384'}
F=((0x471EE8,0x471FA4),(0x471FA4,0x472102),(0x472102,0x4721F4))
PHYS=(0x471EE8,0x472244);POOL=(0x4721F4,0x472244);PATH=0x70643C;CELL=0x472208
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4};NANOPB={0x48F49C,0x490120,0x4905F4,0x490C32};CLOSED={0x443504,0x474CD2,0x474D16,0x475B14,0x475C1A}
STORED=[(0x6A4664,0x472103)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());nano=json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or nano['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('provider provenance changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=3 or sum(r['source_path_anchor']=='yes' for r in rows)!=3 or sum(r['ghidra_discovered']=='yes' for r in rows)!=3:raise c.AuditError('function inventory changed')
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  if set(ins)&set(ii):raise c.AuditError('overlap')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=780 or sh(body)!='1cd19bf8937780bc39edb9364f9f1ee465589c0761a1dc4dcd85e894076ca569' or code!=body or len(ins)!=326 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='5e559dfa7d5cfeb1c0c3f826cf64daab6ffc2433ce330690f6fb2d2c6f2c25ab' or ind:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=80 or sh(non)!='cdadc69245fb572ca75208d8945fcf441559eb7d7aac9d254181286b8478b5ec' or non!=c._slice(b,*POOL) or sh(c._slice(b,*PHYS))!='cb871397e3ad9999c1379199c78e231b160aa859c51497b94a832a38c1939bf5':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='f897dc57489bf4cdcfcefe2344e8b8919de2d3e8ea81558821546396253fd35a' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='a7957a93e4ddd94bfe1eedb66090a7076796bea10cddfba433a2f7d2fa9de8c2':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,NANOPB,CLOSED)
 if len(calls)!=56 or sum(y in starts for x,y in calls)!=1 or c._pair_digest(calls)!='4212dd8409bee70120a0db15e5686870dded9c8c85057fb536bcfbf65082dc66' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(30,8,6,11):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=8 or c._pair_digest(entries)!='4bc8cb9e0f680875088d28870cf53c9bd0c446bee70b3dc9eaef9005e9ac9f8e' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];rawcol=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or rawcol:raise c.AuditError('stored ingress changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\sync_info\sync_info.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=6 or sum(any(a<=x<z for x in refs) for a,z in F)!=3 or c._pair_digest([(CELL,x) for x in refs])!='2a2cc2e0c3562c5f54a2e453b2d247156f4c6743371fe9f01e0f88868355c78a':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any(x.get('path','').lower().endswith('sync_info.c') for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\sync_info\sync_info.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':3,'ghidra_discovered_functions':3,'restored_functions':0,'path_anchored_functions':3,'raw_path_references':6,'body_bytes':780,'physical_bytes':860,'noncode_bytes':80,'reachable_instructions':326,'direct_body_calls':56,'internal_direct_body_calls':1,'external_direct_body_calls':55,'indirect_body_calls':0,'direct_bl_entry_sites':8,'stored_aligned_function_entry_pointers':1,'raw_interior_word_collisions':0,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':30,'iar_dlib_calls':8,'nanopb_calls':6,'closed_first_party_calls':11,'cmsis_freertos_seams':[],'freertos_kernel_seams':[],'nanopb_commit':'98bf4db69897b53434f3d0ba72e0a3ab1a902824','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_sync_info_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
