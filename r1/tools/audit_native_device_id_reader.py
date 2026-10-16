#!/usr/bin/env python3
"""Bind native reader, SDK SVC, complete formatter and source cache fields."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-id-reader'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-device-id-reader-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==3616 and r['counts']==dict(cached=3072,svc=288,random=256) and r['observations_per_side']==1088 and r['trace_sha256']=='b125bdd463f45f2e8ec499fefb133710746d1a5825aa2dff84e0f2ef23ed2144'
 for flag in ['actual_musl_copy_complete_formatter_and_existing_sdk_svc_wrapper','svc109_and_ficr_are_controlled_fixtures','all_cached_byte_lengths_checked_in_mapped_backing','partial_svc_writes_retain_saved_seed_words','raw_r0_r1_r2_r3_callee_sp_nonstack_ram_and_output_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['runtime_admission_changed','hardware_write_executed','hardware_identity_or_svc_success_proven','cache_capacity_or_overlap_safety_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_device_id_reader.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'device-id-reader-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_device_id_reader_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-device-id-reader-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'reader-helpers-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==57 and undefined_symbols(rp.parent/'native-device-id-reader-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'device-id-reader-source.o')[0]==b['graph_undefined_symbols']==[] and undefined_symbols(rp.parent/'reader-helpers-source.o')[0]==[]
 parent=read(BASE/'native-device-id-command-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_native_device_id_read_boundary','snprintf'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 old=rp.parent/'pre-formatter-table-map-fix'
 for p,h in e['superseded_table_mapping_probe'].items():assert sha(old/p)==h,p
 fail=read(old/'counterexample.json');assert fail['case'][0]=='svc' and fail['outputs'][0][0]==fail['outputs'][1][0] and fail['outputs'][0][1]==fail['outputs'][1][1] and fail['outputs'][0][3]!=fail['outputs'][1][3]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('6ab88',58),('6abc4',20),('c0648',25)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-procedure.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x6ab88' and d['body']['total_bytes']==58 and d['body']['ranges']==[dict(start='0x6ab88',end='0x6abc1')]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==58
 from audit_source_frontier import section_bytes
 for name,a,n in [('format',0x6abc8,13),('cache.text',0xc0648,25)]:
  section='.r1.device.id.'+name;assert section_bytes(OUT/'native_device_id_reader.o',section,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
 for name,a,n in [('cache.valid',0x20006da4,1),('cache.length',0x20006e3c,1)]:assert section_bytes(OUT/'native_device_id_reader.o','.r1.device.id.'+name,executable=False)==cold[a-0x200064a8:a-0x200064a8+n]
 assert e['native_code_bytes']==58 and e['new_owned_bytes']==44 and e['existing_nordic_sdk_svc_wrapper_reused'] and e['complete_formatter_linked'] and e['parent_integer_owner_reused'] and e['cold_cache_pointer_symbolic'] and e['unchecked_cache_byte_length_preserved'] and not e['runtime_admission_changed'] and not e['hardware_identity_proven'] and not e['whole_image_identity']
 print('Native identity reader authenticated:3616 cases;58 native+44 source-owned bytes;actual copy/formatter/SDK SVC wrapper;57 imports;hardware/capacity/context/private/image gates retained')
if __name__=='__main__':audit()
