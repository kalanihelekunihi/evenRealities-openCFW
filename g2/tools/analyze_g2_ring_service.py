#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for ring_service/ring_service.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ring-service-function-map.tsv';PM=ROOT/'tools/manifests/g2-ring-service-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ring-service-closure.tsv'
PINS={FM:'85d95f6ebb2941a76e4d7a171a737f5eda2f19d56eeba195c195eb82ffefc2cc',PM:'b18cadb1c0d563fa3bdc02a1574d5675aec88df80e25d4f457dfc9cbe7801df9',CL:'d99c094400517ea256f31397758efb8fb09cdc2f363468769666b53906f9192a'}
PHYS=(0x472244,0x472C7C);PATH=0x6E99A0;CELL=0x472BB8
EASY={0x43CE9E,0x43D0CE,0x43D574,0x43DACC};CMSIS={0x4490CC};RUNTIME={0x43C0E4};NANOPB={0x48EB32};CORDIO=set()
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());nano=json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or nano['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=18 or sum(r['path_anchored']=='yes' for r in rows)!=9:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un!=[(0x4722CC,0x4722D8)] or len(body)!=2412 or sh(body)!='b15d46162880935c8821b9b5569652a91cce2b63a371c24fe9d240e9764a3c19' or len(ins)!=927 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='5d5e248a33bc1bc8d9979a1fded880124d675cf0f4a6a9474464474373c2dd6e' or dyn:raise c.AuditError('body closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=216 or sh(outer)!='f2bba78a9e2e09000b016cb610aa3ee44041f5602ebd06cde77ba9dda195c48d' or sh(c._slice(b,*PHYS))!='77a47da23989d6e3d04630cb85a6aa07bc0a5ded843d23003094dc76aff98d94':raise c.AuditError('physical closure changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-EASY-CMSIS-RUNTIME-NANOPB-CORDIO
 if len(calls)!=125 or sum(t in starts for _,t in calls)!=4 or c._pair_digest(calls)!='684e8111506a61e4c4547d27144fcf3cc1eb112387c15184a07e4e6b5fe703bf' or tuple(sum(ext[t] for t in s) for s in (EASY,CMSIS,RUNTIME,NANOPB,CORDIO,first))!=(76,2,8,1,0,34):raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=27 or c._pair_digest(entries)!='6ab60aeab49c810052a64566be00273554c0f1f56bcf77f83a5d66d64f3609ca' or strict or non or wide or ws:raise c.AuditError('branch ingress changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((c.BASE+off,v,t))
   if t in starts and (c.BASE+off)%4==0 and v&1:stored.append((c.BASE+off,v))
 if len(raw)!=3 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='4494c7b68d01fafa3d43de36ac7c3ab36277ea4d59b93e1121ad844a147ae45a' or len(stored)!=2 or c._pair_digest(stored)!='4b208ce5348811221845f9de477bf864e82712015054c86b5e3bbb06c37fbd2d':raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ring_service\ring_service.c':raise c.AuditError('path changed')
 refs=sorted((CELL,a) for a in th.literal_references(b,CELL))
 if len(refs)!=15 or c._pair_digest(refs)!='8072e267036004c984d3b8547dc8f3b5ad5c906369e1fcac609098097042419a':raise c.AuditError('path refs changed')
 routed=any('ring_service' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\protocols\ring_service\ring_service.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':18,'path_anchored_functions':9,'body_bytes':2412,'physical_bytes':2616,'outer_pool_bytes':216,'reachable_instructions':927,'direct_body_calls':125,'internal_direct_body_calls':4,'external_direct_body_calls':121,'indirect_body_calls':0,'direct_bl_entry_sites':27,'stored_function_pointers':2},'provider_boundary':{'easylogger_calls':76,'cmsis_freertos_calls':2,'runtime_calls':8,'nanopb_calls':1,'cordio_calls':0,'first_party_calls':34,'historical_ring_service_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
