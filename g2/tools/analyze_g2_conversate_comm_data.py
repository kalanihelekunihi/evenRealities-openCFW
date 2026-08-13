#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_comm_data.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-conversate-comm-data-function-map.tsv';PM=ROOT/'tools/manifests/g2-conversate-comm-data-provider-map.tsv';CL=ROOT/'tools/manifests/g2-conversate-comm-data-closure.tsv'
PINS={FM:'5de5f9f4522d022b1011935790dc6aab8e4119e561737ccc450f501a44731dfd',PM:'1d453213096fa1623995969d06d226138d6268fba4fff390864ac572b5a03673',CL:'2da99f43f28465a969a111ca785b199f594a0479dfa6f8715c3849ae50ade8d4'}
PHYS=(0x5B3EF8,0x5B48F8);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};LVGL={0x4897FC};RAW_WORD=(0x490D18,0x5B402B)
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=12 or sum(r['source_path_anchor']=='yes' for r in rows)!=6:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2208 or sh(body)!='27e0783249547617bd7841360e6df6ec6fbb690bbf73a1f90a627d9e8d00138a' or len(ins)!=871 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='a9fc9ce78f0e5828ddb58431a053f6d15b5225f79cd606fb249c99438e9a80d4' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=352 or sh(non)!='4d1259e267fe3d8a2ea208244635a5fb485b33e37587b6920654cf9202c27e62' or sh(c._slice(b,*PHYS))!='ee090313b610b346eca7b536814d4039b2bbfcd417df44907f33571726a27450':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='b68febb0690a40b0af5c33c28ba7b4dd7762bed5212a251ed504a832d8112f42' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='8ab712416f2fabb4ce7f386192b95f3951ee1a20beab71362fe53b90576985cf':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL)
 if len(calls)!=77 or sum(y in starts for x,y in calls)!=5 or c._pair_digest(calls)!='b0c2e1915edcb8832b8ead5e9242eda9fa33021a70f22278ee52cba7ea763693' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(60,11,1):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=22 or c._pair_digest(entries)!='4f2fb75a63eec880a3a91505f901a772b223ec87ea76fc52b7a372d0d58d4791' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior!=[RAW_WORD]:raise c.AuditError('stored ingress changed')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);ii=list(D.disasm(c._slice(b,RAW_WORD[0],RAW_WORD[0]+4),RAW_WORD[0]))
 if len(ii)!=2 or any(i.size!=2 for i in ii):raise c.AuditError('instruction-word collision changed')
 if cstring(b,0x6EC4D8)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_comm_data.c':raise c.AuditError('path changed')
 pairs=[(0x5B4858,x) for x in t.literal_references(b,0x5B4858)]
 if len(pairs)!=13 or c._pair_digest(pairs)!='b8560d5f3455fd87bdab1b8aadadbeac03ab53d42e4a2ec3410ca42ab8e74826':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('conversate_comm_data' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\conversate\conversate_comm_data.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':12,'ghidra_discovered_functions':12,'restored_functions':0,'path_anchored_functions':6,'body_bytes':2208,'physical_bytes':2560,'noncode_bytes':352,'reachable_instructions':871,'direct_body_calls':77,'internal_direct_body_calls':5,'external_direct_body_calls':72,'indirect_body_calls':0,'direct_bl_entry_sites':22,'stored_function_entry_pointers':0,'raw_instruction_word_interior_collisions':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':60,'iar_dlib_calls':11,'lvgl_calls':1,'historical_conversate_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
