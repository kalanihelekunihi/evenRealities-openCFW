#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for menu/menu_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-menu-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-menu-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-menu-page-closure.tsv'
PINS={FM:'a52bfb413c85bc7e8d1c6b6ec262487f511b1f43cefc1a99585180dd7a1703b2',PM:'00e827e8b7abaac2828b26ea005d5fae33becf6bdba48461a1cbfef39a35d020',CL:'58cde8026bfd034f508ab549a261a6c9b281578d7604ae0991af39b2023cd49b'}
PHYS=(0x0046018E,0x00463C68);PATH=0x0070CA64;PATH_CELLS=(0x00460628,0x004611BC,0x00461E8C,0x00462898,0x004631B8,0x00463BBC)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4495E4,0x4497B6,0x44981C};RUNTIME={0x439BE4,0x439C04,0x43C0E4,0x44A43C,0x46CACC};NANOPB={0x48EB32,0x48F49C,0x490120,0x4905F4,0x490C32}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43FCE0,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x4413CE,0x44140E,0x44143E,0x44146A,0x441478,0x441488,0x44DCE2,0x44E368,0x44E3CA,0x44E498,0x44E4AA,0x44EA04,0x4503D6,0x450408,0x450500,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
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
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cmsis=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());nanopb=json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cmsis['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or nanopb['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824' or '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise common.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 funcs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(funcs)!=34 or sum(r['path_anchored']=='yes' for r in rows)!=14 or sum(r['ghidra_discovered']=='yes' for r in rows)!=25:raise common.AuditError('function inventory changed')
 starts={a for a,_ in funcs};ins={};calls=[];dynamic=[];body=b'';uncovered=[]
 for a,z in funcs:
  ii,cc,dd=cfg._recover_function(b,a,z)
  if set(ins)&set(ii):raise common.AuditError('instruction overlap')
  ins.update(ii);calls+=cc;dynamic+=dd;body+=common._slice(b,a,z);uncovered+=common._uncovered((a,z),ii)
 calls.sort();expected_gaps=[(0x00461B10,0x00461B14),(0x00461B6E,0x00461B74),(0x00461E8A,0x00461E94),(0x00461FB8,0x00461FBC),(0x0046236C,0x00462384),(0x00462442,0x00462454),(0x004624EA,0x004624F4)]
 if uncovered!=expected_gaps or len(body)!=13906 or sh(body)!='65e94f585ed00b9e798915a1f84fb1e6606f6551d3543863770815a0b6f0f74f' or len(ins)!=5013 or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='f646c22ac59cf3d7a136734da61e11988864ec6919fd2fdcb1b0cf0e6fc1af1e' or dynamic:raise common.AuditError('body closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),common._slice(b,*PHYS)) if a not in covered)
 if len(outer)!=1236 or sh(outer)!='558b7eebbef7b5da8cb6208bb2fad82f4a4d0db4294380a518401de99b73eee5' or sh(common._slice(b,*PHYS))!='7334866b0e145011ddf7c463557cfab5f9bd946eddc28b2a3154b76265295248':raise common.AuditError('physical closure changed')
 if sh(common._slice(b,PHYS[0]-16,PHYS[0]))!='9fae63d25a20977a3cf33928d4bffac7d6ab916db77bea61bb338c33297c839a' or sh(common._slice(b,PHYS[1],PHYS[1]+16))!='43340b4a2556981a79c40310ccf2ac6c99ea23afee18865e998275048367285c':raise common.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-CMSIS-RUNTIME-NANOPB
 if len(calls)!=830 or sum(t in starts for _,t in calls)!=84 or common._pair_digest(calls)!='3908798176fb62295e255cb3ed9896d22ca7de4638f7fd70bcf0ed4e9f8f3890' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,CMSIS,RUNTIME,NANOPB,first))!=(124,445,3,24,15,135) or len(first)!=22:raise common.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];noncode=[];wide=[];wide_strict=[];wide_noncode=[]
 for a in range(common.BASE,common.BASE+len(b)-3,2):
  t=thumb._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:noncode.append((a,t))
  x,y=struct.unpack('<HH',common._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:wide_strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:wide_noncode.append((a,t))
 if len(entries)!=98 or common._pair_digest(entries)!='6111fa3057caaaf24ba030e66774c4b04bd1f7d85f0e4b5761b6456321da7b6b' or strict or noncode or wide or len(wide_strict)!=5 or common._pair_digest(wide_strict)!='3fcb4f0017d39e15d02c71fb72503897af9e2da2c6933418a225f989100450ae' or wide_noncode:raise common.AuditError('branch classification changed')
 raw=[];stored=[];stored_interior=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((common.BASE+off,v,t))
   if (common.BASE+off)%4==0 and v&1:(stored if t in starts else stored_interior).append((common.BASE+off,v))
 if len(raw)!=65 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='6c8959067a8a78061801cd52d45eb90526e4b6b888d8cb951d45da2eafaef757' or len(stored)!=8 or common._pair_digest(stored)!='3ed23c610eb90ab101913ee9a226f54d3f6294cb0c0bd4bb8a2abb0203b91ea7' or len(stored_interior)!=1 or common._pair_digest(stored_interior)!='97330cdd4c51399cbd0df0de21cdd540acdd95c7d49a436a6da9627db49cbc35':raise common.AuditError('stored-entry closure changed')
 if cstring(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c':raise common.AuditError('path changed')
 refs=sorted((cell,a) for cell in PATH_CELLS for a in thumb.literal_references(b,cell))
 if len(refs)!=89 or common._pair_digest(refs)!='f480d2200ac02f72045a54ec812f02b3642696c30705e101009b838244b70b35':raise common.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any(Path(x.get('path','')).name.lower()=='menu_page.c' for x in overlay['sources'])
 if routed:raise common.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':common.IMAGE_SHA256,'retained_path':r'app\gui\menu\menu_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':34,'ghidra_discovered_functions':25,'path_anchored_functions':14,'restored_non_anchor_functions':9,'body_bytes':13906,'physical_bytes':15066,'outer_pool_bytes':1236,'reachable_instructions':5013,'direct_body_calls':830,'internal_direct_body_calls':84,'external_direct_body_calls':746,'indirect_body_calls':0,'direct_bl_entry_sites':98,'stored_function_start_pointers':8,'stored_interior_entry_pointers':1,'classified_wide_interior_branches':5},'provider_boundary':{'lvgl_calls':124,'easylogger_calls':445,'cmsis_freertos_calls':3,'runtime_calls':24,'nanopb_calls':15,'first_party_calls':135,'lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','nanopb_commit':'98bf4db69897b53434f3d0ba72e0a3ab1a902824','historical_menu_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
