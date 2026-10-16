#!/usr/bin/env python3
"""Authenticate device ID command while retaining native identity-provider gate."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-id-command'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-device-id-command-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==2192 and r['counts']==dict(command=960,workflow=576,op11=144,status=256,clear=256) and r['observations_per_side']==14136 and r['trace_sha256']=='cb6512e7341170d9f6e0f7c86d123c71ca67140df5a04e248d934cf0a0a86ee7'
 for flag in ['actual_status_accessors_op11_phone_getter_and_musl_memory','id_read_response_and_logging_are_fixtures','one_shot_two_call_workflow_checked','provider_writes_limited_to_mapped_28byte_fixture','raw_r0_r2_r3_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution','status_alias_to_eventual_context_required']:assert r[flag]
 for flag in ['native_cached_svc_identity_provider_implemented','hardware_write_executed','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_device_id_command.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'device-id-command-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_device_id_command_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-device-id-command-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'device-id-command-helpers-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==59 and undefined_symbols(rp.parent/'native-device-id-command-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'device-id-command-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'device-id-command-helpers-source.o')[0]==[]
 parent=read(BASE/'native-power-command-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_protocol_command_00083e50'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_native_device_id_read_boundary']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 old=rp.parent/'pre-clear-scratch-fix'
 for p,h in e['superseded_failed_candidate'].items():assert sha(old/p)==h,p
 fail=read(old/'counterexample.json');assert fail['case'][0]=='clear' and fail['outputs'][0][0][0]==[0,0x55667788,0x99aabbcc] and fail['outputs'][1][0][0]==[0,0,0x99aabbcc] and fail['outputs'][0][2]==fail['outputs'][1][2]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n,suffix in [('83e50',156,''),('83eec',4,''),('83ef0',21,''),('83f08',8,''),('83f10',15,''),('9a56c',28,''),('838ba',36,''),('6aadc',12,''),('6abd8',12,''),('6ab88',58,''),('83ef0',23,'-full'),('83f10',17,'-full')]:
  q=read(OUT/f'rea-bytes-{a}{suffix}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure-83e50.json')) and e['metadata_gap_for_command']
 q=read(OUT/'rea-procedure-838ba.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x838ba' and d['body']['total_bytes']==36 and d['body']['ranges']==[dict(start='0x838ba',end='0x838dd')]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==36
 from audit_source_frontier import section_bytes
 for name,a,n in [('default',0x9a56c,28),('ring',0x83ef0,23),('sdk',0x83f10,17)]:assert section_bytes(OUT/'native_device_id_command.o','.r1.device.id.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert section_bytes(OUT/'native_device_id_command.o','.r1.device.id.status',executable=False)==cold[0x20006da5-0x200064a8:0x20006da6-0x200064a8]==b'\0'
 assert e['native_code_bytes']==206 and e['new_owned_bytes']==69 and e['raw_id_provider_unresolved'] and e['bounded_frozen_helper_not_substituted'] and e['status_byte_requires_eventual_context_alias'] and not e['private_frame_history_verified'] and not e['whole_image_identity']
 print('Device ID command authenticated:2192 cases;156 supplemental+14 status+36 locked bytes;69 owned bytes;59 imports;identity/SVC/cache/context/private/image gates retained')
if __name__=='__main__':audit()
