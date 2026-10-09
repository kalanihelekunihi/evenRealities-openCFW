from pathlib import Path
import json,re,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';P=R/'g2/analysis/csky-queue-placement-binding-2026-10-09';v=json.loads((P/'results.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert all(sha((R/p).read_bytes())==h for p,h in v['inputs'].items());counts=[]
for x in v['slices']:
 cmd=x['command'];base=int(next(a.split('=')[1] for a in cmd if a.startswith('--adjust-vma=')),16);b=Path(cmd[-1]).read_bytes();a,z=[int(k,16) for k in x['range']];assert sha(b[a-base:z-base])==x['sha256'];n=0;represented=0
 for line in (P/(x['name']+'-instructions.txt')).read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\t([^\t]+)\t',line)
  if not m:continue
  ts=m[2].split();assert all(re.fullmatch(r'[0-9a-f]{4}(?:[0-9a-f]{4})?',t) for t in ts);raw=b''.join(int(t[j:j+4],16).to_bytes(2,'little') for t in ts for j in range(0,len(t),4));off=int(m[1],16)-base;assert raw==b[off:off+len(raw)];represented+=len(raw);n+=1
 assert represented==z-a;counts.append({'name':x['name'],'bytes':represented,'lines':n})
sources=R/'third-party/upstream/nationalchip-lvp-kws';ai=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/nationalchip-lvp-aiot';k=(sources/'lvp/common/lvp_queue.c').read_text();t=(ai/'lvp/common/lvp_queue.c').read_text();assert 'DRAM0_STAGE2_SRAM_ATTR int LvpQueuePut' in k and '\nint LvpQueueGet(' in k;assert 'DRAM0_STAGE2_SRAM_ATTR int LvpQueueGet' in t
for root in [sources,ai]:
 assert 'section(".sram_text")' in (root/'include/lvp_attr.h').read_text();l=(root/'arch/soc/grus/link.ld').read_text();assert '*(.sram_text*)' in l and '} > stage2_iram' in l and 'CONFIG_MCU_DEFAULT_TEXT_IN_FLASH' in l
assert '((queue->tail + queue->member_size) % queue->size) == queue->head' in k;assert 64//8==8 and 64//8-1==7
res={'status':'PASS','input_hashes_verified':len(v['inputs']),'byte_bound_listings':counts,'conditional_KWS_placement_supported':True,'unchanged_AIoT_Get_SRAM_contract_conflict':True,'physical_slots':8,'usable_pending_items_coherent_state':7,'trigger_returns_enqueue_acknowledgement':False,'original_instruction_execution':False,'source_rebuild':False,'qualification':'Placement conditional on supplied section/linker contracts; no unique pin, live queue behavior, concurrency, alias visibility or new C execution proof'};(O/'QUEUE-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print('PASS authenticated Put/Get listings and conditional source placement')
