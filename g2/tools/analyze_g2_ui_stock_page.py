#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for dashboard ui_stock_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ui-stock-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-ui-stock-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ui-stock-page-closure.tsv'
PINS={FM:'57042e0954fa20344339264f6339a0ef6053c7e14653148d7114594c6ca3b52d',PM:'17d593e886b71ae59d75162b777383cce84df22ddf924ad30e28fb70c0027155',CL:'772d300df2d4c360b99c073ea87c3f4818a006f0b42a26776604b1ff8878b04c'}
PHYS=(0x004E9DD4,0x004ED7D8);PATH=0x006F0E98;PATH_CELLS=(0x004EA7F4,0x004EB328,0x004EBDF8,0x004EC294,0x004ED04C,0x004ED728)
EASY={0x43CE9E,0x43D0CE,0x43D574};RUNTIME={0x439BE4,0x43C0E4,0x44B5A0,0x44B728}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F4C0,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x44130C,0x44131C,0x44140E,0x44143E,0x44145A,0x44146A,0x44D7B8,0x44D878,0x44DCE2,0x44DDEA,0x44E368,0x44E3CA,0x44E498,0x44E4BC,0x44EA04,0x4503D6,0x450408,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
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
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise common.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 funcs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(funcs)!=34 or sum(r['path_anchored']=='yes' for r in rows)!=19 or sum(r['ghidra_discovered']=='yes' for r in rows)!=32:raise common.AuditError('function inventory changed')
 starts={a for a,_ in funcs};ins={};calls=[];dynamic=[];body=b'';uncovered=[]
 for a,z in funcs:
  ii,cc,dd=cfg._recover_function(b,a,z)
  if set(ins)&set(ii):raise common.AuditError('instruction overlap')
  ins.update(ii);calls+=cc;dynamic+=dd;body+=common._slice(b,a,z);uncovered+=common._uncovered((a,z),ii)
 calls.sort();expected_gaps=[(0x004EA252,0x004EA258),(0x004ECD4A,0x004ECD54),(0x004ECDAA,0x004ECDB0)]
 if uncovered!=expected_gaps or len(body)!=13892 or sh(body)!='f30140f241650e0c6e42e1ae5133a33316b3c19311e44b6218413073423bbed8' or len(ins)!=5042 or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='20d516e609245b0f1919e35ed55fd1c01048f54f0c89d33f7c4084d3fe5f1d98' or dynamic:raise common.AuditError('body closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),common._slice(b,*PHYS)) if a not in covered)
 if len(outer)!=982 or sh(outer)!='f021b0808168b128ecc887364fb569edd4191c313e93fcf3efdddca6608e7155' or sh(common._slice(b,*PHYS))!='e5f15feedebba73a550ccffcaa586b079cb52362396b892d0ffa43fead1bd192':raise common.AuditError('physical closure changed')
 if sh(common._slice(b,PHYS[0]-16,PHYS[0]))!='1d1c6a0b474717393e1f7fe1d20aa948def00f421451c8892cfa0ed8abe3e962' or sh(common._slice(b,PHYS[1],PHYS[1]+16))!='1148d298c076231b89cb01dc22f152920efe5a1e3ac6f75e9bab8bc3a65bb7ec':raise common.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-RUNTIME
 if len(calls)!=958 or sum(t in starts for _,t in calls)!=106 or common._pair_digest(calls)!='910a80745bc2a548557c2687ed32b152b8b2380091a96df225da7d0b9b3d0012' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,RUNTIME,first))!=(454,355,10,33) or len(first)!=14:raise common.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];noncode=[];wide=[];wide_strict=[]
 for a in range(common.BASE,common.BASE+len(b)-3,2):
  t=thumb._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:noncode.append((a,t))
  x,y=struct.unpack('<HH',common._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:wide_strict.append((a,t))
 if len(entries)!=116 or common._pair_digest(entries)!='690f65bee09b27851614c033c29564216f27461c4ccea5b58339eb3c9794c13d' or strict or noncode or wide or wide_strict!=[(0x004EC344,0x004ECE42),(0x004EC3A6,0x004ECE42),(0x004EC40A,0x004ECE42)]:raise common.AuditError('branch classification changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((common.BASE+off,v,t))
   if t in starts and (common.BASE+off)%4==0 and v&1:stored.append((common.BASE+off,v))
 if len(raw)!=32 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='69221668cb4080c7521a5fe00a9fa82e6f49a1d1f1f9da60ce8fd47dcf5a1575' or len(stored)!=2 or common._pair_digest(stored)!='0315b664979dc96bfd8b72490a0b317ec42a55983ace491f848ee88340585c54':raise common.AuditError('stored-entry closure changed')
 if cstring(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_stock_page.c':raise common.AuditError('path changed')
 refs=sorted((cell,a) for cell in PATH_CELLS for a in thumb.literal_references(b,cell))
 if len(refs)!=71 or common._pair_digest(refs)!='d20248a8573de434f371e6c64a8ccda497ef3af6c56b648c1f803f9ef58c1bb6':raise common.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('ui_stock_page' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise common.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':common.IMAGE_SHA256,'retained_path':r'app\gui\dashboard\screens\ui_stock_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':34,'ghidra_discovered_functions':32,'path_anchored_functions':19,'restored_non_anchor_functions':2,'body_bytes':13892,'physical_bytes':14852,'outer_pool_bytes':982,'reachable_instructions':5042,'direct_body_calls':958,'internal_direct_body_calls':106,'external_direct_body_calls':852,'indirect_body_calls':0,'direct_bl_entry_sites':116,'stored_function_pointers':2,'classified_wide_interior_branches':3},'provider_boundary':{'lvgl_calls':454,'easylogger_calls':355,'cmsis_freertos_calls':0,'runtime_calls':10,'first_party_calls':33,'lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_stock_page_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
