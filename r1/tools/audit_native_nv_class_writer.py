#!/usr/bin/env python3
"""Bind class serializer/CRC, caller graph and still-failing raw-frame probe."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-class-writer'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-nv-class-writer-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==1696 and r['observations_per_side']==9186 and r['trace_sha256']=='dae17d35102f454a2b39209d0fc6b7e0751492f7a2a0075e822041615f85625d'
 for flag in ['actual_source_crc16','index14_mask_offset_and_flags_before_callback_checked','fresh_port_and_size_after_crc_checked','post_crc_mutations_are_explicit_fixtures','write_failure_does_not_restore_dirty_flag_checked','callback_fourth_word_is_loaded_target_checked','only_port_write_and_logging_are_fixtures','raw_r0_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_flash_or_commit_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nv_class_writer.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['writer_object_sha256']==sha(rp.parent/'nv-class-writer-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_nv_class_writer_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helper_object_sha256']==sha(rp.parent/'writer-helpers-source.o') and b['linked_sha256']==sha(rp.parent/'native-nv-class-writer-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==60 and undefined_symbols(rp.parent/'native-nv-class-writer-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'nv-class-writer-source.o')[0]==b['writer_undefined_symbols']==['nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 parent=read(BASE/'native-nv-update-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_store_class_record_write'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('91780',118),('917f8',4),('917fc',50),('91830',8),('91838',44)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-91780.json');q=q.get('structuredContent') or json.loads(next(x['text'] for x in q['content'] if x['type']=='text'));assert q['normalized_result']['body']['total_bytes']==118
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==118
 from audit_source_frontier import section_bytes
 for name,a,n in [('ring',0x917fc,50),('sdk',0x91838,44)]:assert section_bytes(OUT/'native_nv_class_writer.o','.r1.nv.class_writer.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 cr=rp.parent/'caller-graph-report.json';cb=read(cr);g=read(rp.parent/'caller-graph-verification.json');assert g['comparisons']==3660 and g['observations_per_side']==104532 and g['trace_sha256']=='39b1c24bf53a2512709cadaf0e23c4cc790f69378963377bcfedd1c5d09798e5'
 assert g['actual_record_frames_cached_read_write_musl_fill_copy_dirty_scan_writer_crc'] and g['only_response_port_write_logging_critical_and_final_request_are_fixtures'] and not g['cross_call_private_stack_history_verified'] and not g['whole_flash_commit_graph_executed'] and not g['whole_image_complete']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nv_writer_graph.py') and g['report_sha256']==sha(cr) and g['object_sha256']==cb['graph_object_sha256']==sha(rp.parent/'nv-writer-graph-source.o') and g['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_nv_writer_graph_verification.ld') and g['application_sha256']==r['application_sha256']
 for p,h in cb['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in cb[group].items():assert sha(BASE/p)==h,p
 assert len(cb['undefined_symbols'])==5 and undefined_symbols(rp.parent/'nv-writer-graph-source.o')[0]==cb['undefined_symbols']
 p=read(rp.parent/'failed-read-caller-graph-probe.json');assert p['driver_sha256']==sha(ROOT/'r1/tools/probe_native_nv_writer_frame.py') and p['report_sha256']==sha(cr) and p['object_sha256']==g['object_sha256'] and p['layout_sha256']==g['layout_sha256'] and p['application_sha256']==r['application_sha256'] and p['actual_source_writer_and_crc'] and p['failed_read_then_fresh_valid_handle'] and p['raw_r0_matches'] and not p['matched'] and not p['whole_image_complete']
 n,s=p['results'];assert n[0]==s[0] and n[1]!=s[1] and n[2]!=s[2] and e['failed_read_frame_mismatch_reproduced_with_actual_writer'] and e['new_owned_text_bytes']==94 and not e['whole_image_identity']
 print('NV class writer authenticated:1696 direct+3660 caller cases;118 native/94 text bytes;60 imports;actual-serialization frame counterexample remains OPEN')
if __name__=='__main__':audit()
