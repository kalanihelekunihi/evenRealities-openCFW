#!/usr/bin/env python3
"""Bind native settings/KV/SVC contract separately from portable policy and hardware."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-system-settings'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-system-settings-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json');probe=read(rp.parent/'failed-read-frame-probe.json')
 assert r['comparisons']==21056 and r['counts']==dict(handler=10304,get=9216,set=1536) and r['observations_per_side']==119136 and r['trace_sha256']=='24a7106f799e16541bbb1b84e1363111b0d488ece691315039d1ba267c7ce220' and all(r['lower_observation_counts'].values())
 for flag in ['actual_handler_bit_helpers_kv_musl_accessor','svc_idle_transport_logging_critical_are_fixtures','handler_workflows_use_successful_cached_reads','direct_helper_failed_read_seed_views_checked','ack_before_accessor_and_raw_requested_comparison_checked','fresh_status_after_setter_and_svc_enum63_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','regulator_svc_or_persistence_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_system_settings.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'system-settings-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_system_settings_verification.ld')
 assert probe['matched'] and probe['comparisons']==192 and probe['trace_sha256']=='28e568be68253db4cab602d44d085c615f4199104a3b8dc4d14c72f89648be7b' and probe['bounded_failed_read_samples_only'] and not probe['cross_call_private_frame_history_verified'] and not probe['whole_image_complete'] and probe['driver_sha256']==sha(ROOT/'r1/tools/probe_native_system_settings_frame.py')
 for key in ['report_sha256','object_sha256','layout_sha256','application_sha256']:assert probe[key]==r[key]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-system-settings-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'settings-cached-owners-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==55 and undefined_symbols(rp.parent/'native-system-settings-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'system-settings-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'settings-cached-owners-source.o')[0]==[]
 parent=read(BASE/'native-touch-gesture-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_system_settings_plan_command'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 unit=read(OUT/'report.json');assert unit['sdk_svc_id']==63 and unit['sdk_archive_sha256']==sha(ROOT/'vendor-cache/r1/sdk.zip')=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 import zipfile
 with zipfile.ZipFile(ROOT/'vendor-cache/r1/sdk.zip') as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,h in unit['inputs'].items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('84524',260),('84628',8),('84630',37),('84658',31),('84678',51),('846ac',45),('73750',40),('73800',52)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a,n,end in [('84524',260,'84627'),('73750',36,'73773'),('73800',48,'7382f')]:
  q=read(OUT/f'rea-procedure-{a}.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x'+a and d['body']['total_bytes']==n and d['body']['ranges']==[dict(start='0x'+a,end='0x'+end)]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==3 and all(row in rows for row in e['new_ownership_rows']) and sum(int(row['size']) for row in e['new_ownership_rows'])==344
 from audit_source_frontier import section_bytes
 for section,a,n in [('get_ring',0x84630,37),('get_sdk',0x84658,31),('set_ring',0x84678,51),('set_sdk',0x846ac,45)]:assert section_bytes(OUT/'native_system_settings.o','.r1.settings.'+section,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['native_code_bytes']==344 and e['new_owned_text_bytes']==164 and e['separate_native_handler'] and e['raw_frame_helpers_no_defaults'] and e['sdk_svc_enum63'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['regulator_or_persistence_proven'] and not e['whole_image_identity']
 print('Native settings authenticated:21056 primary+192 failed-read probe;344 native+164 text bytes;actual KV/musl/accessor;55 imports;policy/private/persistence/SVC/image gates retained')
if __name__=='__main__':audit()
