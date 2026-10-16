#!/usr/bin/env python3
"""Authenticate GPIO lifecycle bodies/table without claiming peripheral boot."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-output-gpio-lifecycle-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 expected={'r1_output_gpio_task_initialize':7440,'r1_output_gpio_direct_initialize':7440,'r1_output_gpio_task_release':11856,'r1_output_gpio_direct_release':11856,'nrfx_gpiote_is_init':7440,'nrfx_gpiote_init':3840,'nrfx_gpiote_out_init':7440,'nrfx_gpiote_out_task_enable':7440,'nrfx_gpiote_out_task_disable':11856,'nrfx_gpiote_out_uninit':11856,'nrfx_gpiote_out_set':3824,'nrfx_gpiote_out_clear':3616,'r1_adc_error':7680,'compare':221184,'open_callback':4480,'close_callback':7424}
 assert r['comparisons']==31104 and r['counts']==dict(open=10368,close=10368,workflow=10368) and r['observation_counts']==expected and r['trace_sha256']=='478afff84d38597631079eb373cb2d4b013f859e6296d335d8d04ed3bc78e0b8'
 for flag in ['actual_four_helpers_strcmp_and_inline_hal','only_sdk_and_returning_error_logger_are_fixtures','callback_self_r0_order_and_fresh_close_target_checked','fresh_selector_pin_level_after_callbacks_checked','repeated_open_close_workflows_checked','raw_r0_callee_sp_nonstack_ram_mmio_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_raw_abi_verified','arbitrary_selector_targets_verified','cross_call_private_frame_history_verified','metadata_callback_abi_migrated','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['cold_lifecycle_table_bytes_pointer_normalized']==16
 assert sha(ROOT/'r1/tools/verify_native_output_gpio_lifecycle.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'output-lifecycle-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_output_gpio_lifecycle_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'strcmp-source.o')==b['strcmp_object_sha256'] and undefined_symbols(out/'strcmp-source.o')[0]==[]
 assert sha(out/'native-output-gpio-lifecycle-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-output-gpio-lifecycle-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==42
 assert undefined_symbols(out/'output-lifecycle-source.o')[0]==b['graph_undefined_symbols'] and b['closed_parent_imports']==['r1_output_gpio_close','r1_output_gpio_open'] and b['newly_exposed_imports']==[]
 assert not any(n.startswith('r1_output_gpio_') for n in b['undefined_symbols'])
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('54c58',100),('54d98',88),('54cbc',20),('54df0',46),('54f28',20),('54f48',66)]:
  q=json.loads((BASE/'native-output-gpio-lifecycle'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 print('GPIO lifecycle:31104 cases;six bodies+16-byte table;all GPIO imports source-linked;42 remaining;ABI/peripheral/image gates open')
if __name__=='__main__':audit()
