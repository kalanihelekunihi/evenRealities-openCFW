#!/usr/bin/env python3
"""Bind tested operations to source and authenticated native slices."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-output-gpio-operations-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==11936 and r['counts']==dict(config=864,read=6912,toggle=4160) and r['strcmp_calls_per_side']==29256 and r['trace_sha256']=='b5a4225db7b06adf28ac55f97dbe6eca5858717a9889a73d7dbe9c2bd99c357a'
 for flag in ['actual_strcmp_and_upstream_port_decoder','canonical_configuration_pointer_normalized','config_overlap_and_fresh_lookup_name_checked','saved_r3_read_toggle_and_raw_r0_checked','callee_sp_nonstack_ram_mmio_registers_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['mmio_write_one_hardware_semantics_modeled','full_raw_abi_verified','cross_call_private_frame_history_verified','metadata_callback_abi_migrated','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_output_gpio_operations.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'output-operations-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_output_gpio_operations_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-output-gpio-operations-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-output-gpio-operations-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==45
 assert undefined_symbols(out/'output-operations-source.o')[0]==b['graph_undefined_symbols']==['r1_output_gpio_close','r1_output_gpio_open','r1_output_gpio_slot18']
 assert b['closed_parent_imports']==['r1_output_gpio_driver14','r1_output_gpio_slot10','r1_output_gpio_slot1c'] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('54cd0',80),('54e20',88),('54ea8',38),('79288',28)]:
  q=json.loads((BASE/'native-output-gpio-operations'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 print('GPIO operations:11936 cases;actual strcmp/Nordic decoder;45 imports;ABI/MMIO hardware/image gates remain')
if __name__=='__main__':audit()
