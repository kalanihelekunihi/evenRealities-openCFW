from pathlib import Path
import json,hashlib,re,struct
root=Path(__file__).resolve().parent;repo=root.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
allb=sum([json.loads((root/name).read_text()) for name in ['bodies.json','bodies-callbacks.json','bodies-app.json']],[]);assert len(allb)==24 and all(b['decompile_completed'] for b in allb)
checks=[];intervals=[]
for b in allb:
 stem=hex(b['entry'])[2:];g=(root/(stem+'-ghidra.txt')).read_text();o=(root/(stem+'-objdump.txt')).read_text();ga=set(int(x,16) for x in re.findall(r'> INSN ([0-9a-f]+) ',g));oa=set(int(x,16) for x in re.findall(r'^([0-9a-f]+):\s+[0-9a-f]+\s+',o,re.M));assert ga<=oa,(stem,ga-oa)
 checks.append({'entry':b['entry'],'ghidra_instruction_count':len(ga),'all_instruction_addresses_present_in_independent_objdump':True,'type_propagation_warning':'Type propagation algorithm not settling' in g});intervals.extend((b['image'],s['runtime'][0],s['runtime'][1]) for s in b['spans'])
for image,a,z in intervals:
 assert all(image!=im or z<=x or y<=a or (a,z)==(x,y) for im,x,y in intervals)
inputs=['g2/build/pseudocode-first/20260930T190500Z/identity.json','g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl','g2/build/pseudocode-first/20260930T190500Z/reviews/codec-xip-linked-address-review-068/review.json','third-party/upstream/nationalchip-lvp-kws/lvp/common/lvp_system_init.c','third-party/upstream/nationalchip-lvp-kws/lvp/lvp_mode.c','third-party/upstream/nationalchip-lvp-kws/lvp/lvp_mode.h','third-party/upstream/nationalchip-lvp-kws/lvp/lvp_mode_idle.c','third-party/upstream/nationalchip-lvp-kws/lvp/lvp_mode_tws.c','third-party/upstream/nationalchip-lvp-kws/lvp/app_core/lvp_app_core.c','third-party/upstream/nationalchip-lvp-kws/lvp/app_core/lvp_app.h','third-party/upstream/nationalchip-lvp-kws/lvp/common/lvp_queue.c','third-party/upstream/nationalchip-lvp-kws/lvp/common/lvp_queue.h','third-party/upstream/nationalchip-lvp-kws/app/sample/lvp_app_sample.c','third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/link.ld']
receipt={'schema_version':1,'campaign_id':'20260930T190500Z','target_sha256':'f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa','status':'partial_ready_for_independent_review','function_bodies':24,'unique_instruction_bytes':sum(b['total_bytes'] for b in allb),'input_hashes':{p:sha(repo/p) for p in inputs},'address_agreement_checks':checks,'remaining_boundary':'Firmware-specific application state helpers, NPU/audio providers, mutable callback targets and external XIP/DRAM visibility; no gate closure.'}
(root/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
images={x['id']:x for x in map(json.loads,(repo/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').open())};rec=images['binh_a_stage2_xip'];data=(repo/rec['content_path']).read_bytes();base=0x10203004;rows=[]
for a in range(0x10207a08,0x10207a7c,4):
 v=struct.unpack('<I',data[a-base:a-base+4])[0];s=data[v-base:].split(b'\0',1)[0] if base<=v<base+len(data) else None;rows.append({'pool_runtime':a,'pool_child_offset':a-base,'value':v,'utf8_if_valid':s.decode('utf8',errors='replace') if s is not None else None})
(root/'system-init-literals.json').write_text(json.dumps(rows,indent=2)+'\n')
manifest={p.name:sha(p) for p in sorted(root.iterdir()) if p.is_file() and p.suffix in ['.txt','.json','.py','.md'] and p.name!='SHA256MANIFEST.json'};(root/'SHA256MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('24 bodies;',receipt['unique_instruction_bytes'],'bytes; independent native instruction address checks passed')
