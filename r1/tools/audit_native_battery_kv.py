#!/usr/bin/env python3
"""Bind cold KV records, symbolic handles and existing provider selections."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-kv-runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=OUT/'report.json';b=read(rp)
 assert r['comparisons']==1200 and r['counts']==dict(byte=240,flag=240,signed=240,fields=480) and r['observations_per_side']==640 and r['trace_sha256']=='80eb48ea529813071b8ad02da9dda3facb73d199de97c2e618a978130235955b'
 for flag in ['source_cold_classes_and_symbolic_handles_match','actual_cached_read_write_and_musl_copy','only_critical_callbacks_are_fixtures','callback_mutations_handle_reload_and_input_aliases_checked','raw_getter_r0_r3_callee_sp_and_nonstack_ram_checked','void_setter_raw_return_not_compared','failed_size_preserves_external_raw_stack_view','no_native_candidate_execution']:assert r[flag]
 for flag in ['cross_call_private_stack_history_verified','whole_storage_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_kv.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['cached_object_sha256']==sha(OUT/'battery-kv-cached-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_battery_kv_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['config_object_sha256']==sha(OUT/'native_battery_kv_config.o') and b['readiness_object_sha256']==sha(OUT/'yhm-readiness-source.o') and b['helpers_object_sha256']==sha(OUT/'kv-cached-helpers-source.o') and b['linked_sha256']==sha(OUT/'native-battery-kv-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==69 and undefined_symbols(OUT/'native-battery-kv-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(OUT/'battery-kv-cached-source.o')[0]==b['cached_undefined_symbols']==[]
 parent=read(BASE/'native-battery-context-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_batcfg_record_kv_handle','r1_device_info_record_kv_handle','r1_yhm_ready_native','time_backend_timestamp_thunk'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('8ada4',10),('8adb0',4),('3541c',28)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 from audit_source_frontier import section_bytes
 obj=OUT/'native_battery_kv_config.o';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();rel=subprocess.check_output(['arm-none-eabi-readelf','-r',str(obj)],text=True);total=0
 for name,(a,n,sym) in e['classes'].items():assert section_bytes(obj,'.r1.battery.kv.'+name,executable=False)==cold[a-0x200064a8:a-0x200064a8+n];total+=n
 for name,(a,sym,target) in e['handles'].items():
  block=rel.split("Relocation section '.rel.r1.battery.kv."+name+".handle'",1)[1].split('Relocation section',1)[0];assert 'contains 1 entry' in block and 'R_ARM_ABS32' in block and target in block
  target_address=e['classes'][name][0];assert cold[a-0x200064a8:a-0x200064a8+4]==target_address.to_bytes(4,'little');total+=4
 linked=OUT/'native-battery-kv-runtime.o';syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(linked)],text=True).splitlines() if len(v:=line.split())==3};assert syms['time_backend_timestamp_thunk']==syms['r1_time_backend_timestamp'] and b['timestamp_alias']==e['timestamp_alias']
 assert total==e['new_owned_bytes']==112 and e['new_rows']==0 and e['timestamp_alias_not_new_body_or_row'] and not e['ghidra_mcp_gui_available'] and e['rea_headless_ghidra_bytes_authenticated'] and not e['cross_call_private_stack_history_verified'] and not e['whole_image_identity']
 print('Battery KV source authenticated:1200 cached workflows;112 owned bytes;4 imports closed/69 remain;private history/storage/ABI/image gates open')
if __name__=='__main__':audit()
