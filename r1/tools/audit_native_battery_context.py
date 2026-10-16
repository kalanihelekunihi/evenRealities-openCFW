#!/usr/bin/env python3
"""Bind shared battery context ownership and registered source dependencies."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-context-runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=OUT/'report.json';b=read(rp)
 assert r['comparisons']==2920 and r['cold_context_cases']==24 and r['explicit_numeric_rounding_cases']==336 and r['trace_sha256']=='a807add726944a347ef36415b876ce2efddefb242bf797b4fdfd8d36eef982e5'
 for flag in ['real_statistics','real_control','source_owned_cold_contexts_match','existing_status_and_adc_aliases_preserved','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_raw_abi_verified','whole_battery_hardware_graph_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 for group,n in [('executed_statistics_entry_counts',3),('executed_control_entry_counts',4)]:assert r[group]['native']==r[group]['source'] and len(r[group]['source'])==n and all(x>0 for x in r[group]['source'].values())
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_context.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['control_object_sha256']==sha(OUT/'battery-control-context-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_battery_context_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['config_object_sha256']==sha(OUT/'native_battery_context_config.o') and b['existing_owners_sha256']==sha(OUT/'context-existing-owners.o') and b['linked_sha256']==sha(OUT/'native-battery-context-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==73 and undefined_symbols(OUT/'native-battery-context-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(OUT/'battery-control-context-source.o')[0]==b['control_undefined_symbols']
 parent=read(BASE/'native-status-ring-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_battery_runtime_update_service','r1_native_charger_state_get'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['nrf_delay_ms','r1_batcfg_record_kv_handle','r1_device_info_record_kv_handle','r1_yhm_ready_native','time_backend_timestamp_thunk']
 tick=OUT/'cmsis-tick-frequency-source.o';assert sha(tick)==b['cmsis_tick_frequency_object_sha256'] and not undefined_symbols(tick)[0] and 'osKernelGetTickFreq' in undefined_symbols(tick)[1]
 tr=read(BASE/'rtos-ticks/report.json');tu=next(x for x in tr['units'] if 'osKernelGetTickFreq' in x['defined']);assert b['cmsis_input_object_sha256']==tu['object_sha256']==sha(Path(tu['command'][-1]))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('31fd0',406),('32168',16)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 from audit_source_frontier import section_bytes
 assert 0x20007e04<=0x20016b84 and 0x20016b84+68<=0x20007e04+0x340b4
 obj=OUT/'native-battery-context-runtime.o';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert section_bytes(obj,'.r1.battery.device',executable=False)==bytes(68) and section_bytes(obj,'.r1.battery.runtime',executable=False)==cold[0x20006890-0x200064a8:0x20006890-0x200064a8+92]
 for name,(a,n) in e['owned_cells'].items():assert section_bytes(obj,'.r1.battery.'+name,executable=False)==cold[a-0x200064a8:a-0x200064a8+n]==bytes(n)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(obj)],text=True).splitlines() if len(v:=line.split())==3}
 for alias,(base,offset) in e['aliases'].items():assert syms[alias]-syms[base]==offset
 assert e['new_rows']==0 and e['new_owned_bytes']==166 and e['reused_bytes']==6 and e['previous_status_battery_alias_gate_closed_for_this_composition'] and not e['whole_battery_graph_executed'] and not e['whole_image_identity']
 for folder in ['initial-provider-frontier','pre-cmsis-frequency-provider']:
  history=OUT/folder
  for p,h in read(history/'manifest.json')['files'].items():assert sha(history/p)==h,p
 print('Battery shared context authenticated:2920 cases/24 cold;166 new +6 reused bytes;CMSIS frequency source;73 imports;whole hardware/ABI/image gates open')
if __name__=='__main__':audit()
