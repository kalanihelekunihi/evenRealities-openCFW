#!/usr/bin/env python3
"""Bind packet wrappers and repaired native call frames to both test scopes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-hw-twi-operations-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text());probe=json.loads((out/'composed-frame-probe.json').read_text())
 assert r['comparisons']==46080 and r['counts']==dict(read0=11520,read1=11520,write0=11520,write1=11520) and r['observation_counts']==dict(register_read=7680,register_write=6912,tx=768,wait=192) and r['trace_sha256']=='4da29bc35cb22586f1c9c801dccc81bcee3af9587dcbf6f9722e901bcc369996'
 for flag in ['actual_packet_wrappers','register_tx_wait_are_explicit_fixtures','packet_width_and_fullword_error_mapping_checked','one_byte_direct_write_and_control_flag_asymmetry_checked','saved_r2_r3_and_early_return_words_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution','bounded_composed_register_frame_addresses_verified']:assert r[flag]
 for flag in ['full_composed_private_frame_identity_verified','full_raw_abi_verified','cross_call_private_frame_history_verified','metadata_operation_abi_migrated','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['composed_comparisons']==probe['comparisons']==5760 and r['composed_trace_sha256']==probe['trace_sha256']=='b65a80927d4163bb43fcf7edcb6c39e33acc4c7c11ca1bbc04b81ab605ec62a3'
 assert probe['matched'] and probe['raw_sdk_buffer_addresses_and_bytes_checked'] and probe['no_pointer_normalization'] and probe['raw_r0_saved_words_callee_sp_nonstack_ram_match'] and probe['composed_object_sha256']==b['composed_object_sha256']==sha(out/'hw-operations-register-source.o')
 assert sha(ROOT/'r1/tools/verify_native_hw_twi_operations.py')==r['driver_sha256']==probe['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'hw-operations-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_hw_twi_operations_verification.ld')==r['layout_sha256'] and sha(out/'composed-frame-probe.json')==r['composed_probe_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-hw-twi-operations-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-hw-twi-operations-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==32
 assert undefined_symbols(out/'hw-operations-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(out/'hw-operations-register-source.o')[0]==b['composed_undefined_symbols']
 assert b['closed_parent_imports']==['r1_hw_twi0_read','r1_hw_twi0_write','r1_hw_twi1_read','r1_hw_twi1_write'] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('55414',52),('55448',52),('55ce0',112),('55d50',108)]:
  q=json.loads((BASE/'native-hw-twi-operations'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for p,h in json.loads((out/'superseded-evidence.json').read_text()).items():assert sha(out/p)==h,p
 old=out/'pre-native-call-frame-fix';oldr=json.loads((old/'runtime-report.json').read_text());oldv=json.loads((old/'verification.json').read_text());oldp=json.loads((old/'composed-frame-probe.json').read_text())
 assert not oldp['matched'] and oldp['native_tx_buffer']==0x2003efd4 and oldp['source_tx_buffer']==0x2003efbc and oldp['no_pointer_normalization']
 for name,key in [('hw-operations-source.o','graph_object_sha256'),('hw-operations-register-source.o','composed_object_sha256'),('native-hw-twi-operations-runtime.o','linked_sha256')]:assert sha(old/name)==oldr[key]
 assert oldv['driver_sha256']==sha(old/'verify_native_hw_twi_operations.py') and oldv['composed_probe_sha256']==sha(old/'composed-frame-probe.json') and oldv['trace_sha256']==r['trace_sha256']
 print('TWI operations:46080 isolated+5760 actual-register cases;native call frames repaired;32 imports;full history/SDK/ABI/image gates remain')
if __name__=='__main__':audit()
