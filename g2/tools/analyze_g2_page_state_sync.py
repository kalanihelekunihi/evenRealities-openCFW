#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/dashboard/page_state_sync.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-page-state-sync-function-map.tsv';PM=ROOT/'tools/manifests/g2-page-state-sync-provider-map.tsv';CL=ROOT/'tools/manifests/g2-page-state-sync-closure.tsv'
PINS={FM:'15d1ee55a51a1a6a75d30e115d499a513107da1f9955b45ee3e51c9004d7fb7e',PM:'3885b01934872c8a8986524c94d7d3d8ae5d5df5605871625f4db15da8e7ecb6',CL:'185a3c56d50e5306f59a63cdb76622d82a166688fd03c91aeae6f573cef3187f'}
PHYS=(0x4FFE14,0x500378);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};NANOPB={0x48949C};FIRST={0x45A570,0x4FF7DC,0x558142}
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
 if len(F)!=8 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1244 or sh(body)!='841f4532004309f7aa257ee3b4966c5dae3b9f60f85758b1374a4bfdad636c7d' or len(ins)!=492 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='f45eb5def5aa27435be5d294ace4b088d37822fa8514b2ef4706a6f2acc7bae6' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=136 or sh(non)!='e6f839b50180e2c4d1ddb92a4f4a54cc178451eec7c2ce65db19d0b284e9c77c' or sh(c._slice(b,*PHYS))!='ec6e19eb86a48c300a0bf91e70885b899b0235753a2b164820d9a72a97b92a43':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='ad6ba23ad1468fcda93f5eb6c78017d10353977ae2a5fc264692b36d112f68c6' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='010881a386cfa18500db646144739e2aaa28d3ede1db175f8dabe9486cb91883':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,NANOPB,FIRST)
 if len(calls)!=62 or sum(y in starts for x,y in calls)!=5 or c._pair_digest(calls)!='58483e9a384c805f3a31d82a0bd55f73128e74e70d679f1d5aeb12f4e0e3ea8a' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(50,3,1,3):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=27 or c._pair_digest(entries)!='3593edb5512ce6b646a6878839dd41d32d917ddcec5720c984ff3620a7eaf985' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or len(interior)!=22 or c._pair_digest(interior)!='9376feb123a09ff53a6f1d4b715f93e3bd39406bfec3a0f61573b9eb96625f51':raise c.AuditError('stored ingress changed')
 pairs=[(0x5002FC,x) for x in t.literal_references(b,0x5002FC)]
 if len(pairs)!=10 or c._pair_digest(pairs)!='2c995867f41f6470294c2121d71069d0cb320e20979fa3ddb7991a7c587bdcd5':raise c.AuditError('path refs changed')
 off=0x6FBCCC-c.BASE
 if b[off:b.find(b'\0',off)].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\page_state_sync.c':raise c.AuditError('retained path changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('page_state_sync' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\page_state_sync.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':8,'ghidra_discovered_functions':6,'restored_functions':2,'path_anchored_functions':7,'body_bytes':1244,'physical_bytes':1380,'noncode_bytes':136,'reachable_instructions':492,'direct_body_calls':62,'internal_direct_body_calls':5,'external_direct_body_calls':57,'indirect_body_calls':0,'direct_bl_entry_sites':27,'stored_function_entry_pointers':0,'raw_instruction_word_interior_collisions':22,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':50,'iar_dlib_calls':3,'nanopb_calls':1,'first_party_calls':3,'historical_page_state_sync_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
