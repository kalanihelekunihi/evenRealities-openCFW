#!/usr/bin/env python3
"""Fail-closed object/provider audit for list_anim.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-list-anim-function-map.tsv';PM=ROOT/'tools/manifests/g2-list-anim-provider-map.tsv';CL=ROOT/'tools/manifests/g2-list-anim-closure.tsv'
PINS={FM:'fd1f00148c810be975573be33f293781baf8dcd4e8053b875411fe6bbba3d8fc',PM:'2f54a7b10f0bad9f4d152a0e5a6e2df14ed912ceefebe58cc5b331d97c23cf1f',CL:'7c786eb4205a8fd97f98f9c5da498a0efd0f55358bc21d0594fe55b248335a94'}
PHYS=(0x5893F0,0x5899A4);PATH_CELL=0x589940;PATH_RUN=0x70C364
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};CMSIS={0x4490CC}
LVGL={0x43E2D4,0x43FDDA,0x44104C,0x4413CE,0x44140E,0x44DCA2,0x44DCE2,0x44DDEA,0x44DE92,0x44E498,0x44EA2E}
FIRST={0x58C622,0x58C6C4}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('LVGL changed')
 if 'd213f261b5be6bb29a7cce8b84071706b72f4d53' not in (ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text():raise c.AuditError('CMSIS-FreeRTOS changed')
 iar=(ROOT/'docs/research/iar-dlib-runtime-census.md').read_text()
 if '9.20 is therefore a practical lower bound' not in iar or '9.60.2' not in iar:raise c.AuditError('IAR changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 provenance()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=11 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1348 or sh(body)!='134be743a87f7a32d7cfa52848785fe9d3ec294233ff4d9d6b24ff34a76ce475' or len(ins)!=512 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='82bb5a3598928045990744551225f5774a63e0b17fc6fbccaa445cccaf07faef' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=112 or sh(non)!='da559afedbb8bfae13a7a6aa15df684500da82662ab746f8f29b52c15cffd280' or sh(c._slice(b,*PHYS))!='7b7bbc3f0c07307379f2ebbb724fb13ce5ab1fddd4d9847b06dbf699279d144c':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='5a85880e0adb59c460a936a5abdf782c3a849f312a72455d77f00487291cfd11' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='ab281321ad3bf2c6f9f7da611d6bd231e8e0a8a53b83fbb2cbc93677eea4bedd':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,LVGL,FIRST)
 if len(calls)!=85 or sum(y in starts for x,y in calls)!=12 or c._pair_digest(calls)!='189aacbc8d96b5d04cb3afcda6de4e9a7e39f0c5ad3900e3f8ea78fd9d1ecaf4' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(40,2,2,27,2):raise c.AuditError('call closure changed')
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=37 or c._pair_digest(entries)!='f438c906d4adf44597fe0dc9401c034c1360219249f5bcfb9ebc87edaa50bc45' or strict or unknown:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored!=[(0x589958,0x58949F)] or c._pair_digest(stored)!='f678608b879335e45811760d9dc88da9c9ab56130948db9593f8fba87a2ae231' or interior:raise c.AuditError('stored ingress changed')
 if cstring(b,PATH_RUN)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\list_anim.c' or struct.unpack_from('<I',b,PATH_CELL-c.BASE)[0]!=PATH_RUN:raise c.AuditError('path changed')
 pairs=[(x,PATH_CELL) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=8 or c._pair_digest(pairs)!='7dedba7689769acb38bb72c251a75e2a520cf6a4f26ca1c39c0faf7e8fb31e39':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('list_anim' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\anim\list_anim.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':11,'ghidra_discovered_functions':7,'restored_functions':4,'path_anchored_functions':7,'body_bytes':1348,'physical_bytes':1460,'noncode_bytes':112,'reachable_instructions':512,'direct_body_calls':85,'internal_direct_body_calls':12,'external_direct_body_calls':73,'indirect_body_calls':0,'direct_bl_entry_sites':37,'stored_function_entry_pointers':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':40,'iar_dlib_calls':2,'cmsis_freertos_calls':2,'lvgl_calls':27,'closed_fade_anim_calls':2,'cmsis_freertos_seams':['osKernelGetTickCount'],'freertos_kernel_seams':[],'historical_list_anim_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
