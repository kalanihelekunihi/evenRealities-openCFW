#!/usr/bin/env python3
"""Fail-closed object/provider audit for service_universal_setting.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-service-universal-setting-function-map.tsv';PM=ROOT/'tools/manifests/g2-service-universal-setting-provider-map.tsv';CL=ROOT/'tools/manifests/g2-service-universal-setting-closure.tsv'
PINS={FM:'ac1d8bb38a72aea63cc54d81184789723b292b6833fb6e1f93d0c4a4c0941ecb',PM:'031da2000e1e165b5b9629163044c449fcc048ffddbc0d48f866009c9ea63a71',CL:'fdcf9c7d1bf4adcdb3209beb08342c2d648a91037b825147c4d4e45b23b02f51'}
PHYS=(0x466010,0x46687C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4,0x4751C8};CRC={0x49ACD4};KV={0x49ADF0,0x49AF74,0x49B0F8};FIRST={0x448E34,0x45A568,0x465480}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if 'runtime_crc16_ccitt.c' not in (ROOT/'components/apollo_main/core_overlay/overlay.json').read_text():raise c.AuditError('CRC provider changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=15 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2010 or sh(body)!='2d58b57cd110c3a85179dce649f016e400602e9b3983902627d361229288a22c' or len(ins)!=808 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='d267759976b479ca6368cf586b0f45536189f2d61197d9bc444b80e78e352463' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=146 or sh(non)!='c497a695fe46764713a9ba63860c76364ef8092f5665c6b2c2d83c2c47cb38d0' or sh(c._slice(b,*PHYS))!='a87c440e6017d5215d9f2f7d7579e0271cf7f7fb94f62847b09a2792e6ae8534':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='8c1254d423345c769e00ffc61cd4e3f194ea4e2d0130fb2ba9c363660c82d2b9' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='12edb5113d076d2003e37728f56a7198c964f8764f4dbc0fd66fa15d1c410953':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CRC,KV,FIRST)
 if len(calls)!=106 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!='b5ac88e09d65bc8bfbef5a7e6384749a91ce6c6d65c05d8b28076ee84de28692' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(75,17,3,3,5):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=81 or c._pair_digest(entries)!='44eabfc8ac0a80d885b8a59f0fd49c3483cdaf214119e51531d5c4719c64a6e4' or len(strict)!=1 or c._pair_digest(strict)!='d12fd22b391d8ec65731d6aaec7a23cd909b328b35eb679455a5eab690caf2af':raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored or len(interior)!=2 or c._pair_digest(interior)!='7ebc994f95313798012370a3284b21d641a2c681369ec25035f23033fbb494d2':raise c.AuditError('stored ingress changed')
 pairs=[(0x4667FC,x) for x in t.literal_references(b,0x4667FC)]
 if len(pairs)!=15 or c._pair_digest(pairs)!='e68a810889ead7a8e045e50d593db574973065e313cdcf5946ad3a073390bcbe':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('service_universal_setting' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\service\service_universal_setting\service_universal_setting.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':15,'ghidra_discovered_functions':5,'restored_functions':10,'path_anchored_functions':5,'body_bytes':2010,'physical_bytes':2156,'noncode_bytes':146,'reachable_instructions':808,'direct_body_calls':106,'internal_direct_body_calls':3,'external_direct_body_calls':103,'indirect_body_calls':0,'direct_bl_entry_sites':81,'stored_function_entry_pointers':0,'strict_interior_ingress':1},'provider_boundary':{'easylogger_calls':75,'iar_dlib_calls':17,'source_owned_crc_calls':3,'closed_kv_calls':3,'first_party_calls':5,'historical_universal_setting_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
