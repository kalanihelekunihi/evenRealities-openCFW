#!/usr/bin/env python3
"""Fail-closed object/provider audit for teleprompt_timer_mgr.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-teleprompt-timer-mgr-function-map.tsv';PM=ROOT/'tools/manifests/g2-teleprompt-timer-mgr-provider-map.tsv';CL=ROOT/'tools/manifests/g2-teleprompt-timer-mgr-closure.tsv'
PINS={FM:'04e1a6241d91207fe5356de93f6f4a3ef6ba84e069b10d38a0b074ec691278c0',PM:'2d81b49269a6f577329515c0f44dc2ee735e5a3b052a5026ea2de0258f680a7e',CL:'f96616762e7481f78b7b2045f3ffe99febb4caeb1f6425f3dd82cd7c3b91226b'}
PHYS=(0x588D74,0x5893F0);EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC}
FIRST={0x44A1EA,0x45A568,0x5548C4,0x589B68}
TABLE=0x77C52C;TABLE_WORDS=(0,0,0x588D75,0x588DF5,0x588E43,0x588ECD);TABLE_POOL=0x5893B0;DISPATCH=(0x588F1A,0x588FE4)
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
 cmsis=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
 if cmsis['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cmsis['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c':raise c.AuditError('CMSIS-FreeRTOS changed')
 if json.loads((ROOT/'third_party/freertos-kernel/PROVENANCE.json').read_text())['upstream']['selected_commit']!='def7d2df2b0506d3d249334974f51e427c17a41c':raise c.AuditError('FreeRTOS-Kernel changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=13 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1498 or sh(body)!='489a2793b91e07cb71bc699ff41bb76923055a7b193ed43da1e25fc5efec6276' or len(ins)!=595 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='3bbc82dc7a42779bea09a95fff9ddca1d78080ca880ef8a69c60c7e50f99a1b9' or ind!=[0x588F92,0x589060]:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=162 or sh(non)!='c69771f3b8e8033b44b7c58b7ef157763883466c1998ad08dc75045eea7c6aa7' or sh(c._slice(b,*PHYS))!='55d714cf3c983ba2d675f4f13b628099071198668e84251b365ab6b61c84fe15':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='5fd0aeff8eb49bbc27bc7d0d4e492c2bf811e083e06ba5c0ccd9b7e1b5b00af3' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='ec7bf4e973704a13cf5b1923f0f31930024a7cc9981b61370c9ff8920b3b3946':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FIRST)
 if len(calls)!=74 or sum(y in starts for x,y in calls)!=9 or c._pair_digest(calls)!='88e2ec1db3743e4ae300296be2f0e0506c58e50a517aa0c22358214a215cd53c' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(55,3,7):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=13 or c._pair_digest(entries)!='460693959b20089285cfb15a8645a8c73d87bd454b257ce08441c3ac2c5b8a9f' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=4 or c._pair_digest(stored)!='7075a9526a7843011c6a3397569045fe7d63fb3397aee13d98732ebd88e609a9' or interior:raise c.AuditError('stored ingress changed')
 if struct.unpack_from('<I',b,TABLE_POOL-c.BASE)[0]!=TABLE or struct.unpack_from('<6I',b,TABLE-c.BASE)!=TABLE_WORDS:raise c.AuditError('callback table changed')
 if {v&~1 for v in TABLE_WORDS if v}-starts:raise c.AuditError('callback table escapes object')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 for d in DISPATCH:
  head=list(D.disasm(c._slice(b,d,d+0x14),d))
  if [i.mnemonic for i in head[:10]]!=['push','movs','movs','uxtb','cmp','bge','movs','uxtb','cmp','bne'] or head[4].op_str!='r0, #3' or head[8].op_str!='r0, #0':raise c.AuditError('dispatch range check changed')
 if cstring(b,0x6F0218)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_timer_mgr.c':raise c.AuditError('path changed')
 pairs=[(0x589360,x) for x in t.literal_references(b,0x589360)]
 if len(pairs)!=11 or c._pair_digest(pairs)!='832a5c41efc1fc1d95adb44c57375e06ddd15b25b96defca72c329635bc451be':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('teleprompt_timer_mgr' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\teleprompt\teleprompt_timer_mgr.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':13,'ghidra_discovered_functions':9,'restored_functions':4,'path_anchored_functions':5,'body_bytes':1498,'physical_bytes':1660,'noncode_bytes':162,'reachable_instructions':595,'direct_body_calls':74,'internal_direct_body_calls':9,'external_direct_body_calls':65,'indirect_body_calls':2,'bounded_timer_callback_table_entries':3,'direct_bl_entry_sites':13,'stored_function_entry_pointers':4,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':55,'cmsis_freertos_calls':3,'first_party_calls':7,'cmsis_freertos_seams':['osKernelGetTickCount'],'historical_timer_mgr_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
