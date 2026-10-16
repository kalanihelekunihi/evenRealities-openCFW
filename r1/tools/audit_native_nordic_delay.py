#!/usr/bin/env python3
"""Authenticate pinned Nordic loop, cycle contract and actual filter consumer."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nordic-delay-runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=OUT/'report.json';b=read(rp)
 assert r['comparisons']==117 and r['counts']==dict(fixture=72,actual=27,prefix=18) and r['requests_per_side']==13797 and r['cycle_instruction_steps_per_side']==1165833 and r['trace_sha256']=='de42f4621d8c87cdfde89dc542c1b5f2baee16480132521486f0b6683fa129ed'
 for flag in ['sdk_loop_unchanged','cycle_primitive_body_matches_all_used_native_clones','actual_cycle_tier_present','large_values_only_three_request_prefix_checked','callee_sp_and_nonstack_ram_checked_on_return','void_raw_r0_r3_and_apsr_not_compared','no_native_candidate_execution']:assert r[flag]
 for flag in ['hardware_elapsed_time_verified','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nordic_delay.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['delay_object_sha256']==sha(OUT/'nordic-delay-source.o')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['primitive_object_sha256']==sha(OUT/'delay-primitive-source.o') and b['linked_sha256']==sha(OUT/'native-nordic-delay-runtime.o') and b['unchanged_sdk_delay_header'] and b['cycle_conversion']==64
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==68 and undefined_symbols(OUT/'native-nordic-delay-runtime.o')[0]==b['undefined_symbols'] and not undefined_symbols(OUT/'nordic-delay-source.o')[0]
 parent=read(BASE/'native-battery-kv-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['nrf_delay_ms'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 assert e['inputs']['vendor-cache/r1/sdk.zip']=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for p in OUT.glob('rea-bytes-*.json'):
  q=read(p)['structuredContent'];d=q['normalized_result'];a=int(d['address'],16);n=d['requested_bytes']
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[a-0x27000:a-0x27000+n]
 ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=list(csv.DictReader(ownership.open()));assert sha(ownership)==r['ownership_sha256'] and len(e['ownership_rows'])==9 and all(x in rows for x in e['ownership_rows']) and r['clone_entries']==[x['entry'] for x in e['ownership_rows']] and sum(int(x['size']) for x in e['ownership_rows'])==e['native_outer_bytes']==246
 f=read(OUT/'filter-verification.json');assert f['comparisons']==7104 and f['adc_reads']==35520 and f['busy_delays']==15984 and f['rtos_delays']==19536 and f['trace_sha256']=='1197bafc474bb069e6f4f660d220f648a8ec3a0e791e4993147148a9479690bb' and f['actual_sdk_millisecond_loop'] and f['cycle_primitive_is_fixture_here']
 assert f['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nordic_delay_filter.py') and f['delay_report_sha256']==sha(rp) and f['delay_object_sha256']==r['object_sha256'] and f['report_sha256']==sha(BASE/'native-battery-filter/report.json') and f['object_sha256']==sha(BASE/'native-battery-filter/native_battery_filter.o') and f['application_sha256']==r['application_sha256']
 for p,h in f['evidence'].items():assert sha(OUT/p)==h,p
 assert e['new_owned_data_bytes']==0 and e['primitive_reused_not_new_rows'] and not e['duplicate_final_placement_verified'] and not e['hardware_elapsed_time_verified'] and not e['whole_image_identity']
 print('Nordic SDK delay authenticated:9 rows/246 bytes;117 direct +7104 filter cases;68 imports;timing/raw ABI/duplicate placement/image gates open')
if __name__=='__main__':audit()
