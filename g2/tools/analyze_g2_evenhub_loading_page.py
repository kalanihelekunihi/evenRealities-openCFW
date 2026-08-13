#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for evenhub_loading_Page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import analyze_g2_ui_quicklist_page as quick
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-evenhub-loading-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-evenhub-loading-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-evenhub-loading-page-closure.tsv'
PINS={FM:'2d50793b142d53c34160620da5c53d92606242e36d07ec7b6c4ab5d8baa4faeb',PM:'5d525dd240ce71aa6c33abf3b226a3ed085334848769f72c5646ae7c827ef571',CL:'81b0dfe9424a7891ba22686754af61b5ec9613ea11c69c530d3db7ab33d57fac'}
PHYS=(0x492CB4,0x4935CC);PATH=0x6F3564;CELL=0x493510
EASY={0x43CE9E,0x43D0CE,0x43D574};RUNTIME={0x43C0E4,0x44B728};LVGL=quick.LVGL|{0x43F6AC}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=4 or sum(r['path_anchored']=='yes' for r in rows)!=2:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un or len(body)!=2042 or sh(body)!='ce8d1a0422787396d7ce472962e8f63b152c822b49ed1fe66280f9b0e1a4621a' or len(ins)!=761 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='f1253464c74bad9831eb9baae14b77d8bf2b74ea81c4aab6474a75d67e630bbe' or dyn:raise c.AuditError('body closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=286 or sh(outer)!='34b3add0099d99b6415ea0c23a7eaa699804b1b80f9f162f36b04ef81b087493' or sh(c._slice(b,*PHYS))!='85b0d97eebc1f8b74e20bbbeecbc18e49c9ced14aa25b65fe95e229911170801':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='a037bbda94e2f7e0fa099810a6bc02ec5e8a81ba4efd4e885d97d268f7ac6d7c' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='3cdf814075b69d43579aa8c38270309cd6179432c58d09363a9122d9f2c26069':raise c.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-RUNTIME
 if len(calls)!=138 or sum(t in starts for _,t in calls)!=1 or c._pair_digest(calls)!='3ccf377d5371a912856bc89bfd1df830564c2658e4cbcae605e25c82573a6ddb' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,RUNTIME,first))!=(36,85,2,14) or len(first)!=10:raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=2 or c._pair_digest(entries)!='d010421c0366387c951d54d45467379c3178ea61e8651df14364921a9cd83875' or strict or non or wide or ws:raise c.AuditError('branch ingress changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((c.BASE+off,v,t))
   if t in starts and (c.BASE+off)%4==0 and v&1:stored.append((c.BASE+off,v))
 if len(raw)!=6 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='61cdc3f31620c2f3b58877b4e1c40d47391ff36b5d00349018a4e75413732b40' or len(stored)!=2 or c._pair_digest(stored)!='620c4e793e70a69c37017d38252940b616df52b47de0b75a9cff643d6f3845ae':raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_loading_Page.c':raise c.AuditError('path changed')
 refs=sorted((CELL,a) for a in th.literal_references(b,CELL))
 if len(refs)!=18 or c._pair_digest(refs)!='329bde762a32f64ebbaf22365aad4c8cd1368a9325cfb6ef25e7221bee09a07e':raise c.AuditError('path refs changed')
 routed=any('evenhub_loading' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\EvenHub\evenhub_loading_Page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':4,'path_anchored_functions':2,'body_bytes':2042,'physical_bytes':2328,'outer_pool_bytes':286,'reachable_instructions':761,'direct_body_calls':138,'internal_direct_body_calls':1,'external_direct_body_calls':137,'indirect_body_calls':0,'direct_bl_entry_sites':2,'stored_function_pointers':2},'provider_boundary':{'lvgl_calls':36,'easylogger_calls':85,'runtime_calls':2,'first_party_calls':14,'historical_loading_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
