#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for ui_widget_news_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
FM=ROOT/'tools/manifests/g2-ui-widget-news-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-ui-widget-news-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ui-widget-news-page-closure.tsv'
PINS={FM:'6f43b02ff610cd8c3de250efa80a75828124857b45e466dda588f99807669d87',PM:'b1f04dd0e5bdd98a6b058e24278fc530a2444fc0831badd7512bfb93258c025d',CL:'8121151e182691f4fa360e3b275a4c1a4f110702a7bbc5ea4a9c88923a621abc'}
PHYS=(0x004EFF94,0x004F5050);PATH=0x006EAE4C
PATH_CELLS=(0x004F0E08,0x004F189C,0x004F23DC,0x004F2EB0,0x004F33E8,0x004F3F80,0x004F4644,0x004F4F6C)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4497B6,0x44981C};RUNTIME={0x439BE4,0x439C04,0x43C0E4,0x44A43C,0x44B728,0x47CC60}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43FC70,0x43FCE0,0x43FD9E,0x43FDDA,0x44104C,0x441094,0x4410A6,0x441164,0x44120E,0x44121C,0x44122A,0x441238,0x441246,0x441254,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44140E,0x44142E,0x44143E,0x44144C,0x44145A,0x44146A,0x441478,0x44BDEA,0x44D7B8,0x44D878,0x44DCE2,0x44DDEA,0x44E368,0x44E3CA,0x44E498,0x44EA04,0x4503D6,0x450408,0x450500,0x4506CE,0x4515D2,0x45A568,0x498668,0x498680,0x499416,0x49942E,0x499678}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-common.BASE;e=b.find(b'\0',o)
 if o<0 or e<o:raise common.AuditError('unterminated retained path')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=common.IMAGE_SIZE or sh(b)!=common.IMAGE_SHA256:raise common.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise common.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cmsis=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cmsis['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53':raise common.AuditError('provider provenance changed')
 if '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise common.AuditError('LVGL provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 funcs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(funcs)!=45 or sum(r['path_anchored']=='yes' for r in rows)!=22 or sum(r['ghidra_discovered']=='yes' for r in rows)!=31:raise common.AuditError('function inventory changed')
 starts={a for a,_ in funcs};ins={};calls=[];dynamic=[];body=b'';uncovered=[]
 for a,z in funcs:
  ii,cc,dd=cfg._recover_function(b,a,z)
  if set(ins)&set(ii):raise common.AuditError('instruction overlap')
  ins.update(ii);calls+=cc;dynamic+=dd;body+=common._slice(b,a,z);uncovered+=common._uncovered((a,z),ii)
 calls.sort()
 if uncovered!=[(0x004F1EF6,0x004F1EFC)] or len(body)!=19058 or sh(body)!='80b867abc48e75a3e048dbf56ca7ddfc01d50786dae2a3dfe79a778ed63aba7e' or len(ins)!=6993 or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='4e559489dbcbfd1830f09888cceb98492eacf9cd9d81d2af18b498c17af2ddaa' or dynamic:raise common.AuditError('body closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),common._slice(b,*PHYS)) if a not in covered)
 if len(outer)!=1616 or sh(outer)!='c7109545f199b110a5e79a0f70875599b3de829cb45900df350bc600e0aa04d1' or sh(common._slice(b,*PHYS))!='bb4a6545f316cf445d5d01745a4ec7c525efd7cce64732f0792936fc11d5846e':raise common.AuditError('physical closure changed')
 if sh(common._slice(b,PHYS[0]-16,PHYS[0]))!='75d93a019e1694fa4ad2090b82e0f32f50ef4194c60f7ee04e5270064f0a294b' or sh(common._slice(b,PHYS[1],PHYS[1]+16))!='465e7000a8fd784ed0461585752fb003ffd73af8aaa697f7e9d23662ec17493e':raise common.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-CMSIS-RUNTIME
 if len(calls)!=1252 or sum(t in starts for _,t in calls)!=56 or common._pair_digest(calls)!='9b619585e6609056e8146a48ada2dc281973bd7f9db63423b557429f7d3a62fd' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,CMSIS,RUNTIME,first))!=(508,565,8,36,79) or len(first)!=23:raise common.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];noncode=[];wide=[];wide_strict=[]
 for a in range(common.BASE,common.BASE+len(b)-3,2):
  t=thumb._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:noncode.append((a,t))
  x,y=struct.unpack('<HH',common._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:wide_strict.append((a,t))
 if len(entries)!=70 or common._pair_digest(entries)!='22fb5f9f5021cbe9615e8e77fe37c4428533263e57f5d0cf84ac1643b6a1f73d' or strict!=[(0x004EF5C4,0x004F4678),(0x004EF5D4,0x004F4688)] or noncode!=[(0x004EF58C,0x004F4640),(0x004EF59A,0x004F464E),(0x004EF5A8,0x004F465C),(0x004EF5B6,0x004F466A),(0x004EF5E2,0x004F4696)] or wide or wide_strict!=[(0x004F0018,0x004F0916),(0x004F0102,0x004F0916),(0x004F3498,0x004F3F68),(0x004F34E6,0x004F3F68),(0x004F3574,0x004F3F64),(0x004F3608,0x004F3F68),(0x004F367C,0x004F3F64),(0x004F36DC,0x004F3F64)]:raise common.AuditError('branch classification changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((common.BASE+off,v,t))
   if t in starts and (common.BASE+off)%4==0 and v&1:stored.append((common.BASE+off,v))
 if len(raw)!=37 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='e38f7f534cc77469bdc2c5365bfdbec2ff4efa976f71f8d08449bdb37afa9fea' or len(stored)!=12 or common._pair_digest(stored)!='614b3d3f740d41c3ea6157d9a289cbed15c9f1722f44947a118683a5578391c6':raise common.AuditError('stored-entry closure changed')
 if cstring(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_widget_news_page.c':raise common.AuditError('path changed')
 refs=sorted((cell,a) for cell in PATH_CELLS for a in thumb.literal_references(b,cell))
 if len(refs)!=113 or common._pair_digest(refs)!='589acb568a04dac402043e048025fbfc031df7fbf12e894581e1d745378a2e9e':raise common.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('ui_widget_news_page' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise common.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':common.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\screens\ui_widget_news_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':45,'ghidra_discovered_functions':31,'path_anchored_functions':22,'restored_non_anchor_functions':14,'body_bytes':19058,'physical_bytes':20668,'outer_pool_bytes':1616,'reachable_instructions':6993,'direct_body_calls':1252,'internal_direct_body_calls':56,'external_direct_body_calls':1196,'indirect_body_calls':0,'direct_bl_entry_sites':70,'stored_function_pointers':12,'classified_pseudo_bl':7,'classified_wide_interior_branches':8},'provider_boundary':{'lvgl_calls':508,'easylogger_calls':565,'cmsis_freertos_calls':8,'runtime_calls':36,'first_party_calls':79,'lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','historical_news_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
