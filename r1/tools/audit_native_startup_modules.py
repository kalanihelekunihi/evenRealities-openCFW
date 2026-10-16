#!/usr/bin/env python3
"""Audit reused constructor spans, peripheral dispatch and compiled provider integration."""
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();boot=BASE/'native-boot-ctors';peripheral=BASE/'native-peripheral-module';b=read(boot/'verification.json');p=read(peripheral/'verification.json');be=read(boot/'evidence.json');pe=read(peripheral/'evidence.json');brp=BASE/'native-initcalls/report.json';br=read(brp);prp=peripheral/'report.json';pr=read(prp)
 assert sha(app)==b['application_sha256']==p['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert b['comparisons']==54 and b['null_target_fault_comparisons']==12 and b['callbacks_per_implementation']==540 and b['trace_sha256']=='02025b598cc8a845009a75fc3afc85c56c5f39ff9288b91a1b38b120599c8344' and b['boot_combined_noncontiguous_body_bytes']==40 and b['boot_wrapper_bytes']==18 and b['post_init_shared_tail_bytes']==22 and b['registrar_bodies_are_fixtures'] and b['independent_calls_reset_xpsr'] and not b['instruction_identity']
 assert b['driver_sha256']==sha(ROOT/'r1/tools/verify_native_boot_ctors.py') and b['report_sha256']==sha(brp) and b['object_sha256']==sha(brp.parent/'initcalls.o')==br['selected_object_sha256']
 assert p['comparisons']==270 and p['callback_observations_per_side']==2700 and p['trace_sha256']=='7f834f26f400220d1a488838c547782a92599868392bd76dbf394bcb38a65e40'
 assert p['driver_sha256']==sha(ROOT/'r1/tools/verify_native_peripheral_module.py') and p['report_sha256']==sha(prp) and p['object_sha256']==sha(peripheral/'native_peripheral_module.o')==pr['units'][0]['object_sha256'] and p['layout_sha256']==sha(ROOT/p['layout'])
 assert p['callback_bodies_are_named_fixtures'] and p['typed_callback_order_primask_return_r0_stack_callee_integer_and_nonstack_ram_checked'] and not p['provider_bodies_integrated'] and not p['runtime_no_unresolved'] and not p['instruction_identity']
 for data in [br,pr]:
  for path,h in data['inputs'].items():assert sha(ROOT/path)==h,path
 for out,e in [(boot,be),(peripheral,pe)]:
  for group in ['ghidra','rea']:
   for path,h in e[group].items():assert sha(out/path)==h,path
  assert not e['locked_ownership_changed'] and e['provider_bodies_are_fixtures'] and not e['full_linked_graph_execution_verified'] and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
 for out,a,n in [(boot,0x4e1e4,18),(boot,0x5cb4c,22),(boot,0x4e1f8,32),(peripheral,0x50384,46)]:assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a,n in [(0x5cb4c,22),(0x4e1f8,32)]:
  evidence=read(boot/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'));assert evidence['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and evidence['normalized_result']['body']['total_bytes']==n
 for out,a in [(boot,0x4e1e4),(peripheral,0x50384)]:
  evidence=read(out/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'));assert evidence['error']['code']=='invalid_request' and 'No procedure exists' in str(evidence)
 assert be['combined_body_bytes']==40 and be['body_ranges']==[{'start':'0x4e1e4','end':'0x4e1f5','bytes':18},{'start':'0x5cb4c','end':'0x5cb61','bytes':22}] and be['boundary_gate_resolved_for_source_route'] and not be['raw_abi_and_instruction_gate_closed']
 assert be['locked_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0004e1e4') and be['locked_row']['size']=='40' and be['locked_row']['end']=='0x0005cb61'
 assert be['source_sha256']==sha(ROOT/be['reused_source']) and be['prior_evidence_sha256']==sha(BASE/'native-initcalls/evidence.json') and be['prior_verification_sha256']==sha(BASE/'native-initcalls/verification.json')
 assert raw[0x4e1e6-0x27000:0x4e1e8-0x27000]==bytes.fromhex('72b6') and raw[0x4e1ec-0x27000:0x4e1ee-0x27000]==bytes.fromhex('62b6')
 assert pe['native_body_bytes']==46 and pe['ordered_provider_calls']==10
 rp=BASE/'native-startup-providers/report.json';r=read(rp);assert r['linked_sha256']==sha(rp.parent/'native-startup-providers.o') and r['source_aliases']=={'r1_boot_ctor_run':'r1_native_boot_initcall_dispatch'} and len(r['application_imports_resolved'])==9 and r['remaining_application_imports']==['ble_dfu_buttonless_async_svci_init','cm_backtrace_init','r1_device_module_init','r1_reset_reason_nordic_adapter'] and len(r['undefined_symbols'])==67 and not r['full_provider_execution_verified'] and not r['application_linked'] and not r['original_instruction_identity']
 for path,h in r['inputs'].items():assert sha(ROOT/path)==h,path
 for group in ['provider_reports','objects']:
  for path,h in r[group].items():assert sha(BASE/path)==h,path
 assert set(r['application_imports_resolved'])=={'nrf_drv_clock_init','nrf_log_default_backends_init','nrf_log_frontend_std_0','nrf_log_init','r1_adc_error','r1_boot_ctor_run','r1_peripheral_module_init','r1_structured_log_format','r1_structured_log_mode_get'}
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'native-startup-providers.o')[0]==r['undefined_symbols']
 symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(rp.parent/'native-startup-providers.o')],text=True).splitlines() if len(v:=line.split())==3};assert symbols['r1_boot_ctor_run']==symbols['r1_native_boot_initcall_dispatch']
 print('Constructor40-byte noncontiguous source route and peripheral46-byte dispatcher authenticated; nine app imports source-linked, four direct and67 total imports remain')
if __name__=='__main__':audit()
