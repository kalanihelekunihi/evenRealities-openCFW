#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_watchface_layout2.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-dashboard-watchface-layout2-function-map.tsv';PM=ROOT/'tools/manifests/g2-dashboard-watchface-layout2-provider-map.tsv';CL=ROOT/'tools/manifests/g2-dashboard-watchface-layout2-closure.tsv'
PINS={FM:'bd4a60a56d4a770c153041d506832cb0ad546b52ad0bae133835d573f3f56b30',PM:'1428ae6168f55c520c5ea54538c024ee41fc1439d59e59d724e24ef56bd76323',CL:'9a4e54bf410b765aa353514b71f38ce1c7c361976c7c23bf22262dc07b505667'}
PHYS=(0x5B90E8,0x5B9CEC);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};PRINTF={0x4B4728}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F4C0,0x43F506,0x43F568,0x43F6D6,0x44104C,0x441254,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x44140E,0x44142E,0x44143E,0x44146A,0x44D7B8,0x498668,0x498680,0x499416,0x49942E}
FIRST={0x44A19A,0x45FFFE,0x460084,0x47D8CE,0x47D9C4,0x47D9CC,0x48BA78,0x48BA92,0x49C5BC,0x4FFC32,0x4FFC90,0x509F8E,0x5B8A6A,0x5B8A9C,0x5B8BC8,0x5B8D20,0x5B8DD0,0x5B8E1A,0x5B8E4A,0x5B8E72,0x5B8E84,0x5B8ECE,0x5B8F18,0x5B90AE}
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
 if len(body)!=2844 or sh(body)!='4e55df50318814c510602ff47815610b21da75f9c49b880b9478ff27999758be' or len(ins)!=1073 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='f9d353663db707ad568e0f8393f0ce8ed4c941c3f5ceefc92fd1f03cc0f76ee7' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=232 or sh(non)!='bca8aa4838c870c2eab9c97fb7d66c89eb84295533ca1e99c2e357d1d00f153f' or sh(c._slice(b,*PHYS))!='4bcdd884ab77c7996d3e71501e0f6cdc882656c8d774409f7be1df595ae24e5d':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='37b5c383c36a683e8ff7281ebb8969d2246f50c8b517cbb6562edfa29ef4b451' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='1056875846aa769c29e5b76e8c788be568cb67dea4ffc56c1cebd0af573ccb1b':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,PRINTF,FIRST)
 if len(calls)!=182 or sum(y in starts for x,y in calls)!=1 or c._pair_digest(calls)!='8c66b62945157ec113578f27d919eb2b90fa0cd7423758f82f835b7babe5f1c0' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(20,104,9,5,43):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=1 or c._pair_digest(entries)!='c864fc91d08459bd07021c5f164bed20e9891d8d8b6ee189957a9b830a897d1c' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if len(stored)!=18 or c._pair_digest(stored)!='ffeb94d92bb8e5a3c38273c770a53de5ed1bcd8f5960d4cf5574acc188767b48' or interior:raise c.AuditError('stored ingress changed')
 pairs=[(0x5B9C6C,x) for x in t.literal_references(b,0x5B9C6C)]
 if len(pairs)!=4 or c._pair_digest(pairs)!='118d46b9948813555d66d1fef2d4bf573ca26d5a620032e236323e26717da1b6':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('dashboard_watchface_layout2' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\dashboard_watchface_layout2.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':19,'ghidra_discovered_functions':6,'restored_functions':13,'path_anchored_functions':1,'body_bytes':2844,'physical_bytes':3076,'noncode_bytes':232,'reachable_instructions':1073,'direct_body_calls':182,'internal_direct_body_calls':1,'external_direct_body_calls':181,'indirect_body_calls':0,'direct_bl_entry_sites':1,'stored_function_entry_pointers':18,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':20,'lvgl_calls':104,'iar_dlib_calls':9,'mpaland_printf_calls':5,'first_party_calls':43,'historical_layout2_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
