#!/usr/bin/env python3
"""Fail-closed object/provider audit for the embedded cJSON parser body (g2-json-parser)."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-json-parser-function-map.tsv';CL=ROOT/'tools/manifests/g2-json-parser-closure.tsv'
PINS={FM:'3da8d5145ff3a49c454b7d342ec6fa663a9f4def717b8c53c3542136f22c6878',CL:'eea456f98d57361981f91b04337686e085e0865b7794a243fdaa989827c17963'}
PHYS=(0x4D798C,0x4D83D8)
IAR={0x43C0E4,0x44A43C,0x44B610,0x46CACC};NANOPB={0x48949C};IAR_UNCLOSED={0x4D58C2,0x542D48}
BLX=(0x4D79E2,0x4D7A2A,0x4D7A40,0x4D7A4A,0x4D7CC2,0x4D7D36)
EXT_ENTRIES=((0x48E58A,0x4D7F7E),(0x48E5D4,0x4D83AA),(0x48E61A,0x4D79FA),(0x48E624,0x4D83AA),(0x48E62E,0x4D83AA),(0x48E638,0x4D83AA),(0x48E642,0x4D83AA),(0x48E64C,0x4D83AA),(0x48E656,0x4D83AA),(0x48E660,0x4D83AA),(0x48E66A,0x4D83AA),(0x48E674,0x4D83AA),(0x48E722,0x4D79FA),(0x4D59C6,0x4D7F7E),(0x4D5A34,0x4D83AA),(0x4D5A84,0x4D79FA),(0x4D5AA8,0x4D83AA),(0x4D5AF8,0x4D79FA),(0x4D5B1C,0x4D83AA),(0x4D5B6C,0x4D79FA),(0x4D5B90,0x4D83AA),(0x4D5BE0,0x4D79FA),(0x4D5C00,0x4D83AA),(0x4D5C4E,0x4D79FA),(0x4D5C5E,0x4D83AA),(0x4D5CAE,0x4D79FA),(0x4D5CD0,0x4D83AA),(0x4D5D20,0x4D79FA),(0x4D5D2A,0x4D83BC),(0x4D5D36,0x4D830C),(0x4D5E50,0x4D83AA),(0x4D5E5C,0x4D83AA),(0x4D5ECA,0x4D8344),(0x4D5F24,0x4D79FA))
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 nano=json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())
 if nano['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb provider provenance changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=21 or any(r['source_path_anchor']!='no' or r['ghidra_discovered']!='no' for r in rows):raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2572 or sh(body)!='ad3ec2fe0550a87aca90b84d7bd9481445cc75d6a11571c8f9f13270097e37d5' or len(ins)!=1172 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='5a8b6793781392ac2d56fc3f95691ad94a0c1bd371533f000879ca6884c6232a':raise c.AuditError('instruction closure changed')
 if tuple(ind)!=BLX:raise c.AuditError('indirect hook-dispatch sites changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=64 or sh(non)!='26d32b1b8ba37bc805b8b86de34fcc5168b310fe4d6c13641371199d59944d45' or sh(c._slice(b,*PHYS))!='07f8a8063cb577146e1c24ee87557012f76b4066c1cf0681102ae20210e4e394':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='6e8c884158bd8cc2c65ca67785315d1436e5ce362ea06bdeb950b68919a74f52' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='2ca8e8072b6c6e3a284320cfde303aeb51f0d5ce6afa1a8580ffceb2a738c518':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(IAR,NANOPB,IAR_UNCLOSED)
 if len(calls)!=47 or sum(y in starts for x,y in calls)!=34 or c._pair_digest(calls)!='cd7956de06b337e934ca7e36317924e86e6c57e8274291dfbc6348891b10fc06' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(7,1,5):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[];ientries=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in ientries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=68 or c._pair_digest(entries)!='9d39c3743dfe5e8d5fe8b70c89687aec20bd1deecf7ef6d8e220edf762f62b03' or strict or pseudo:raise c.AuditError('BL ingress changed')
 ext_entries=sorted((x,y) for x,y in entries if not(PHYS[0]<=x<PHYS[1]))
 if tuple(ext_entries)!=EXT_ENTRIES or c._pair_digest(ext_entries)!='ce3f46f29265246b1ba57c6e5a3bef42b1cb9dc52d4ad135eb3cf52d625eb7f1':raise c.AuditError('external entry closure changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in ientries]
 if stored or interior:raise c.AuditError('stored ingress changed')
 def bw(a):
  f,s=struct.unpack_from('<HH',b,a-c.BASE)
  if f&0xF800!=0xF000 or s&0xD000!=0x9000:return None
  sg=(f>>10)&1;j1,j2=(s>>13)&1,(s>>11)&1;i1,i2=(~(j1^sg))&1,(~(j2^sg))&1
  im=((sg<<24)|(i1<<23)|(i2<<22)|((f&0x03FF)<<12)|((s&0x07FF)<<1))
  if im&(1<<24):im-=1<<25
  return a+4+im
 if any(bw(a) in starts or bw(a) in ientries for a in range(c.BASE,c.BASE+len(b)-3,2)):raise c.AuditError('B.W ingress changed')
 pool={0x4D7F8C:0x2007410C,0x4D7F94:0x200004BC,0x4D80D0:0x78D15C,0x4D80D4:0xFFC00,0x4D83B4:0x78D164,0x4D83B8:0x78D16C}
 if any(struct.unpack_from('<I',b,a-c.BASE)[0]!=v for a,v in pool.items()):raise c.AuditError('literal pool pointer changed')
 if b[0x4D7F90-c.BASE:0x4D7F94-c.BASE]!=bytes.fromhex('efbbbf00'):raise c.AuditError('UTF-8 BOM literal changed')
 if struct.unpack_from('<d',b,0x4D7B38-c.BASE)[0]!=0.0 or struct.unpack_from('<d',b,0x4D7B40-c.BASE)[0]!=2147483647.0 or struct.unpack_from('<Q',b,0x4D7B48-c.BASE)[0]!=0xC1DFFFFFFFFFFFFF:raise c.AuditError('parse_number double constants changed')
 for a,s in ((0x78D15C,'null'),(0x78D164,'false'),(0x78D16C,'true')):
  o=a-c.BASE;e=b.find(b'\0',o)
  if e<0 or b[o:e].decode('ascii')!=s:raise c.AuditError('literal pool string changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('json' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented JSON parser routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':None,'upstream_family':'cJSON (DaveGamble/cJSON)','upstream_version_interval':'v1.7.9 through v1.7.12','embedded_third_party_definitions':['cJSON 1.7.9-1.7.12 parse-side subset: ParseWithOpts/Parse/parse_value/parse_string/parse_number/parse_array/parse_object/parse_hex4/utf16_literal_to_utf8/buffer_skip_whitespace/skip_utf8_bom/get_decimal_point/case_insensitive_strcmp/cJSON_New_Item plus public cJSON_Delete/GetArraySize/GetArrayItem/GetObjectItem/IsArray']},'surface':{'linked_functions':21,'ghidra_discovered_functions':0,'restored_functions':21,'path_anchored_functions':0,'body_bytes':2572,'physical_bytes':2636,'noncode_bytes':64,'reachable_instructions':1172,'direct_body_calls':47,'internal_direct_body_calls':34,'external_direct_body_calls':13,'indirect_body_calls':6,'direct_bl_entry_sites':68,'external_direct_bl_entry_sites':34,'stored_function_entry_pointers':0,'strict_interior_ingress':0,'b_w_entry_or_interior_targets':0},'provider_boundary':{'admitted_nanopb_shared_initializer_calls':1,'nanopb_commit':'98bf4db69897b53434f3d0ba72e0a3ab1a902824','iar_dlib_calls':7,'unclosed_iar_runtime_calls':5,'unclosed_iar_runtime_bodies':['0x004D58C2 tolower trampoline','0x00542D48 strtod'],'hook_dispatch_sites':6,'cmsis_freertos_calls':0,'freertos_kernel_calls':0,'new_version_discriminator':True,'version_interval':'cJSON v1.7.9 through v1.7.12'},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
