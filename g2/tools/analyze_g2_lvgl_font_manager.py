#!/usr/bin/env python3
"""Fail-closed object/provider audit for lvgl_font_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-lvgl-font-manager-function-map.tsv";CL=ROOT/"tools/manifests/g2-lvgl-font-manager-closure.tsv";PM=ROOT/"tools/manifests/g2-lvgl-font-manager-provider-map.tsv"
PINS={FM:"84321bac79894c7bbe7d59bfdaf05196b9dfe46f0427082b8b43468524cd5f31",CL:"7b46d6404f9998cfdfdf706400da34f8f231f3c4bd133d9a4ee895dc3a82659e",PM:"f46bf7bb0ada18b9554b458ce59fea273ab9da147e9fd744c97ffb0d987b9754"}
PHYS=(0x46CAE0,0x46D67C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};MSPI={0x46F65E,0x46F674};HEAP={0x474CD2,0x474D16};FT={0x4B1C9C,0x4B1EF6}
PATH_CELLS={0x46D57C:[0x46CAFE,0x46CB44,0x46CB92,0x46CBE0,0x46CC32,0x46CC94,0x46CD06,0x46CD4A,0x46CE1C,0x46CF14,0x46CF72,0x46CFE4,0x46D048,0x46D092,0x46D0DA,0x46D126,0x46D18C,0x46D206],0x46D620:[0x46D2D8,0x46D366,0x46D3B4,0x46D410,0x46D49C,0x46D4FA,0x46D546]}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());ft=json.loads((ROOT/"third_party/freetype/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if ft["upstream"]["peeled_commit"]!="86bc8a95056c97a810986434a3f268cbe67f2902" or ft["upstream"]["declared_library_version"]!="2.9.1":raise c.AuditError("FreeType changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if "deff9ab509341f264addbd3c8ada533678591905" not in (ROOT/"third_party/tlsf/README.openCFW.md").read_text():raise c.AuditError("TLSF changed")
 iar=(ROOT/"docs/research/iar-dlib-runtime-census.md").read_text()
 if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:raise c.AuditError("IAR changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=8 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if uncovered or len(body)!=2590 or sh(body)!="f92e57b0ab1bda61b008095d44a8136d19f7f784d49a6497d8cad4b092c1c3e2" or len(ins)!=973 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="59c7c85e6d5172a6cb944f154575c5a624b91b4b32e0b2e377bace1912a8a950" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=382 or sh(non)!="29e7e2c153aefaa2aa5fc6fae57be48090c77c30da0a5325b78891e5dc5c22e9" or sh(c._slice(b,*PHYS))!="49b22952decc2e1a561f87928b8d59ea68fd21ac70de46225a2aee2f6be3b3a3":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x46CAD0,PHYS[0]))!="d8afb8ea7c29be018860a02f0b7187e1eb9af1a9f99b7debdb6518dfd229093b" or sh(c._slice(b,PHYS[1],0x46D68C))!="8786401041671ede00770cae6ad04d69824555fb3bd9dec1cb22686be7617ee9":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,MSPI,HEAP,FT)
 if len(calls)!=149 or sum(y in starts for x,y in calls)!=9 or c._pair_digest(calls)!="7e6275d8832f2d33facf78cde5c5e7b90056af228ab9123efb576e7efdaab5de" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(125,2,2,9,2):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=12 or c._pair_digest(entries)!="c72c61f3b3124d72cc796f1726f07f05fe2a2edcb6c244b4451d322647ad3145" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[struct.unpack_from('<I',b,o)[0] for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored:raise c.AuditError("stored callbacks changed")
 if cstring(b,0x6FB45C)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\common\lvgl_font_manager.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("lvgl_font_manager" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\common\lvgl_font_manager.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":8,"path_anchored_functions":7,"body_bytes":2590,"physical_bytes":2972,"noncode_bytes":382,"reachable_instructions":973,"direct_body_calls":149,"internal_direct_body_calls":9,"external_direct_body_calls":140,"indirect_body_calls":0,"direct_bl_entry_sites":12,"stored_entry_pointers":0,"strict_interior_ingress":0},"behavior":{"four_entry_font_chains":True,"external_xip_font_headers":True,"font_create_delete_lifecycle":True,"mspi_serialized_registration":True,"background_and_foreground_roles":True},"provider_boundary":{"easylogger_calls":125,"iar_dlib_calls":2,"g2_mspi_lock_calls":2,"source_owned_heap_wrapper_calls":9,"lvgl_freetype_adapter_calls":2,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","freetype_version":"2.9.1","freetype_commit":"86bc8a95056c97a810986434a3f268cbe67f2902","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
