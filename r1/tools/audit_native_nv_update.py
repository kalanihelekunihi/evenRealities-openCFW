#!/usr/bin/env python3
"""Authenticate NV update candidates and preserve failed-read frame counterexample."""
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-update'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-nv-update-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==3660 and r['counts']==dict(scan=720,idle=720,bit=600,peer=270,command=1350) and r['observations_per_side']==64576 and r['trace_sha256']=='efbb65435d8f6f7da2e8dcddf591644e689d0fecc8cfe3e1a7de8f266d9763fc'
 for flag in ['source_cold_classes_and_symbolic_table_match','actual_record_frames_cached_read_write_musl_fill_copy_and_dirty_scan','only_response_store_logging_critical_and_final_request_are_fixtures','raw_r0_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['cross_call_private_stack_history_verified','whole_flash_commit_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nv_update.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'nv-update-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_nv_update_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 for p,h in b['helpers'].items():assert sha(rp.parent/p)==h,p
 assert b['config_object_sha256']==sha(rp.parent/'native_nv_table_config.o') and b['cached_owners_sha256']==sha(rp.parent/'nv-cached-owners-source.o') and b['linked_sha256']==sha(rp.parent/'native-nv-update-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==61 and undefined_symbols(rp.parent/'native-nv-update-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'nv-update-source.o')[0]==b['graph_undefined_symbols']==['nrf_log_frontend_std_2','r1_protocol_send_response','r1_store_class_record_write','r1_structured_log_format','r1_structured_log_mode_get']
 parent=read(BASE/'native-system-event-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_health_record_kv_handle','r1_protocol_command_000844b0'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_store_class_record_write']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 assert sha(OUT/'supplemental-pseudocode.txt')==e['supplemental_pseudocode_sha256']
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('734e8',144),('73578',8),('73580',43),('735b4',37),('735dc',4),('73688',12),('73834',48),('73864',4),('738a8',68),('738ec',8),('844b0',60)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a,n in [('734e8',144),('73688',12),('73834',48)]:assert read(OUT/f'rea-{a}.json')['structuredContent']['normalized_result']['body']['total_bytes']==n
 for a in e['rea_procedure_gaps']:assert 'No procedure exists' in str(read(OUT/f'rea-{a}.json'))
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==4 and all(x in rows for x in e['new_ownership_rows']) and sum(int(x['size']) for x in e['new_ownership_rows'])==e['locked_native_bytes']==272 and not any(x['entry']=='0x000844b0' for x in rows)
 from audit_source_frontier import section_bytes
 cfg=rp.parent/'native_nv_table_config.o';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();total=16
 for name,(a,n) in e['new_classes'].items():assert section_bytes(cfg,'.r1.nv.class.'+name,executable=False)==cold[a-0x200064a8:a-0x200064a8+n];total+=n
 for name,a,n in [('ring',0x73580,43),('sdk',0x735b4,37)]:assert section_bytes(OUT/'native_nv_update.o','.r1.nv.sync.'+name,executable=False)==raw[a-0x27000:a-0x27000+n];total+=n
 assert total==e['new_owned_bytes']==324 and e['reused_handle_bytes']==12 and e['canonical_handle_span']==[0x20007de8,0x20007e04]
 rel=subprocess.check_output(['arm-none-eabi-readelf','-rW',str(rp.parent/'native-nv-update-runtime.o')],text=True);block=rel.split("Relocation section '.rel.r1.nv.handles'",1)[1].split('Relocation section',1)[0];assert 'contains 7 entries' in block and block.count('R_ARM_ABS32')==7
 p=read(rp.parent/'failed-read-frame-probe.json');assert p['driver_sha256']==sha(ROOT/'r1/tools/probe_native_nv_update_frame.py') and p['report_sha256']==sha(rp) and p['object_sha256']==r['object_sha256'] and p['layout_sha256']==r['layout_sha256'] and p['application_sha256']==r['application_sha256'] and p['failed_read_then_fresh_valid_handle'] and p['raw_r0_matches'] and not p['matched'] and not p['whole_image_complete']
 n,s=p['results'];assert n[0]==s[0] and n[1]!=s[1] and n[2]!=s[2] and e['failed_read_fresh_handle_private_frame_mismatch'] and not e['whole_image_identity']
 print('NV update bounded contracts:3660 cases;4 rows/272 bytes+60 supplemental;324 owned bytes;61 imports;failed-read frame mismatch explicitly OPEN')
if __name__=='__main__':audit()
