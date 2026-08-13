#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for dashboard ui_calendar_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import analyze_g2_ui_widget_news_page as news
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ui-calendar-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-ui-calendar-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ui-calendar-page-closure.tsv'
PINS={FM:'975e0a35950c91492a26cc65013b3f90b7b5dd9d18b5a02224903421fb027903',PM:'809ed7e98d659e18d02705f69968c41c38ea9b4b34733578ab6d585702dc462d',CL:'f89c03b3f2b76394f64852ce35dcbc3f578d25ba325ab47c0ce1a5adf7eccb11'}
PHYS=(0x4ED7D8,0x4EFF94);PATH=0x6EA7BC;CELLS=(0x4EDAA4,0x4EF98C,0x4EFF14)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4497B6,0x44981C};RUNTIME={0x439BE4,0x43C0E4,0x44A43C};LVGL=news.LVGL
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=15 or sum(r['path_anchored']=='yes' for r in rows)!=5 or sum(r['ghidra_discovered']=='yes' for r in rows)!=12:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z)
  if set(ins)&set(ii):raise c.AuditError('instruction overlap')
  ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un!=[(0x4EE6F6,0x4EE70C)] or len(body)!=9690 or sh(body)!='4c98014b9041e648d809ee3ab11cdc142020db43ccdd186c26ec6542c050ead3' or len(ins)!=3418 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='e5f946d4dbdb73f53f595baf0e9ab382f5d77f548776698623f84b5f7cca9017' or dyn:raise c.AuditError('body closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=504 or sh(outer)!='6a72780177c0dc3c7ff62bcd7c7cb0e565251a5c1a1e5316c0af248543757361' or sh(c._slice(b,*PHYS))!='7c3f4f78ade5b3e6c2a0bd37d18156ee25bf7ee50c029de9650c9ff492a21f89':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='2a3d7be58a1830241ef69f1ddb7b64e33d0d88843bd7a78f3ced0699ae09db9a' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='c88f4cb92b0b3ecb614f0fbdbd4cd18f8bcc90aa52556f7bbc1c45d3367750af':raise c.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-CMSIS-RUNTIME
 if len(calls)!=743 or sum(t in starts for _,t in calls)!=21 or c._pair_digest(calls)!='a2d98074d8fdd218ae3ddc483b2a06807b3b7c46f21d6dbb3303fa8af87faeb7' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,CMSIS,RUNTIME,first))!=(533,85,34,12,58) or len(first)!=14:raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=32 or c._pair_digest(entries)!='e56401b7413f6f88dc5c15cee0459fa29d20b5aa6222547d757583b1ddb95807' or strict or non or wide or ws!=[(0x4EDF2E,0x4EEAA2)]:raise c.AuditError('branch ingress changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((c.BASE+off,v,t))
   if t in starts and (c.BASE+off)%4==0 and v&1:stored.append((c.BASE+off,v))
 if len(raw)!=38 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='f78ccb263883d56f22a6c0c1360bad6fd36645778fc08c6405349fb0d9b6b888' or len(stored)!=3 or c._pair_digest(stored)!='335e45521f530beb7399fcc6ed360f7128ad7e9de9c17ccc95d61b38e7d78ca6':raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_calendar_page.c':raise c.AuditError('path changed')
 expected=((2,'3ed664e4f08debc6839fcf9c0323911654a999c60dbbf993424eebc73912417f'),(5,'8369f7423b76f91c6ca6d1972fa34e987bdc7fc7c0cbdba95ca080d832743556'),(10,'38ecf8eb03a2a4b466fb0fde71fba9a3d25198325a62baad3f249ecbc316fee7'))
 for cell,(n,d) in zip(CELLS,expected):
  refs=sorted((cell,a) for a in th.literal_references(b,cell))
  if len(refs)!=n or c._pair_digest(refs)!=d:raise c.AuditError('path refs changed')
 routed=any('ui_calendar_page' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\screens\ui_calendar_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':15,'path_anchored_functions':5,'body_bytes':9690,'physical_bytes':10172,'outer_pool_bytes':504,'reachable_instructions':3418,'direct_body_calls':743,'internal_direct_body_calls':21,'external_direct_body_calls':722,'indirect_body_calls':0,'direct_bl_entry_sites':32,'stored_function_pointers':3,'restored_functions':3},'provider_boundary':{'lvgl_calls':533,'easylogger_calls':85,'cmsis_freertos_calls':34,'runtime_calls':12,'first_party_calls':58,'historical_calendar_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
