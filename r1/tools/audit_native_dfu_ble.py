#!/usr/bin/env python3
"""Authenticate native DFU divergence instead of substituting stock SDK events."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from audit_source_frontier import section_bytes
 out=BASE/'native-dfu-ble-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text());e=json.loads((out/'native-sdk-correlation.json').read_text())
 assert r['comparisons']==34560 and r['counts']==dict(event=16128,authorize=18432) and r['observation_counts']==dict(value_get=18624,reply=37248,prepare=756,write=6214,callback=567,getter=2016,indication=9312) and r['trace_sha256']=='ea7f9ba4a3ee1783923fad44bc69b37cbd483ab4a1e23e182f67a6786f5691e4'
 for flag in ['actual_native_observer_authorizer_sdk_bit_helper_and_glasses_getter','only_svc_backend_and_event_callbacks_are_fixtures','native_connection_updates_and_disconnect_divergence_checked','all_cccd_bytes_partial_value_writes_and_busy_retries_checked','native_external_auth_frame_addresses_and_reply_bytes_checked','fresh_connection_and_mutated_reply_status_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_sdk_observer_substitution_used','full_raw_abi_verified','cross_call_private_frame_history_verified','backend_preparation_and_control_point_execution_proven','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_dfu_ble.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'dfu-ble-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_dfu_ble_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-dfu-ble-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-dfu-ble-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==28
 assert sha(out/'indication-helper-source.o')==b['helper_object_sha256'] and sha(out/'glasses-handle-source.o')==b['getter_object_sha256'] and undefined_symbols(out/'indication-helper-source.o')[0]==undefined_symbols(out/'glasses-handle-source.o')[0]==[]
 assert undefined_symbols(out/'dfu-ble-source.o')[0]==b['graph_undefined_symbols']==b['newly_exposed_imports']==['r1_dfu_bootloader_prepare_boundary','r1_dfu_control_point_write_boundary'] and b['closed_parent_imports']==['ble_dfu_buttonless_on_ble_evt','r1_ble_dfu_context']
 assert b['native_observer_differs_from_sdk'] and not b['complete_sdk_observer_substituted'] and b['source_context_bytes']==28 and b['new_value_seed_bytes']==4
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('52154',132),('7cdc8',108),('9c65c',4)]:
  q=json.loads((BASE/'native-dfu-ble-event'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 obj=BASE/'native-dfu-ble-event/native_dfu_ble_event.o';assert section_bytes(obj,'.r1.dfu.context',executable=False)==bytes(28) and section_bytes(obj,'.r1.dfu.value_seed',executable=False)==raw[0x9c65c-0x27000:0x9c660-0x27000]
 assert e['native_observer_whole_sdk_substitution_rejected'] and len(e['native_vs_sdk_differences'])==3 and not e['frozen_ownership_ledger_edited'] and int(e['cold_context_address'],16)==0x2002c110 and e['cold_context_bytes']==28 and [int(x,16) for x in e['native_zero_scatter_interval']]==[0x20007e04,0x2003beb8]
 zero=json.loads((BASE/'native-scatter-data/verification.json').read_text());assert zero['official_zero_bytes']==0x340b4 and 0x20007e04<=0x2002c110<0x2002c110+28<=0x20007e04+zero['official_zero_bytes']==0x2003beb8
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for inputs in [json.loads((BASE/'sdk-ble-service-common/report.json').read_text())['inputs'],e['sdk_reference_sources']]:
   for p,h in inputs.items():
    assert sha(ROOT/p)==h,p
    if p.startswith(prefix):assert hashlib.sha256(z.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==h,p
 for p,h in json.loads((out/'superseded-evidence.json').read_text()).items():assert sha(out/p)==h,p
 print('DFU BLE:34560 cases;native/SDK divergences retained;28 context+4 seed bytes;28 imports incl two backend gates;ABI/hardware/image gates open')
if __name__=='__main__':audit()
