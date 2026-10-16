#!/usr/bin/env python3
"""Bind exhaustive arithmetic, signed-count and partial-sample ordering evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-motion-fifo-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==19104 and r['counts']==dict(lis=6368,bma=6368,qma=6368) and r['observation_counts']==dict(acquire=10464,release=10464,read=19104) and r['matching_faults']==4860 and r['exhaustive_blocks']==6144 and r['exhaustive_values_per_axis_per_family']==65536 and r['partial_triple_fault_cases']==2430 and r['trace_sha256']=='76fc53281b5e02fe13009d4c409136753abf489d23e38c91d1dc3338b8effdf1'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'motion-fifo-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_motion_fifo.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-motion-fifo'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_three_normalizers_bus_wrappers_and_registry_dispatch','only_raw_fifo_and_bus_operations_are_fixtures','unclamped_counts_signed_returns_asr_rounding_and_qma_preload_checked','raw_r0_callee_sp_and_partial_fault_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_fifo_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-motion-fifo-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==31 and undefined_symbols(out/'motion-fifo-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_bma456w_fifo_normalized','r1_lis2dw12_fifo_normalized','r1_qma6100_fifo_normalized'] and b['newly_exposed_imports']==['r1_bma456w_fifo_read','r1_lis2dw12_fifo_read','r1_qma6100_bounded_fifo_read']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Motion FIFO:19104 comparisons; all16-bit axis values; native partial-fault ordering retained')
if __name__=='__main__':audit()
