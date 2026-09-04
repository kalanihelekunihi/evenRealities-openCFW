#!/usr/bin/env python3
"""Fail-closed linked-object audit for the G2 production gray screen."""
from __future__ import annotations
import csv, hashlib, json, struct, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'; BASE=0x437FE0
sys.path.insert(0,str(ROOT/'tools'))
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-pdt-gray-screen-function-map.tsv'; CLOSURE=ROOT/'tools/manifests/g2-pdt-gray-screen-closure.tsv'
PINS={FM:'e2fa2e3bbdad9eaa58334aa9f05f819051bb820111fdb0835c309b23c7ab4a3a',CLOSURE:'709e9687c0d87b1d184d7e0df240a4aadebb1cf4134bb65e59321a5f7b58e079'}
PHYS=(0x5CF634,0x5CF7A8); PHYS_SHA='cc54723cf804434f6c43210a0f6cfa27ac08f770a199cd199f69d157598f6db8'; BODY_SHA='123af7b5377985763178d0cc2208acfe93e627bf24280ee59335297d0ba92fff'
POOL=(0x5CF788,0x5CF7A8); POOL_SHA='25a8a137f4c51e00f96088314261b55838eacb8dab0358afd1dadcd44ea2f1bc'; NEXT=(0x5CF7A8,0x5CF7F2); NEXT_SHA='b2c776e944bc8876c6d2fd1c2292785ddde2536891c3dd7e1966406deab4b0a3'
DESC=(0x6A45D0,0x6A45E0); DESC_SHA='ff87ec0080513646b1337f1821589077db72f4d8c0c8d9443983ddf50afa520e'; CALL_SHA='7d8d75977f908ce2407d7d6c355ffa35acc8bb13e6eea0f7584a4f40a0eb827c'; STORED_SHA='8973f2e6c2916b4ac776adc7a67381d8bd6a91dd5ad06a40abb8fdf342e43a34'
PATH=0x6F5314; RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\PdtGrayScreen\pdt_gray_screen.c'; NEXT_PATH=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\ProductionTest\production_test.c'
WORDS={0x5CF788:0x7580D0,0x5CF78C:0x7580AC,0x5CF790:PATH,0x5CF794:0x787F60,0x5CF798:0x72BE2C,0x5CF79C:0x20074880,0x5CF7A0:0x78DF8C,0x5CF7A4:0x20003080,0x6A45D0:0x10F,0x6A45D4:0x5CF635,0x6A45D8:0x5CF67F,0x6A45DC:0x20003080,0x6A45E0:0x10B,0x6A45E4:0x5CF7A9,0x6A45E8:0x5CF7F3,0x6A45EC:0x200030A0,0x79373C:0x5CF67B}
STRINGS={PATH:RETAINED,0x7580D0:'PdtGrayScreen recv data len = %d',0x7580AC:'PdtGrayScreen_common_data_handler',0x787F60:'pdt_gray_screen',0x72BE2C:'[pdt_gray_screen]PdtGrayScreen recv data len = %d',0x6EEE68:NEXT_PATH}
STORED=[(0x6A45D4,0x5CF635),(0x6A45D8,0x5CF67F),(0x79373C,0x5CF67B)]
SOURCE=ROOT/'components/apollo_main/core_overlay/pdt_gray_screen.c'; HEADER=ROOT/'components/apollo_main/core_overlay/pdt_gray_screen.h'; CONFIG=ROOT/'components/apollo_main/core_overlay/overlay.json'; REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json'; MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
NAMES=('open_cfw_pdt_gray_common_data_handler','open_cfw_pdt_gray_predicate','open_cfw_pdt_gray_screen_event'); PATCHES=tuple(f'replace_pdt_gray_screen_{i:02d}' for i in range(1,4)); F=((0x5CF634,0x5CF67A),(0x5CF67A,0x5CF67E),(0x5CF67E,0x5CF788))
SOURCE_PIN=(4699,'85832459ba3b032759a4249fbcee7c26049107c0b772fa4bd2726146ed379709'); HEADER_PIN=(505,'f4c02403fa4b8f11ae551173d5ba56863faf2a7a2423203fbcd6df72f3db1d4b')
PROVIDER_TARGETS=(4447874,4448164,4453638,4453736,4448164,4460620,4461182,4461214,4461292,4447874,4448164,4453568,4452506,4461340,4461674,4460648,4461182,4461214)
ROUTES={
 'apple-clang':{'path':ROOT/'components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin','component':'4ced07de526820d5eb97273a6c1418d751bff6bdd2e315150d559806e986696b','targets':(0x4C4990,0x4C498C,0x46CBE4),'sizes':(4,4,242),'text':('a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4','64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb','0e91960c969cfdcacd1834f856852c6eaeaf9d4fd523061f897fff7430ed5235')},
 'linux-clang':{'path':ROOT/'build/canonical-provider/linux-clang/apollo_main/ota_s200_firmware_ota.bin','component':'226865166edf39ce3349bf44061d9699293231e4394eb724ff571e54895191e9','targets':(0x7BBE40,0x7BBE44,0x7BBE48),'sizes':(4,4,242),'text':('a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4','64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb','1fca3fc2795831cc29f189b084374a8d1f8b1a95b71b27f244754f81e36cd07e')},
}
ROUTES['apple-clang'].update(component='7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6',targets=(0x4D10FC,0x4D10F8,0x46CDE8),text=('a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4','64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb','785201c0872f87ae2ca7eb36ff75ba375162b985eb83e67d1d0321349272fc2d'))
ROUTES['linux-clang'].update(path=ROOT/'build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin',component='dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6')
class AuditError(RuntimeError):pass
def sha(b):return hashlib.sha256(b).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pairs(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError(f'unterminated string at {a:#x}')
 return b[o:e].decode('ascii')
def bw(b,a):
 o=a-BASE;f,s=struct.unpack_from('<HH',b,o)
 if f&0xF800!=0xF000 or s&0xD000!=0x9000:return None
 sign=(f>>10)&1;j1=(s>>13)&1;j2=(s>>11)&1;i1=(~(j1^sign))&1;i2=(~(j2^sign))&1
 imm=(sign<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if imm&(1<<24):imm-=1<<25
 return a+4+imm
def validate_production():
 for path,pin,label in ((SOURCE,SOURCE_PIN,'source'),(HEADER,HEADER_PIN,'header')):
  raw=path.read_bytes()
  if (len(raw),sha(raw))!=pin:raise AuditError(f'gray-screen production {label} changed')
 cfg=json.loads(CONFIG.read_text());leaves={x.get('function'):x for x in cfg['relocated_leaves'] if x.get('function') in NAMES}
 if set(leaves)!=set(NAMES):raise AuditError('gray-screen production leaf inventory changed')
 for index,name in enumerate(NAMES):
  leaf=leaves[name];relocs=leaf.get('relocations',[]);linux=leaf.get('toolchain_profiles',{}).get('linux-clang',{});linux_relocs=linux.get('relocations',[])
  expected_count=(0,0,18)[index];expected_targets=() if index<2 else PROVIDER_TARGETS
  if leaf.get('profiles')!=['apple-clang','linux-clang'] or leaf.get('strict_relocation_contract') is not True or leaf.get('source',{}).get('sha256')!=SOURCE_PIN[1] or len(relocs)!=expected_count or tuple(x.get('target_address') for x in relocs)!=expected_targets:raise AuditError(f'gray-screen production pins changed: {name}')
  if linux.get('reviewed_version_prefix')!='Homebrew clang version 22.1.8' or len(linux_relocs)!=expected_count or tuple(x.get('target_address') for x in linux_relocs)!=expected_targets:raise AuditError(f'gray-screen Linux pins changed: {name}')
 patches={x.get('name'):x for x in cfg['patch_sites'] if x.get('name') in PATCHES}
 if set(patches)!=set(PATCHES):raise AuditError('gray-screen production patch inventory changed')
 for name,function,bounds in zip(PATCHES,NAMES,F):
  patch=patches[name]
  if patch.get('runtime_address')!=bounds[0] or patch.get('expected_size')!=bounds[1]-bounds[0] or patch.get('target_function')!=function or patch.get('profiles')!=['apple-clang','linux-clang']:raise AuditError(f'gray-screen production patch changed: {name}')
 report=json.loads(REPORT.read_text());built={x.get('extraction',{}).get('function'):x for x in report['relocated_leaves'] if x.get('extraction',{}).get('function') in NAMES}
 if set(built)!=set(NAMES):raise AuditError('gray-screen built leaf inventory changed')
 manifest=json.loads(MANIFEST.read_text())['component_overrides']['apollo_main']
 for start,_end in F:
  off=start-BASE;owners=[x for x in manifest['regions'] if x.get('file_offset',-1)<=off<x.get('file_offset',-1)+x.get('size',0)]
  if len(owners)!=1 or owners[0].get('address_status') not in {'generated_source_entry_replacement','generated_source_data_replacement'}:raise AuditError('gray-screen manifest entry ownership changed')
 for profile,route in ROUTES.items():
  component=route['path'].read_bytes()
  if len(component)!=3956672 or sha(component)!=route['component']:raise AuditError(f'{profile} gray-screen component changed')
  for bounds,target,size,digest in zip(F,route['targets'],route['sizes'],route['text']):
   replacement=sl(component,bounds[0],bounds[1])
   if apollo_overlay.decode_thumb_branch(bounds[0],replacement[:4],link=False)!=target or replacement[4:]!=b'\x00\xbf'*((len(replacement)-4)//2):raise AuditError(f'{profile} gray-screen redirect changed')
   if sha(sl(component,target,target+size))!=digest:raise AuditError(f'{profile} gray-screen compiled text changed')
 validate_apollo_main_artifacts(ROOT,AuditError,'production gray screen')
 return {'candidate':str(SOURCE.relative_to(ROOT)),'header':str(HEADER.relative_to(ROOT)),'production_routed':True,'ownership_bytes':340,'source_inventory_available':True,'source_functions':3,'compiled_text_bytes':{'apple-clang':250,'linux-clang':250},'alignment_bytes':{'apple-clang':2,'linux-clang':2},'strict_relocations':18,'stock_body_bytes_displaced':340,'retained_stock_noncode_bytes':32,'profiles_verified':['apple-clang','linux-clang'],'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_evidence_required':['authorized G2 panel trace confirming a black 640x480 root and eight 72x288 bands at x=0,72,144,216,288,360,432,504 with gray values 17,34,68,136,136,68,34,17'],'hardware_operations':[]}
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 starts=set();inside=set();iv=[];bodies=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);x=sl(b,a,z)
  if len(x)!=int(r['stock_bytes']) or sha(x)!=r['stock_sha256']:raise AuditError('body changed')
  starts.add(a);inside.update(range(a+2,z,2));iv.append((a,z));bodies.append(x)
 if len(rows)!=3 or sum(map(len,bodies))!=340 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('inventory changed')
 if sha(sl(b,*PHYS))!=PHYS_SHA or sha(sl(b,*POOL))!=POOL_SHA or sha(sl(b,*NEXT))!=NEXT_SHA or sha(sl(b,*DESC))!=DESC_SHA:raise AuditError('object boundary changed')
 if sha(sl(b,0x78DF8C,0x78DF94))!='a0462039e29b56a35c37da645dc89b97093fae1de6d7f1fccca7831847d1138f':raise AuditError('gray table changed')
 if list(sl(b,0x78DF8C,0x78DF94))!=[1,2,4,8,8,4,2,1]:raise AuditError('gray factors changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError(f'word changed at {a:#x}')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 needle=struct.pack('<I',PATH);hits=[];q=b.find(needle)
 while q>=0:hits.append(BASE+q);q=b.find(needle,q+1)
 if hits!=[0x5CF790]:raise AuditError('path pointer topology changed')
 import recover_apollo_embedded_source_paths as d
 entry=[];inter=[];entry_bw=[];inter_bw=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
  t=bw(b,a)
  if t in starts:entry_bw.append((a,t))
  elif t in inside:inter_bw.append((a,t))
 if entry or inter or entry_bw or inter_bw:raise AuditError('direct ingress changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=23 or pairs(calls)!=CALL_SHA:raise AuditError('callee closure changed')
 encoded=starts|inside|{v|1 for v in starts|inside};raw=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if v in encoded:raw.append((BASE+o,v))
 if raw!=STORED or pairs(raw)!=STORED_SHA:raise AuditError('stored ingress changed')
 return {'surface':{'linked_functions':3,'body_bytes':340,'literal_pool_bytes':32,'physical_bytes':372,'descriptor_bytes':16,'direct_bl_entry_sites':0,'direct_body_calls':23,'stored_entry_pointers':3,'strict_interior_ingress':0},'registration':{'screen_id':'0x0000010f','data_handler':'0x005cf635','screen_event_handler':'0x005cf67f','predicate':'0x005cf67b','state_address':'0x20003080'},'behavior':{'data_handler_returns_zero':True,'predicate_returns_one':True,'construct_event':2,'recognized_noop_event':3,'root_dimensions':[640,480],'band_count':8,'band_dimensions':[72,288],'x_positions':[0,72,144,216,288,360,432,504],'gray_factors':[1,2,4,8,8,4,2,1],'gray_values':[17,34,68,136,136,68,34,17],'root_global':'0x20074880','registry_root_field':'0x20003084'},'boundary':{'next_object':'ProductionTest/production_test.c','next_handler':'0x005cf7a8','next_descriptor':'0x006a45e0'},'production':validate_production()}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 gray-screen audit: PASS')
