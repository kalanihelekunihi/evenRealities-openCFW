#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for terminal_data.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-terminal-data-function-map.tsv';PM=ROOT/'tools/manifests/g2-terminal-data-provider-map.tsv';CL=ROOT/'tools/manifests/g2-terminal-data-closure.tsv'
PINS={FM:'00ce7df4bfbe38e0101f0cfbbfa27c921827393cd66c19a02844b6d8fe19a435',PM:'19f9df4d0bb92c020b5148ae7816b17727a6773380331e66d8058affebe8f346',CL:'32fa1a214c8b35af85d44368951735ed52c06e7c415c5ff8ff1b2f42bb98df5b'}
PHYS=(0x5970A8,0x597C6C);PATH_ADDR=0x6FDAE4;CELL=0x597C28
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};TIME={0x44A1EA}
STRICT=[(0x4925C0,0x597654)];PSEUDO=[(0x4A4616,0x597C20)];INTERIOR=[(0x58B787,0x5970D1)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=44 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort()
 if len(body)!=2902 or sh(body)!='91a39f6debcb7038af836313f4a9e6db9b75c58c1e197919be911b153fab90ce' or len(ins)!=1123 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='60c6f1a5c4bde2fa7aee488395580ed5cd043f743be91a627a18660851cf9e70' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=110 or sh(non)!='7052040913232eed37d18b21d92f2bf38807cbb76d7a0e66349c781348f36821' or sh(c._slice(b,*PHYS))!='1dd9b7530c35ec637447595ca4ed8db67c81761e582b78b9531e0881978dbef8':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='4999b9437a8dfdfd369c6b9bd8772095467ec3209d8f8b65dcc05aaa891faa4f' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='cdcca81be6a951b5d7541588eb3701c82bf8bd22e5f2047417227ff1e35c9e8e':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,TIME)
 if len(calls)!=73 or sum(y in starts for x,y in calls)!=28 or c._pair_digest(calls)!='9c8bf0c8c4ff5f174594739c78a63d6e6b75e7b7f9aecdba4bbeb2b54864d22c' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(30,13,2):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=180 or c._pair_digest(entries)!='cb9b3a0f9f38b9045efdd678467753e4755e19d14ea64df707afec3644a2bde8' or strict!=STRICT or c._pair_digest(strict)!='4da92b0c366bf40a64b4041b7562c7685a9bfe155c48e308be281f0aacb655a6' or pseudo!=PSEUDO or c._pair_digest(pseudo)!='c4629cedf9dd1e9891dd5aa435e4882c1e255729146e760b3a7cb223e3e035ab':raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored or interior!=INTERIOR or c._pair_digest(interior)!='c70085845ec619217a4b83f62da095a5a923fabe9ec77c00b2b1c8b74f4ea700':raise c.AuditError('stored ingress changed')
 o=PATH_ADDR-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0 or b[o:e].decode('ascii')!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_data.c':raise c.AuditError('path changed')
 refs=t.literal_references(b,CELL);pairs=[(CELL,x) for x in refs]
 if len(refs)!=6 or c._pair_digest(pairs)!='4a86d0ba15c37774447277f2496c4e1191f3b21fd852aa0aadea4811253d734e':raise c.AuditError('path refs changed')
 if any('terminal_data' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\terminal\terminal_data.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':44,'ghidra_discovered_functions':4,'restored_functions':40,'path_anchored_functions':4,'body_bytes':2902,'physical_bytes':3012,'noncode_bytes':110,'reachable_instructions':1123,'direct_body_calls':73,'internal_direct_body_calls':28,'external_direct_body_calls':45,'indirect_body_calls':0,'direct_bl_entry_sites':180,'external_direct_bl_entry_sites':152,'stored_function_entry_pointers':0,'stored_interior_pointers':1,'strict_interior_ingress':1,'raw_noncode_pseudo_bl':1},'provider_boundary':{'easylogger_calls':30,'iar_dlib_calls':13,'closed_time_service_calls':2,'cmsis_freertos_calls':0,'freertos_kernel_calls':0,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
