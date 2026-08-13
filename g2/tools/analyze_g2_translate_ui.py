#!/usr/bin/env python3
"""Fail-closed stock/provider audit for translate_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-translate-ui-function-map.tsv';PM=ROOT/'tools/manifests/g2-translate-ui-provider-map.tsv';CL=ROOT/'tools/manifests/g2-translate-ui-closure.tsv'
PINS={FM:'4e027aa0a336ca9823ed1a0d0d4c9b95ac012fcb8b2a976ef9bd326437387a20',PM:'1236112701dd8c5262d2dacf43ad35c2a221134569b5372fcd1448ca3fd3bdfb',CL:'252f6dc0a86f2f686697e1f2b3019c9dd1167cfd1d6b14b67ab34c799828a258'}
PHYS=(0x59D380,0x59E9E2);PATH=0x6FE6FC;CELLS=(0x59DEF8,0x59E63C)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x4490CC}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F4C0,0x43F66C,0x43F6B8,0x43F6D6,0x43FDDA,0x44104C,0x4411AA,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x4413BE,0x4413CE,0x44140E,0x44143E,0x44144C,0x44145A,0x44146A,0x441488,0x44D7B8,0x44D878,0x44DCE2,0x44E368,0x44EA04,0x4503D6,0x450408,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
FIRST={0x45A568,0x45FFFE,0x460084,0x46AE9C,0x47D8CE,0x58BFB2,0x58C238,0x58C426,0x58C7A0,0x58C836,0x58C84E,0x59E9E2,0x59EA10,0x59EA14,0x59EC28,0x59F71A,0x59F960}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;return b[o:b.index(0,o)].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();body=b'';ins=[];calls=[];ind=[]
 if len(F)!=29 or sum(r['source_path_anchor']=='yes' for r in rows)!=7 or sum(r['stored_entry']=='yes' for r in rows)!=11:raise c.AuditError('inventory changed')
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii=list(md.disasm(raw,a))
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256'] or sum(x.size for x in ii)!=len(raw):raise c.AuditError('function body changed')
  body+=raw;ins += [(x.address,x.size) for x in ii];inter.update(range(a+2,z,2))
  for x in ii:
   y=t._thumb_bl_target(b,x.address)
   if y is not None:calls.append((x.address,y))
   elif x.mnemonic=='blx':ind.append((x.address,x.op_str))
 if len(body)!=5288 or sh(body)!='7d0f91828d1e2b73aafa10731d4d02f88a224e6d481057e1f1013cf44ad1d3e1' or len(ins)!=1942 or c._instruction_digest(ins)!='c23628ebd38cc205ccf33878d530580018be776979e19797adc49b96a01792fe':raise c.AuditError('instruction closure changed')
 if calls!=sorted(calls) or len(calls)!=367 or sum(y in starts for x,y in calls)!=21 or c._pair_digest(calls)!='6f97c59a5b8b91edd5f3b541cd292273adf9ec8c4f15334b31767b03bbd9b9dc' or ind!=[(0x59DD54,'r2')]:raise c.AuditError('call closure changed')
 non=b'';pos=PHYS[0]
 for a,z in F:non+=c._slice(b,pos,a);pos=z
 non+=c._slice(b,pos,PHYS[1])
 if len(non)!=442 or sh(non)!='b625bc336dd401344d495723fdb3e0f6cabedd61f5892f9fb7677aa41a1e6c16' or sh(c._slice(b,*PHYS))!='257d8e695b5f3465028acc823ab71789c3182dc072588afd14cb8cbc7ea7812f':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='35a9994cbc16789a1ca463faa7d55363e7a82f4fa74c178f02b57ec5989df599' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='31621181b850031802e0765b02528a720ca7086a56c583f36733a9dcde3ae324':raise c.AuditError('boundary changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_ui.c' or tuple(struct.unpack('<I',c._slice(b,x,x+4))[0] for x in CELLS)!=(PATH,PATH):raise c.AuditError('retained path changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,CMSIS,FIRST)
 if set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(175,125,10,2,34):raise c.AuditError('provider closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=41 or c._pair_digest(entries)!='1ca5f294fc08e74679e6f84888d69a770ab38b48839a1265b939db2235ab1e4f' or strict:raise c.AuditError('direct ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc]
 if len(stored)!=13 or c._pair_digest(stored)!='52a601bc7c5dbeb61650b3d5fd922cd6ac24457fad2299912374efaac694006e':raise c.AuditError('stored ingress changed')
 for p,k in ((ROOT/'third_party/easylogger/PROVENANCE.json','a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24'),(ROOT/'third_party/lvgl/PROVENANCE.json','344c7c318047b7348e1be8572a9fd4260c251cfa')):
  d=json.loads(p.read_text());
  if d['upstream']['selected_commit']!=k:raise c.AuditError('provider provenance changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('translate_ui.c' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\translate\translate_ui.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':29,'ghidra_discovered_functions':7,'restored_functions':22,'path_anchored_functions':7,'body_bytes':5288,'physical_bytes':5730,'noncode_bytes':442,'reachable_instructions':1942,'direct_body_calls':367,'internal_direct_body_calls':21,'external_direct_body_calls':346,'indirect_body_calls':1,'direct_bl_entry_sites':41,'stored_entry_pointers':13,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':175,'lvgl_calls':125,'iar_dlib_calls':10,'cmsis_freertos_calls':2,'first_party_calls':34,'bounded_first_party_indirect_calls':1,'easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','historical_translate_ui_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
