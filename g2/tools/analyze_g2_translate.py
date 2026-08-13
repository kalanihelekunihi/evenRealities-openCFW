#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/translate/translate.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-translate-function-map.tsv';PM=ROOT/'tools/manifests/g2-translate-provider-map.tsv';CL=ROOT/'tools/manifests/g2-translate-closure.tsv'
PINS={FM:'accb812ef0d173a606f73a637274bed5246fe0c207f90c62d4f3e7d118d7fe88',PM:'2affe82c86986e5aa530b494919e82b9beb0c1c869262321b6260c5e4007a15d',CL:'740340687407ef4d6b00684d167612456dfd4ace6f9a589270b3f30db3d46c73'}
PHYS=(0x59E9E2,0x59F510);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4,0x47CC60};LVGL={0x441488};CMSIS={0x4490CC,0x44971C,0x4497B6,0x44981C};NANOPB={0x48EB32};FIRST={0x4434D0,0x45A568,0x464BB2,0x478110,0x478252,0x54F50E,0x596B0C,0x59D8F0,0x59D9D4,0x59DA94,0x59DB5C,0x59DB80,0x59DB9A,0x59DF04,0x59F53C,0x59F71A,0x59F842}
RAW_WORDS=[(0x43E768,0x59F115),(0x5C6930,0x59F10D)];UNALIGNED=(0x794175,0x59EFE1)
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 if json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53':raise c.AuditError('CMSIS changed')
 if json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 provenance()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=11 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2504 or sh(body)!='0d658c74cae6ac517836c984d461773ab1e53abb07b2bf101159fe01c3091aef' or len(ins)!=931 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='7a49bf110fcc1367aff46e38cf858515c78a9af7bbabecbfe0c23641c73f3717' or ind:raise c.AuditError('instruction closure changed')
 non=c._slice(b,0x59EA10,0x59EA64)+c._slice(b,0x59F3FE,0x59F510)
 if len(non)!=358 or sh(non)!='3043136eb5e2a571eda1d79fc2c47c5f3fa36e8426630b9492618c2f169ba892' or sh(c._slice(b,*PHYS))!='eb7b8d2e1128ca37ad70a07f84c651ce48d3b30e945752ce097a9d2282924f97':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='bd49c6290cb8f9c1c3f08ff015fbeef016048133c897fc75e440a099f8fb89a9' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,CMSIS,NANOPB,FIRST)
 if len(calls)!=168 or sum(y in starts for x,y in calls)!=12 or c._pair_digest(calls)!='5635d5d180c4ab2ae26bfc727071bcaf688de3145a3bb4df508cefb54357646a' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(105,7,2,7,3,32):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=23 or c._pair_digest(entries)!='c1d8d5d54fc3d6e500f73e3f739f4ee0502f5d09f868c322c850920fb80550d6' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored[:2]!=[(0x6A46E4,0x59F0EB),(0x6A46E8,0x59F237)] or stored[2:]!=[UNALIGNED] or interior!=RAW_WORDS:raise c.AuditError('stored ingress changed')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 for a,v in RAW_WORDS:
  i=next(D.disasm(c._slice(b,a,a+4),a),None)
  if i is None or i.size!=4:raise c.AuditError('instruction collision changed')
 if sh(c._slice(b,0x79416D,0x794181))!='7f009bac7cd1512007866252a4976e001ad15414c3195f9bd1781dd0877c230e':raise c.AuditError('resource collision changed')
 pairs=[(0x59F410,x) for x in t.literal_references(b,0x59F410)]
 if len(pairs)!=21 or c._pair_digest(pairs)!='cb2d7d206f1123275383f161a66129356db0cf85fbee47bff638e9c873cf5900':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('translate.c' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\translate\translate.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':11,'ghidra_discovered_functions':9,'restored_functions':2,'path_anchored_functions':7,'body_bytes':2504,'physical_bytes':2862,'noncode_bytes':358,'reachable_instructions':931,'direct_body_calls':168,'internal_direct_body_calls':12,'external_direct_body_calls':156,'indirect_body_calls':0,'direct_bl_entry_sites':23,'stored_aligned_function_entry_pointers':2,'unaligned_exact_entry_byte_windows':1,'raw_instruction_word_interior_collisions':2,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':105,'iar_runtime_calls':7,'lvgl_calls':2,'cmsis_freertos_calls':7,'nanopb_calls':3,'first_party_calls':32,'historical_translate_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
