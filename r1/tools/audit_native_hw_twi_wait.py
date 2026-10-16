#!/usr/bin/env python3
"""Authenticate compiled TWI wait policy and retain timing/full-provider gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-hw-twi-wait-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==21984 and r['counts']==dict(matrix=16800,mutation=5184) and r['observation_counts']==dict(state=10784,freq=5696,acquire=5696,delay=531168,null_acquire=864) and r['trace_sha256']=='d52ce5fe50dea40c9ad5358efd6cc3400bb0103e9496478432921a1d542305d8'
 for flag in ['actual_wait_policy_and_canonical_clusters','only_cmsis_and_cycle_delay_are_fixtures','wrapping_tick_poll_arithmetic_and_minimum_tick_checked','bus_ready_flag_asymmetry_checked','fresh_semaphore_and_result_after_lower_calls_checked','polling_completion_and_timeout_edges_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['physical_wait_timing_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_hw_twi_wait.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'hw-wait-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_hw_twi_wait_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-hw-twi-wait-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-hw-twi-wait-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==36
 assert undefined_symbols(out/'hw-wait-source.o')[0]==b['graph_undefined_symbols'] and b['closed_parent_imports']==[] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('70820',108),('7088c',108)]:
  q=json.loads((BASE/'native-hw-twi-wait'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 print('TWI waits:21984 cases;wrapping arithmetic/minimum tick/poll and mutation checks;36 imports unchanged;transfer/timing/ABI/image gates open')
if __name__=='__main__':audit()
