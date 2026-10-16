#!/usr/bin/env python3
"""Authenticate response composition and source body variants with canonical storage."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-response-graph-runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def body_view(obj,section):
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'section.bin';subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(obj),str(p)],check=True);data=p.read_bytes()
 raw=subprocess.check_output(['arm-none-eabi-readelf','-rW',str(obj)],text=True);block=raw.split("Relocation section '.rel"+section+"'",1)[1].split('Relocation section',1)[0]
 rel=[(x[0],x[2],*x[4:]) for line in block.splitlines() if len(x:=line.split())>=5 and re.fullmatch('[0-9a-fA-F]{8}',x[0])]
 return data,rel

def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=OUT/'report.json';b=read(rp)
 assert r['comparisons']==3240 and r['counts']==dict(response=1080,header=1080,phone=1080) and r['observations_per_side']==8875 and r['trace_sha256']=='4ee91cea732c044fa2edcf3ee6af7921c9f086d916c9459c7c628e7949ffded4'
 for flag in ['actual_response_header_phone_encoder_gates_crc_memory_hook','only_allocator_logging_and_lower_callback_are_fixtures','raw_r0_callee_sp_and_observed_nonstack_ram_checked','private_header_pointer_not_compared','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_allocator_ble_or_rtos_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_response_graph.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(OUT/'response-graph-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_response_graph_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helpers_object_sha256']==sha(OUT/'response-helpers-source.o') and b['linked_sha256']==sha(OUT/'native-response-graph-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==65 and undefined_symbols(OUT/'native-response-graph-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(OUT/'response-graph-source.o')[0]==b['graph_undefined_symbols']==['nrf_log_frontend_std_1','nrf_log_frontend_std_2','nrf_log_frontend_std_4','pvPortMalloc','r1_structured_log_format','r1_structured_log_mode_get','vPortFree']
 parent=read(BASE/'native-nordic-delay-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_phone_cmd_send_op1','r1_protocol_response_send_0x100','r1_protocol_send_response'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('828b4',364),('83896',36),('84c0c',82),('82f9c',136),('827f8',14)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 original=(ROOT/'r1/components/board/native_protocol_encoder.c').read_text();expected=original.replace('volatile uint16_t r1_protocol_sequence __attribute__((section(".r1.protocol.sequence")))=0;','extern volatile uint16_t r1_protocol_sequence;').replace('volatile uint8_t r1_protocol_version_map[4] __attribute__((section(".r1.protocol.version_map")))={0,100,100,100};','extern volatile uint8_t r1_protocol_version_map[4];');assert expected==(ROOT/'r1/components/runtime/native_protocol_encoder_body.c').read_text()
 original=(ROOT/'r1/components/board/native_protocol_send_hook.c').read_text();assert original.replace('volatile uintptr_t r1_protocol_send_hook\n    __attribute__((section(".r1.protocol.send_hook"))) = 0;','extern volatile uintptr_t r1_protocol_send_hook;')==(ROOT/'r1/components/runtime/native_protocol_send_hook_body.c').read_text()
 for orig,new,fn in [('native-protocol-encoder/native_protocol_encoder.o','native_protocol_encoder_body.o','r1_model_encode'),('native-protocol-send-hook/native_protocol_send_hook.o','native_protocol_send_hook_body.o','r1_protocol_send_hook_call')]:assert body_view(BASE/orig,'.text.'+fn)==body_view(OUT/new,'.text.'+fn)
 from audit_source_frontier import section_bytes
 assert section_bytes(OUT/'version-map-source.o','.r1.protocol.version_map',executable=False)==bytes([0,100,100,100])
 for obj in ['native_protocol_encoder_body.o','native_protocol_send_hook_body.o']:
  u,d=undefined_symbols(OUT/obj);assert not {'r1_protocol_sequence','r1_protocol_version_map','r1_protocol_send_hook'}&set(d)
 assert e['new_rows']==0 and e['new_owned_data_bytes']==0 and e['single_sequence_version_hook_owner'] and not e['private_stack_history_verified'] and not e['whole_image_identity']
 print('Response graph authenticated:3240 cases;encoder/hook compiled bodies+relocations preserved;3 imports closed/65 remain;allocator/BLE/ABI/image gates open')
if __name__=='__main__':audit()
