#!/usr/bin/env python3
"""Authenticate cold status ring ownership, raw return variant and role composition."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-status-ring'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-status-ring-runtime/report.json';b=read(rp)
 assert r['comparisons']==33578 and r['counts']==dict(publish=30234,device=256,peers=16,charge=3072) and r['observations_per_side']==165088 and r['trace_sha256']=='a67dc3227fc7b386b6c3b28f53885bcf8be8b81fc08698b7514baef04772be3b'
 for flag in ['actual_source_device_peer_charge_getters','raw_r0_callee_sp_and_observed_nonstack_ram_checked','provider_register_clobbers_checked','captured_metadata_before_timestamp_critical_callbacks_checked','ring_drop_wrap_and_out_of_range_write_observed','only_configuration_battery_update_timestamp_critical_event_are_fixtures','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_battery_event_or_rtos_graph_executed','private_stack_identity_verified','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_status_ring.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['status_object_sha256']==sha(rp.parent/'status-ring-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_status_ring_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helper_object_sha256']==sha(rp.parent/'status-fields-source.o') and b['linked_sha256']==sha(rp.parent/'native-status-ring-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==70 and undefined_symbols(rp.parent/'native-status-ring-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'status-ring-source.o')[0]==b['status_undefined_symbols'] and len(b['status_undefined_symbols'])==6
 parent=read(BASE/'native-phone-role-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_charge_state_byte_get','r1_status_record_ring_publish'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_battery_runtime_update_service']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in e['byte_read_sizes'].items():
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['new_rows']==0 and len(e['existing_rows_not_new'])==4 and all(x in rows for x in e['existing_rows_not_new'])
 from audit_source_frontier import section_bytes
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();obj=OUT/'native_status_ring.o';total=0;z,nz=e['zero_scatter_span']
 for name,(a,n) in e['owned_cells'].items():
  data=section_bytes(obj,'.r1.status.'+name,executable=False);assert data==bytes(n);total+=n
  if a<0x20007e04:assert data==cold[a-0x200064a8:a-0x200064a8+n]
  else:assert z<=a and a+n<=z+nz
 assert total==e['new_owned_bytes']==134 and e['old_void_variant_preserved'] and e['raw_event_return_variant'] and e['legacy_void_declarations_gate'] and not e['whole_image_identity']
 cr=rp.parent/'role-graph-report.json';cb=read(cr);g=read(rp.parent/'role-graph-verification.json')
 assert g['comparisons']==4800 and g['fatal_boundary_cases']==472 and g['observations_per_side']==41284 and g['trace_sha256']=='938f17ad2f277bbde059e03863bd39d710560d712179cce2ccf2d846eb327f32'
 assert g['actual_source_status_ring_and_getters'] and g['only_logging_delay_battery_configuration_time_critical_event_and_terminal_are_fixtures'] and g['terminal_paths_stop_before_native_stack_blx'] and not g['fatal_transfer_implemented'] and not g['whole_battery_event_rtos_or_logging_graph_executed'] and not g['whole_image_complete']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_role_status_graph.py') and g['runtime_report_sha256']==sha(cr) and g['object_sha256']==cb['graph_object_sha256']==sha(rp.parent/'role-status-graph-source.o') and g['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_role_status_graph_verification.ld') and g['application_sha256']==r['application_sha256']
 for p,h in cb['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in cb[group].items():assert sha(BASE/p)==h,p
 assert len(cb['undefined_symbols'])==14 and undefined_symbols(rp.parent/'role-status-graph-source.o')[0]==cb['undefined_symbols'] and 'r1_phone_role_assertion_stack_transfer' in cb['undefined_symbols']
 print('Status ring authenticated:33578 cases;134 owned bytes;0 new rows;70 imports;ABI/private frame/battery alias/image gates remain')
if __name__=='__main__':audit()
