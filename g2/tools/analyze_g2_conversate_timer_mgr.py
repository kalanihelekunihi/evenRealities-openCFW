#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_timer_mgr.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-conversate-timer-mgr-function-map.tsv';PM=ROOT/'tools/manifests/g2-conversate-timer-mgr-provider-map.tsv';CL=ROOT/'tools/manifests/g2-conversate-timer-mgr-closure.tsv'
PINS={FM:'767609c752c4d1732d51655506b65765cfe422a9aa43a9a58ec2cebb0e4aeaaa',PM:'9a31311fd41f7d5d41ae38965a060de8d8f897d701c77d92a3c805f627f7de4a',CL:'fa3bf5688d351fef8ed1a946cc4147472a95db54287fa676d13fe9aded4f2a9c'}
PHYS=(0x5B3570,0x5B3EF8);EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC}
FIRST={0x44A1C6,0x45A568,0x5B02E4,0x5B16DC,0x5B57AC}
TABLE=0x75EA90;TABLE_WORDS=(0,0,0x5B3767,0x5B37C9,0x5B37D9,0x5B383D,0x5B384D,0x5B38B7);TABLE_POOL=0x5B3E2C;DISPATCH=0x5B36BE
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
 if len(F)!=24 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2204 or sh(body)!='3f08c5bebc030c1ad3e7612979061bd029606370f94105dbe4f6d19f0998a1fe' or len(ins)!=836 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='3f13c4890306136d6276d31a3ec2e4e385074903da37277f852ee6070c0edfc2' or ind!=[0x5B36F4,0x5B3712]:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=236 or sh(non)!='3ffe68bfda304dea5064599a5119e7d359c1bff4ad782f01a7999e3ea2bf39ab' or sh(c._slice(b,*PHYS))!='bbefc4cb85defe08a5f5581703cbe458f83bd2dbf2eff0c2a9293eaa5d660e8b':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='67d4d40f14635ae4806bd427fafbf041a265bf44f101b61bf7feda521cb27eef' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='d632b43062b5ef1186f07143a7c0f64e60e963c7d60bba600b8247a9b6c85e43':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FIRST)
 if len(calls)!=129 or sum(y in starts for x,y in calls)!=27 or c._pair_digest(calls)!='115ed90df730bd79219ee40f8fd7eed50ecf29ddfd94faf395a370fa16787fa5' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(85,2,15):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=33 or c._pair_digest(entries)!='b3d485702640b7c4da7050efd1bab856f2caf0d9dd2efad40cbb65e479f522c0' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=6 or c._pair_digest(stored)!='a85efd9923d77116c2178e34982c5898a44c4106511b3cb086e584e01b3a5baa' or interior:raise c.AuditError('stored ingress changed')
 if struct.unpack_from('<I',b,TABLE_POOL-c.BASE)[0]!=TABLE or struct.unpack_from('<8I',b,TABLE-c.BASE)!=TABLE_WORDS:raise c.AuditError('callback table changed')
 if {v&~1 for v in TABLE_WORDS if v}-starts:raise c.AuditError('callback table escapes object')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);head=list(D.disasm(c._slice(b,DISPATCH,DISPATCH+0x14),DISPATCH))
 if [i.mnemonic for i in head[:8]]!=['push','movs','uxtb','cmp','beq','movs','uxtb','cmp'] or head[3].op_str!='r2, #0' or head[7].op_str!='r2, #4':raise c.AuditError('dispatch range check changed')
 if cstring(b,0x6EC668)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_timer_mgr.c':raise c.AuditError('path changed')
 pairs=[(0x5B3E14,x) for x in t.literal_references(b,0x5B3E14)]
 if len(pairs)!=17 or c._pair_digest(pairs)!='f5d42f56c6e1116fc15de6d8168b4a6f186225420956938868d431affd74fb87':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('conversate_timer_mgr' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\conversate\conversate_timer_mgr.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':24,'ghidra_discovered_functions':9,'restored_functions':15,'path_anchored_functions':7,'body_bytes':2204,'physical_bytes':2440,'noncode_bytes':236,'reachable_instructions':836,'direct_body_calls':129,'internal_direct_body_calls':27,'external_direct_body_calls':102,'indirect_body_calls':2,'bounded_timer_callback_table_entries':4,'direct_bl_entry_sites':33,'stored_function_entry_pointers':6,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':85,'cmsis_freertos_calls':2,'first_party_calls':15,'cmsis_freertos_seams':['osKernelGetTickCount'],'historical_timer_mgr_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
