#!/usr/bin/env python3
"""Alternate-method raw Thumb operand review plus bounded stack-evidence audit."""
from pathlib import Path
import json,struct,hashlib,collections
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;B=H.parent;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';blob=F.read_bytes()[32:];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:{'path':str(p.relative_to(R)),'sha256':sha(p)}
original=json.loads((B/'case-wave025-ram-callback-provenance/verification.json').read_text());audit=json.loads((B/'case-wave053-native-ram-effective-addresses/verification.json').read_text());catalogue=list(map(json.loads,(R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()));functions={int(x['entry'],16):x for x in catalogue};rows=[];defects=[]
# Decode only architectural Thumb16 immediate memory forms directly from bytes,
# independently of disassembler text/CFG parser in wave053.
def memory_operand(word):
 top=word&0xf800
 if top in [0x6000,0x6800]:size=4;kind='read' if top==0x6800 else 'write';scale=4
 elif top in [0x7000,0x7800]:size=1;kind='read' if top==0x7800 else 'write';scale=1
 elif top in [0x8000,0x8800]:size=2;kind='read' if top==0x8800 else 'write';scale=2
 else:return None
 return {'base_register':'r'+str((word>>3)&7),'offset':((word>>6)&31)*scale,'size':size,'kind':kind,'data_register':'r'+str(word&7)}
for target in [x['address'] for x in original['RAM_literals'] if not x['aligned_native_literal_word_locations']]:
 candidates=[]
 for hit in audit['joins'][target]:
  pc=int(hit['PC'],16);word=struct.unpack_from('<H',blob,pc-0x08000000)[0];decoded=memory_operand(word)
  if decoded is None:continue
  addr=int(hit['effective_address'],16);fn=functions[int(hit['function_entry'],16)]
  assert int(fn['body_start'],16)<=pc and pc+2<=int(fn['body_end_inclusive'],16)+1
  assert decoded['size']==hit['access_bytes'] and decoded['kind']==hit['kind']
  assert addr<=int(target,16)<addr+decoded['size']
  base=addr-decoded['offset'];basebytes=struct.pack('<I',base);literal_locations=[hex(0x08000000+i) for i in range(0,len(blob)-3,4) if blob[i:i+4]==basebytes]
  candidates.append({'PC':hex(pc),'function_entry':hit['function_entry'],'native_opcode':hex(word),'decoded_operand':decoded,'required_base_value':hex(base),'effective_address':hex(addr),'same_base_native_word_locations':literal_locations,'scope':'Operand/width/offset verified independently; base-register reaching definition remains separate CFG obligation'})
 if not candidates:defects.append({'target':target,'defect':'No independently decodable immediate memory operand among proposed examples'})
 rows.append({'target':target,'examples':candidates,'status':'RAW_OPERAND_CONFIRMED' if candidates else 'UNCONFIRMED'})
assert not defects,defects
# Existing measured stack samples are reviewed once; do not repeat executions.
stack_sources=[('case-wave023-native-stack-envelope','verification.json','native_initial_SP'),('case-wave036-heap-provider','verification.json','native_initial_SP'),('case-wave037-stock-queue-dynamic-delete','verification.json','native_initial_SP'),('case-wave040-event-waiter-wakeup','verification.json','native_initial_SP'),('case-wave042-waiter-preemption-request','verification.json','native_initial_SP'),('case-wave043-task-frame-init','verification.json','native_initial_SP'),('case-wave044-pendsv-context-boundary','verification.json','native_initial_SP')]
stack=[]
for folder,file,scope in stack_sources:
 p=B/folder/file;d=json.loads(p.read_text());samples=d.get('comparisons',[]);native=[x['native_stack_bytes'] for x in samples if 'native_stack_bytes' in x];source=[x['source_stack_bytes'] for x in samples if 'source_stack_bytes' in x]
 if not source:continue
 stack.append({'evidence':ref(p),'cases':d.get('cases'),'native_max_bytes':max(native),'source_max_bytes':max(source),'source_remaining_in_1024_byte_MSP_window':1024-max(source),'scope':scope,'limitations':d.get('limits',[])})
# Pin the actual static storage envelope from native-derived heap setup.
heap_source=R/'g2/components/case/startup_candidate_20261011/application_boot_heap_allocate_candidate.c';heap_text=heap_source.read_text();assert 'start=0x20001c88u' in heap_text and 'span=3072u' in heap_text
initial_msp=0x20002c88;heap_footer_end=0x20001c88+3072;assert initial_msp-heap_footer_end==1024
# A function extent may contain inline strings. Filter verified data before
# considering a raw BX/BLX encoding an indirect-control site.
string_ranges=[(int(x['native_address'],16),int(x['native_address'],16)+x['bytes_including_NUL']) for x in original['strings']]
indirect=[];inline_data=[]
classes={'080000c0':'fixed application veneer','080000cc':'first-task architectural handoff','08000102':'architectural EXC_RETURN','08000144':'fixed reset hook/start handoff','08000270':'CRT initialization record dispatcher','08009170':'saved-LR function return','08009190':'compiler switch-table dispatch','08009210':'formatter emit argument','08009638':'formatter padding emit argument','08009658':'formatter padding emit argument','080048e6':'DMA handle callback slot +0x38','08005f50':'UART handle RxISR slot +0x74','0800b0a0':'timer callback slot +0x20','0800b0fc':'deferred-message callback or timer callback','0800b2b0':'timer callback slot +0x20'}
for fn in catalogue:
 lo=int(fn['body_start'],16);hi=int(fn['body_end_inclusive'],16)+1
 for pc in range(lo,hi-1,2):
  word=struct.unpack_from('<H',blob,pc-0x08000000)[0]
  if word&0xff87 not in [0x4700,0x4780]:continue
  register=(word>>3)&15;kind='BLX' if word&0x80 else 'BX'
  if kind=='BX' and register==14:continue
  entry={'function_entry':fn['entry'],'PC':hex(pc),'opcode':hex(word),'kind':kind,'register':register}
  data=[(a,b) for a,b in string_ranges if a<=pc<b]
  if data:entry['verified_string_ranges']=[list(map(hex,x)) for x in data];inline_data.append(entry)
  else:entry['contract_class']=classes.get(fn['entry'],'requires code/data classification');indirect.append(entry)
assert len(inline_data)==6 and len(indirect)==23
# Regression for the review method: these six BX-like words are authenticated
# string bytes and must never become callback roots or executable coverage.
assert all(x['kind']=='BX' and x['register']==4 for x in inline_data)
assert not any(any(a<=int(hit['PC'],16)<b for a,b in string_ranges) for hits in audit['joins'].values() for hit in hits)
r={'status':'PASS_BOUNDED_RAW_RAM_OPERAND_AND_STACK_EVIDENCE_REVIEW','firmware':ref(F),'reviewed_RAM_targets':len(rows),'RAM_operand_review':rows,'actual_source_defects_found':defects,'indirect_control_candidates':indirect,'raw_branch_encodings_in_verified_string_data':inline_data,'binding_sources':[ref(R/'g2/components/case/uart_start_offline/start.c'),ref(R/'g2/components/case/source_candidate_20261010/dma_abort_provider.c'),ref(R/'g2/components/case/source_candidate_20261010/uart_irq_continuations.c'),ref(R/'g2/components/case/startup_candidate_20261011/application_policy_event_scheduler_helpers_candidate.c')],'measured_stack_evidence':stack,'maximum_measured_source_MSP_bytes':max(x['source_max_bytes'] for x in stack),'heap_storage_source':ref(heap_source),'native_initial_MSP':hex(initial_msp),'heap_footer_end':hex(heap_footer_end),'MSP_window_bytes':1024,'limits':['Alternate-method mechanical operand check, not an independent reviewer acceptance or whole-CFG reachability/code-data classification proof','A native word matching a base value is provenance evidence; it does not prove the load reaches that memory access or its object extent','Measured synchronous maxima are lower bounds on global worst-case use, not upper bounds; IRQ nesting/reentrancy and other callbacks remain unqualified'],'review_method_correction':'Whole-function byte scans alone would count six string-embedded BX encodings as code; verified-data filtering rejects them. This is an analysis-method issue, not a firmware source defect.', 'missing_inputs_for_global_gate':['Complete indirect call-site to runtime target binding/registration/lifetime inventory, not merely39 known roots','Verified IRQ priority configuration and feasible nesting/reentrancy scenarios after actual CASE startup (or an independently validated complete STM32G0 peripheral model)','Stack use for unexercised hardware/error paths and live task/ISR transcripts covering such paths','Independent review of original code/data boundaries and CFG definition chains used by wave053']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['reviewed_RAM_targets'],r['maximum_measured_source_MSP_bytes']);print([(x['evidence']['path'].split('/')[-2],x['source_max_bytes']) for x in stack])
