#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for efs_transport.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-efs-transport-function-map.tsv';PM=ROOT/'tools/manifests/g2-efs-transport-provider-map.tsv';CL=ROOT/'tools/manifests/g2-efs-transport-closure.tsv'
SOURCE=ROOT/'components/apollo_main/core_overlay/efs_transport.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
PINS={FM:'5bf8d4181e1f2051e1c3a741ac1bb781257fed67e9797dd6211f59cb70bed2fd',PM:'a8521cc8865ec2e2b82675b6ebaad9ab13cbc26dbb553acb3915da5e0b423ebb',CL:'aac6aae8962f6cf115cdf78e4e5d51a58e98444fd823bf0c8f7e00587232c136'}
PHYS=(0x4D0D80,0x4D15E8);PATH=0x6E78D0;CELL=0x4D1550
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC};RUNTIME={0x439BE4,0x43C0E4};EFS={0x458BD2,0x458BF8};CRC={0x49ACD4};HEAP={0x474D16}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or 'deff9ab509341f264addbd3c8ada533678591905' not in (ROOT/'third_party/tlsf/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=2 or sum(r['path_anchored']=='yes' for r in rows)!=2:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];un=[];body=b''
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;un+=c._uncovered((a,z),ii);body+=c._slice(b,a,z)
 calls.sort()
 if un or len(body)!=1990 or sh(body)!='110eeac10f41244a3cae4b64306dd25bc7e748153a76cd7401038d74ddbbc9a2' or len(ins)!=766 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='e09a97ae0e20c3e2c11ed5d1c38f93c8746d45519d23ba18156aa76743c488a4' or dyn!=[0x4D0E6A,0x4D10C6,0x4D128A,0x4D14B0]:raise c.AuditError('body/indirect closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=162 or sh(outer)!='b6c01ee60c344ec04e29c8c9ecdd94e688688640e1d9d76633bb72c060560b86' or sh(c._slice(b,*PHYS))!='0ab3e18ff423dcefe53b23dd206325bbe960ba331f12501604cc6967c30cc704':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='9d2131be91fb6a1d3de217c6164d1851b1070a75df7a71f346cffd641c5a6a89' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='09968466bc2bb41af3c91c9baacf80f34b53c0cc4bc54b38e73a0b6fed0b6f57':raise c.AuditError('boundary changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-EASY-CMSIS-RUNTIME-EFS-CRC-HEAP
 if len(calls)!=87 or c._pair_digest(calls)!='f897cace2a297340f562259b55955499a9efc6011cb00f8a195b724d4a422ce4' or tuple(sum(ext[t] for t in s) for s in (EASY,CMSIS,RUNTIME,EFS,CRC,HEAP,first))!=(60,1,8,5,4,6,3):raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=2 or c._pair_digest(entries)!='b2e868b3462d44ea7c5758bb75ef6e00dd29d54e9bba7a4855d06a51a8f88e5a' or strict or non or wide or ws:raise c.AuditError('branch ingress changed')
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\platform\protocols\efs_service\efs_transport.c':raise c.AuditError('path changed')
 refs=sorted((CELL,a) for a in th.literal_references(b,CELL))
 if len(refs)!=13 or c._pair_digest(refs)!='af091257246ec2c55eabfdd7d9696f46f570f497bce344f24ef906805dbfc003':raise c.AuditError('path refs changed')
 source=SOURCE.read_bytes()
 if len(source)!=13453 or sh(source)!='6facd03cb8f48f68b61d14e100106e505c1dd869f715752c1ea2742375485514':raise c.AuditError('production EFS transport source changed')
 overlay=json.loads(OVERLAY.read_text());leaves={x['function']:x for x in overlay['relocated_leaves']};patches={x['name']:x for x in overlay['patch_sites']}
 production=[('EFS_ReceivePacket',700,215572,12,0x4D0D80,1374,'eb5dd1f1f34063c660a796e236079e23b8ce0709adff70212709f41f2a96cafb'),('EFS_SendPacket',576,216272,3,0x4D12DE,616,'67ef77338d11810123f2d592d857839758832561cef80e943c23c9990ecfcab1')]
 for order,(name,size,offset,relocs,address,stock_size,stock_hash) in enumerate(production,1):
  leaf=leaves.get(name)
  if not leaf or leaf.get('source',{}).get('path')!='components/apollo_main/core_overlay/efs_transport.c' or leaf.get('source',{}).get('sha256')!=sh(source) or leaf.get('source',{}).get('size')!=len(source) or leaf.get('expected',{}).get('size')!=size or leaf.get('expected',{}).get('offset')!=offset or leaf.get('expected',{}).get('alignment')!=4 or len(leaf.get('relocations',[]))!=relocs or not leaf.get('strict_relocation_contract') or leaf.get('profiles')!=['apple-clang']:raise c.AuditError(f'production EFS transport leaf changed: {name}')
  patch=patches.get(f'replace_efs_transport_{order:02d}')
  if not patch or patch.get('runtime_address')!=address or patch.get('expected_size')!=stock_size or patch.get('expected_sha256')!=stock_hash or patch.get('target_function')!=name or patch.get('branch')!='b_w' or patch.get('profiles')!=['apple-clang']:raise c.AuditError(f'production EFS transport patch changed: {name}')
 report=json.loads(REPORT.read_text());reported={x['extraction']['function']:x for x in report['relocated_leaves']}
 for name,size,offset,relocs,*_ in production:
  item=reported.get(name)
  if not item or item['placement']['offset']!=offset or item['placement']['size']!=size or item['placement']['alignment']!=4 or item['extraction']['relocation_count']!=relocs:raise c.AuditError(f'production EFS transport build report changed: {name}')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions={x['name']:x for x in main['regions']}
 if (main['provider']['size'],main['provider']['sha256'],manifest['package']['expected_size'],manifest['package']['expected_sha256'])!=(3764088,'b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed',4542582,'275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85'):raise c.AuditError('production EFS transport manifest pins changed')
 expected_regions={'efs_transport_01_source_replacement':(0x4D0D80,1374,'generated_source_entry_replacement'),'efs_transport_02_source_replacement':(0x4D12DE,616,'generated_source_entry_replacement'),'efs_transport_retained_pool':(0x4D1546,162,'official_blob'),'efs_transport_receive_source_text':(0x7C8D38,700,'source_compiled'),'efs_transport_send_source_text':(0x7C8FF4,576,'source_compiled')}
 for name,expected in expected_regions.items():
  item=regions.get(name)
  if not item or (item.get('target_address'),item.get('size'),item.get('address_status'))!=expected:raise c.AuditError(f'production EFS transport region changed: {name}')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\protocols\efs_service\efs_transport.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':2,'path_anchored_functions':2,'body_bytes':1990,'physical_bytes':2152,'outer_pool_bytes':162,'reachable_instructions':766,'direct_body_calls':87,'internal_direct_body_calls':0,'external_direct_body_calls':87,'indirect_body_calls':4,'indirect_call_sites':dyn,'direct_bl_entry_sites':2,'stored_function_pointers':0},'provider_boundary':{'easylogger_calls':60,'cmsis_freertos_calls':1,'runtime_calls':8,'efs_service_calls':5,'crc16_calls':4,'heap_wrapper_calls':6,'first_party_calls':3,'registered_callback_calls':4,'callback_slots':['0x2000096C','0x20000970'],'historical_efs_transport_commit':None,'new_version_discriminator':False},'production':{'candidate':'components/apollo_main/core_overlay/efs_transport.c','production_routed':True,'source_functions':2,'compiled_text_bytes':1276,'alignment_bytes':0,'strict_relocations':15,'stock_replaced_bytes':1990,'retained_pool_bytes':162,'software_functional_gap':False,'hardware_validation':'blocked','hardware_blocker':'No authorized responsive G2 peer is physically available for live EFS import/export, fragmentation, CRC-failure, timeout, disconnect/resume, and media-content evidence; the authorized right temple is nonresponsive and the left temple must remain stock.'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
