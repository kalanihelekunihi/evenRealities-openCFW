#!/usr/bin/env python3
"""Bind ST source attribution, scratch ABI and composed native FIFO evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-lis-fifo-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text());unit=BASE/'native-lis-fifo';u=json.loads((unit/'report.json').read_text())
 assert r['comparisons']==12652 and r['counts']==dict(proxy=300,level=1696,burst=288,fifo=5184,normalized=5184) and r['observation_counts']==dict(read=18118,acquire=1728,release=1728) and r['matching_faults']==1254 and r['trace_sha256']=='c24624b34d55085ea5250d1e58e61071ea228d9b081c89aca80c264a864c22ae'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'lis-fifo-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_fifo.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=unit/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_four_entries_attributed_st_kernel_and_composed_normalizer','only_register_callback_and_bus_operations_are_fixtures','exact_register_scratch_pointer_length_status_and_saved_r3_checked','raw_r0_callee_sp_context_and_buffer_ram_checked']:assert r[flag]
 for flag in ['full_context_size_proven','full_private_frame_history_verified','full_raw_abi_verified','real_context_initialization_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert r['source_zero_context_prefix_bytes']==16 and allocated_sections(unit/'native_lis_fifo.o')['.bss.r1.lis.context']==[8,3,16,4,hashlib.sha256(b'').hexdigest()] and 0x20007e04<=0x2001e4d8<0x2001e4e8<=0x20007e04+0x340b4
 assert u['upstream_component']=='st-lis2dw12-pid' and u['upstream_pin']=='8d4bd522015004a9646102702901ba5a15ec6d39' and u['upstream_license']=='BSD-3-Clause' and not u['exact_vendor_checkout_proven'] and not u['unmodified_upstream_body'] and not u['full_context_size_proven'] and u['context_prefix_bytes']==16
 vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+u['upstream_pin']);original=(vendor/'lis2dw12_reg.c').read_bytes();assert hashlib.sha256(original[u['source_slice_start']:u['source_slice_end']]).hexdigest()==u['original_slice_sha256']=='d05357f12368232f327371eaf4d8e9dd562108801c4f127fd51d0f618ced74ff'
 generated=(unit/'st-level-frame.c').read_text();assert (vendor/'LICENSE').read_text() in generated and 'r1_lis_fifo_level_body' in generated and 'reg->diff' in generated and len(u['adaptations'])==3
 for row in u['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(unit/Path(row['command'][-1]).name)==row['object_sha256']
 assert sha(unit/'native-lis-fifo.o')==u['linked_sha256'] and undefined_symbols(unit/'native-lis-fifo.o')[0]==u['undefined_symbols']==[]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-lis-fifo-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==30 and undefined_symbols(out/'lis-fifo-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_lis2dw12_fifo_read'] and b['newly_exposed_imports']==[]
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('LIS FIFO:12652 cases; attributed ST algorithm and native scratch contracts authenticated')
if __name__=='__main__':audit()
