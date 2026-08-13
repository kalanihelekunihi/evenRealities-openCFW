#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/module_configure/general_configure.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-general-configure-function-map.tsv';PM=ROOT/'tools/manifests/g2-general-configure-provider-map.tsv';CL=ROOT/'tools/manifests/g2-general-configure-closure.tsv'
PINS={FM:'cbb6fef02d0db3e2d647f2099c90216e490746169c0a86a164e9e6defbb95dc5',PM:'24d476187133fd1751b0c50fe439775dc37dc98c09e4761189d12dead56aa2d5',CL:'0e0f6b6377f0c114e6abf60720e1a1cbe361f153441387508618aa072ad864a1'}
PHYS=(0x471164,0x471B9C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4};CMSIS={0x4495E4};NANOPB={0x48F49C,0x490120,0x4905F4,0x490C32};FIRST={0x465480,0x475B14,0x49240E,0x4924F6}
STORED=[(0x6A4534,0x4716BB)];STRICT=[(0x5F132A,0x47137C),(0x5F134A,0x47139C)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53':raise c.AuditError('CMSIS-FreeRTOS changed')
 if json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=10 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2376 or sh(body)!='ac6167490d24eed4d23f5a369cc92f7c6d62736ce7b04e8cdd6228e7b64b638c' or len(ins)!=905 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='9fe3781d3c55a18cbe42756e78a44084c424642b308af0f56e1b49ade2cb7d79' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=240 or sh(non)!='4a87638c7d74b0471313d5899627d2684cbc972ae13785522c2673a2a328816f' or sh(c._slice(b,*PHYS))!='25fdbbf0f3e0e924e2ae1d08c9873a3e57372c51f7970893206392b1c52b7fdd':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='b588d710fa47475951ede5af5286f81b20070b1e890667a3f9dffba1626d493b' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='ca2eb6bb3438f6e9fc177fb6d0e6fc3cd1dffd03ca8f7831786df13ff67e7ce2':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,NANOPB,FIRST)
 if len(calls)!=146 or sum(y in starts for x,y in calls)!=5 or c._pair_digest(calls)!='447b3ab5c0376223c907e3a4206ee4d6e85048c2307b91b55930ea2eafd72770' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(110,13,3,8,7):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=10 or c._pair_digest(entries)!='494b931e3608062ab5b23d95486884c0e213cdc3fa2fd6c33d65b149c2982733':raise c.AuditError('BL ingress changed')
 if strict!=STRICT or c._pair_digest(strict)!='8024f7939e2b134bff20370095c0e38536dffb6fc4880901c94b77cd8d5190b4':raise c.AuditError('secondary entry ingress changed')
 for a,y in STRICT:
  ii,_,_=q._recover_function(b,y,0x47142A)
  if not set(ii)<=ins.keys():raise c.AuditError('secondary entry body changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or c._pair_digest(stored)!='96062ce0874cb1caa8fbf8886982845b24d4879060f66cebdb9efb87a86fa84b' or interior:raise c.AuditError('stored ingress changed')
 pairs=[(0x471ADC,x) for x in t.literal_references(b,0x471ADC)]
 if len(pairs)!=22 or c._pair_digest(pairs)!='0df334ba67e23ddd6c908fd99cca7d134a84a69f5f80c4343dd24ae655c588f0':raise c.AuditError('path refs changed')
 off=0x6E8158-c.BASE
 if b[off:b.find(b'\0',off)].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\module_configure\general_configure.c':raise c.AuditError('retained path changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('general_configure' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\module_configure\general_configure.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':10,'ghidra_discovered_functions':4,'restored_functions':6,'path_anchored_functions':7,'merged_body_secondary_entries':2,'body_bytes':2376,'physical_bytes':2616,'noncode_bytes':240,'reachable_instructions':905,'direct_body_calls':146,'internal_direct_body_calls':5,'external_direct_body_calls':141,'indirect_body_calls':0,'direct_bl_entry_sites':10,'stored_function_entry_pointers':1,'raw_instruction_word_interior_collisions':0,'strict_interior_ingress':2},'provider_boundary':{'easylogger_calls':110,'iar_dlib_calls':13,'cmsis_freertos_calls':3,'cmsis_freertos_seams':{'osEventFlagsSet':3},'nanopb_calls':8,'first_party_calls':7,'historical_general_configure_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
