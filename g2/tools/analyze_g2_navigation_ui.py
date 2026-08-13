#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for navigation/navigation_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-navigation-ui-function-map.tsv';PM=ROOT/'tools/manifests/g2-navigation-ui-provider-map.tsv';CL=ROOT/'tools/manifests/g2-navigation-ui-closure.tsv'
PINS={FM:'05b67e7284131e3e64585bda98d16e746a6d42b20d9ebfbec69b69c7795d9004',PM:'720aeb89fa429112676b128649fc7edd7ebe835829306bc90f2faa11d87b68f0',CL:'658b479f039184cdc6a12cbe4f450901662e2ce18b6028b34468cbce278af7ab'}
PHYS=(0x00545588,0x0054EE18);PATH=0x006FB6E4
PATH_CELLS=(0x00545CC4,0x005467EC,0x0054778C,0x0054800C,0x00548B4C,0x005496EC,0x00549BC4,0x0054A920,0x0054B218,0x0054BF04,0x0054C5A8,0x0054CF54,0x0054D988,0x0054E444,0x0054ED78)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4497B6,0x44981C};RUNTIME={0x439BE4,0x439C04,0x43C0E4,0x44A43C,0x44B5A0,0x44B728};NANOPB={0x48EB32};MPALAND={0x4B4728}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6AC,0x43F6B8,0x43F6D6,0x43FCE0,0x43FD9E,0x440656,0x4409FA,0x44104C,0x441068,0x441094,0x4410A6,0x441180,0x4411F2,0x441200,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x4413CE,0x44140E,0x44142E,0x44143E,0x44145A,0x44146A,0x441488,0x44BDEA,0x44D878,0x44DCE2,0x44E368,0x44E3CA,0x44E498,0x44E4AA,0x44EA04,0x4503D6,0x450408,0x450500,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
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
 if len(funcs)!=61 or sum(r['path_anchored']=='yes' for r in rows)!=16 or sum(r['ghidra_discovered']=='yes' for r in rows)!=32:raise common.AuditError('function inventory changed')
 starts={a for a,_ in funcs};ins={};calls=[];dynamic=[];body=b'';uncovered=[]
 for a,z in funcs:
  ii,cc,dd=cfg._recover_function(b,a,z)
  if set(ins)&set(ii):raise common.AuditError('instruction overlap')
  ins.update(ii);calls+=cc;dynamic+=dd;body+=common._slice(b,a,z);uncovered+=common._uncovered((a,z),ii)
 calls.sort();expected_gaps=[(0x00546D96,0x00546DA0),(0x0054A918,0x0054A944),(0x0054AA94,0x0054AAA0),(0x0054AB28,0x0054AB4C),(0x0054AC50,0x0054AC74),(0x0054AD4C,0x0054AD78),(0x0054B0CA,0x0054B0D8),(0x0054B1C4,0x0054B220),(0x0054B802,0x0054B81C),(0x0054B9EC,0x0054B9F8),(0x0054BA4C,0x0054BAAC),(0x0054BE66,0x0054BE7C),(0x0054BEFC,0x0054BF40),(0x0054D3B6,0x0054D3BC),(0x0054EC1E,0x0054EC2C)]
 if uncovered!=expected_gaps or len(body)!=36612 or sh(body)!='e334509f9691b6b3181e9b59b84345e3af9294f66b03b0770d1a21472f2d00ac' or len(ins)!=12665 or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='942ab224519a1c5c86bd20ad36a9d46a211c16bb833875c2ff30809d22284a05' or dynamic:raise common.AuditError('body closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),common._slice(b,*PHYS)) if a not in covered)
 if len(outer)!=2976 or sh(outer)!='211f1e288dc962ea97abd651a0d64a5ac76c4589bc176f4e121cf398a0a25c3d' or sh(common._slice(b,*PHYS))!='914d0d69ddd805dd54cb6309d0aed84c7890aee7a8d4c1aeca4cbcc7d1e53460':raise common.AuditError('physical closure changed')
 if sh(common._slice(b,PHYS[0]-16,PHYS[0]))!='5bf09ef017dc9706942d3387fe9c830e6f98cf1b68012d29bfd40820d96f06a8' or sh(common._slice(b,PHYS[1],PHYS[1]+16))!='5fb96866f2206e82fe778e6e9061db80f1de8db6561db4193efa3288a40f0238':raise common.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-CMSIS-RUNTIME-NANOPB-MPALAND
 if len(calls)!=2376 or sum(t in starts for _,t in calls)!=139 or common._pair_digest(calls)!='d85ffbc7173325b6e12f6e6097208e0d27253cea8826cdbdd349d4e0fad6b498' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,CMSIS,RUNTIME,NANOPB,MPALAND,first))!=(702,1245,20,67,22,2,179) or len(first)!=53:raise common.AuditError('provider closure changed')
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
 expected_noncode=[(0x005456E0,0x0054681E),(0x005549AA,0x0054AFBA)]
 if len(entries)!=152 or common._pair_digest(entries)!='43a77581ab026bfb7e0d4caddd15f81a5bbb703e38156dd08f92b8c49d420ff5' or strict or noncode!=expected_noncode or wide or len(wide_strict)!=19 or common._pair_digest(wide_strict)!='447737232e957fa81deac93a56e1c7bc3a691436c1ed717035d722738c0d4b47' or wide_noncode:raise common.AuditError('branch classification changed')
 raw=[];stored=[];stored_interior=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((common.BASE+off,v,t))
   if (common.BASE+off)%4==0 and v&1:(stored if t in starts else stored_interior).append((common.BASE+off,v))
 if len(raw)!=57 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='cdae7fe191b8463d8117b1b30101c89c44e965aa00c1050a66f7c7c4408093ef' or len(stored)!=14 or common._pair_digest(stored)!='5443c41cfff8c4381bfe15679f1fffaa3faec1f584070a83ac6a660b07308e52' or len(stored_interior)!=5 or common._pair_digest(stored_interior)!='59d79b79e58855b7df5a3c9ed9700dc15f87b25c10d58baec4728d6056dd9f28':raise common.AuditError('stored-entry closure changed')
 if cstring(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c':raise common.AuditError('path changed')
 refs=sorted((cell,a) for cell in PATH_CELLS for a in thumb.literal_references(b,cell))
 if len(refs)!=249 or common._pair_digest(refs)!='dbfde2cefd1f660d741ee23d5682733e7957bfc366dec3a5443a624022da2b7b':raise common.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('navigation_ui' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise common.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':common.IMAGE_SHA256,'retained_path':r'app\gui\navigation\navigation_ui.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':61,'ghidra_discovered_functions':32,'path_anchored_functions':16,'restored_non_anchor_functions':29,'body_bytes':36612,'physical_bytes':39056,'outer_pool_bytes':2976,'reachable_instructions':12665,'direct_body_calls':2376,'internal_direct_body_calls':139,'external_direct_body_calls':2237,'indirect_body_calls':0,'direct_bl_entry_sites':152,'stored_function_start_pointers':14,'stored_interior_entry_pointers':5,'classified_noncode_pseudo_bl_sites':2,'classified_wide_interior_branches':19},'provider_boundary':{'lvgl_calls':702,'easylogger_calls':1245,'cmsis_freertos_calls':20,'runtime_calls':67,'nanopb_calls':22,'mpaland_printf_calls':2,'first_party_calls':179,'lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','nanopb_commit':'98bf4db69897b53434f3d0ba72e0a3ab1a902824','mpaland_printf_commit':'d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e','historical_navigation_ui_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
