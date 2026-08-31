#!/usr/bin/env python3
"""Fail-closed audit of the six-function G2 NVDB product-mode helper."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';FM=ROOT/'tools/manifests/g2-nvdb-product-mode-function-map.tsv'
FM_SHA='94ce69c8a34c354cb380b29dbbbb5edc7a226be249378f6d5ea56e25c2634986'
PHYS=(0x4ABD90,0x4ABEC8);PHYS_SHA='ff1ab9f69ab28b170f754280b7afa0073010217748706b238c21b3cc717addb4';BODY_SHA='1bfe7d97d0352877f2563deaee8402758c6d79f816a9de19916bad5c46918584';DATA_SHA='41f66af2dd97ea8482ff3702a0414d97fd698b225f82a516c0bd186fea9ac2f4'
ENTRY_COUNT=54;ENTRY_SHA='8b85c8a4f26cf599c427ede08e8f91e9c1f0d30d7079483cb474f73dc86a3b2a';OUT_COUNT=18;OUT_SHA='5713c9580d9c0c8796dec2cfbe365121e569e7b9ff9772ab47224609ff7af1ab'
STORED=[(0x6D1E94,0x4ABD91),(0x78F520,0x4ABDA5)]
WORDS={0x4ABEA0:0x200038F0,0x4ABEA4:0x74E09C,0x4ABEA8:0x783460,0x4ABEAC:0x6E18DC,0x4ABEB0:0x788C10,0x4ABEB8:0x78C008,0x4ABEC0:0x783474}
STRINGS={0x783460:'_nvdbUpdataProdMd',0x6E18DC:r'D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_product_mode.c',0x788C10:'nv.productMode',0x78C008:'nvProdMode',0x783474:'set_product_mode'}
class AuditError(RuntimeError):pass
def sha(b):return hashlib.sha256(b).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pairs(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def decoder():
 sys.path.insert(0,str(ROOT/'tools'));p=ROOT/'tools/recover_apollo_embedded_source_paths.py';s=importlib.util.spec_from_file_location('pmdec',p);m=importlib.util.module_from_spec(s);sys.modules['pmdec']=m;s.loader.exec_module(m);return m
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 if sha(FM.read_bytes())!=FM_SHA:raise AuditError('function map changed')
 with FM.open(newline='') as handle:rows=list(csv.DictReader(handle,delimiter='\t'))
 starts={};inside=set();bodies=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);x=sl(b,a,z)
  if len(x)!=int(r['stock_bytes']) or sha(x)!=r['stock_sha256']:raise AuditError('body changed')
  starts[a]=r['function'];inside.update(range(a+2,z,2));bodies.append(x)
 if len(rows)!=6 or sum(map(len,bodies))!=270 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('inventory changed')
 if sha(sl(b,*PHYS))!=PHYS_SHA or sha(sl(b,0x4ABE9E,0x4ABEC8))!=DATA_SHA:raise AuditError('physical object changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError('literal changed')
 for a,v in STRINGS.items():
  o=a-BASE;e=b.find(b'\0',o)
  if b[o:e].decode()!=v:raise AuditError('string changed')
 d=decoder();entry=[];inter=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  if t in inside:inter.append((a,t))
 if len(entry)!=ENTRY_COUNT or pairs(entry)!=ENTRY_SHA or inter:raise AuditError('ingress changed')
 out=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0)
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:out.append((q,t))
 if len(out)!=OUT_COUNT or pairs(out)!=OUT_SHA:raise AuditError('callee closure changed')
 stored=[]
 for a in starts:
  n=struct.pack('<I',a|1);p=b.find(n)
  while p>=0:stored.append((BASE+p,a|1));p=b.find(n,p+1)
 if sorted(stored)!=STORED:raise AuditError('stored roots changed')
 for a in inside:
  for v in (a,a|1):
   if b.find(struct.pack('<I',v))>=0:raise AuditError('interior pointer appeared')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 candidate='components/apollo_main/core_overlay/nvdb_product_mode.c'
 expected_patches={
  'replace_nvdb_product_mode_default_crc_initialize':(0x004ABD90,20,'80c08774a0852a8bedd18ee767b2e92898b50212b321c2e4f4de71f0478fc781','open_cfw_nvdb_product_mode_default_crc_initialize'),
  'replace_nvdb_product_mode_load_and_migrate':(0x004ABDA4,112,'23aa7a2a4434ae72b8badcf613bb9c3b1fd600474c4576ef03a32f604d089664','open_cfw_nvdb_product_mode_load_and_migrate'),
  'replace_nvdb_product_mode_set':(0x004ABE14,76,'a46abcbe853a0a2bc1d57aac68a2208a8826dbb41b65d3be4fe6a080ddc60cec','open_cfw_nvdb_product_mode_set'),
  'replace_nvdb_product_mode_get':(0x004ABE60,6,'a34d3198ce3cb5e9f90231d706ea91fd58e8530a91d433dbdf1d173702dc74f2','open_cfw_nvdb_product_mode_get'),
  'replace_nvdb_product_mode_update':(0x004ABE66,38,'204a4bd3e1dcdbbd9915ebab59b8d960727fce16f8360180de051accab1d14a7','open_cfw_nvdb_product_mode_update'),
  'replace_nvdb_product_mode_read':(0x004ABE8C,18,'9fe24dc73d40265ac55a643d80fdeb921bcc4a9c651985306822b0cf58ea0cc9','open_cfw_nvdb_product_mode_read'),
 }
 patches={r['name']:r for r in overlay['patch_sites'] if r.get('name') in expected_patches}
 leaves={r['function']:r for r in overlay['relocated_leaves'] if r.get('source',{}).get('path')==candidate}
 if (set(patches)!=set(expected_patches)
  or any(patches[n]['runtime_address']!=a or patches[n]['expected_size']!=z or patches[n]['expected_sha256']!=d or patches[n]['branch']!='b_w' or patches[n]['target_function']!=t or patches[n].get('profiles')!=['apple-clang'] for n,(a,z,d,t) in expected_patches.items())
  or set(leaves)!={t for *_,t in expected_patches.values()}
  or any(l['source']['sha256']!='f02df8296dce95390a54141341cc546668361f3b8acc28b28746976952ecf05e' or l.get('profiles')!=['apple-clang'] for l in leaves.values())):raise AuditError('production product-mode routing changed')
 return {'surface':{'linked_functions':6,'body_bytes':270,'physical_bytes':312,'direct_bl_ingress_sites':54,'direct_provider_calls':18,'stored_entry_pointers':STORED,'strict_interior_ingress':0},'record':{'address':0x200038F0,'boot_hex':'01000000','initialized_crc16':0x2E3E,'key':'nvProdMode'},'behavior':{'missing_rewrites_defaults':True,'pre_v1_crc_mismatch_rewrites_defaults':True,'v1_crc_mismatch_rewrites_defaults':False,'read_imports_record_without_validation':True},'production':{'candidate':candidate,'production_routed':True,'ownership_bytes':270,'retained_stock_noncode_bytes':42,'toolchain_profiles':['apple-clang'],'relocated_leaves':sorted(leaves),'patch_sites':sorted(patches)}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
