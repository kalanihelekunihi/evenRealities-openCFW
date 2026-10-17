#!/usr/bin/env python3
"""Authenticate native GXT frame replacement and unnormalized temperature composition."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-gxt-call-frames';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());parent=BASE/'native-temperature';po=parent/'native-temperature-runtime.o';clone=out/'parent-weakened.o'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['weakened_parent_sha256'] and allocated_sections(po)==allocated_sections(clone)
 def nm(path):return {v[2]:(v[0],v[1]) for l in subprocess.check_output(['arm-none-eabi-nm',str(path)],text=True).splitlines() if len(v:=l.split())==3}
 before,after=nm(po),nm(clone);names=b['replacement_symbols'];assert len(names)==len(set(names))==5 and set(before)==set(after)
 for name,v in before.items():assert after[name]==(v[0],'W') if name in names else after[name]==v
 assert sha(out/'replacement-symbols.json')==b['replacement_symbols_sha256'] and set(json.loads((out/'replacement-symbols.json').read_text()).values())==set(names)
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 assert sha(out/'native-gxt-call-frames-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-gxt-call-frames-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==18 and not b['closed_parent_imports'] and not b['newly_exposed_imports']
 assert sha(out/'gxt-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'gxt-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==11
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_gxt_call_frames.py')==r['driver_sha256'] and r['application_sha256']==sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')
 assert r['comparisons']==5376 and r['counts']['r1_temperature_pair_read_calibrated']==3456 and all(r['counts'][n]==384 for n in names) and sum(r['counts'].values())==5376
 assert r['observation_counts']==dict(osDelay=3456,r1_kv_class_read=3456,r1_structured_log_mode_get=56064,r1_structured_log_format=8256,nrf_log_frontend_std_1=10560,nrf_log_frontend_std_0=3456,r1_stock_dispatch_08=3456,r1_stock_dispatch_0c=3456,r1_stock_dispatch_10=6912,r1_stock_dispatch_14=23424) and r['trace_sha256']=='7d32c628728fb2f567e1477ba017ee594f163c37d324f701067f27af13cd4781'
 for p,h in r['evidence'].items():assert sha(BASE/'native-temperature-analysis'/p)==h,p
 for a,body in [('6f804',['0x6f804: mov r1, r0','0x6f806: movs r0, #0x90','0x6f808: b.w 0x0006f648']),('6f81e',['0x6f81e: mov r1, r0','0x6f820: movs r0, #0x94','0x6f822: b.w 0x0006f648'])]:
  n=json.loads((out/('rea-'+a+'.json')).read_text())['structuredContent']['normalized_result'];assert n['procedure']['address']=='0x'+a and n['assembly']==body
 for flag in ['actual_temperature_gxt_bus_and_mode_bodies','registry_dispatch_nv_rtos_and_log_callbacks_are_fixtures','prior_four_byte_mode_frame_probe_covered_without_normalization','raw_r0_callee_sp_fp_state_data_and_typed_call_records_checked']:assert r[flag]
 for flag in ['whole_source_consumer_graph_executed','full_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 probe=json.loads((parent/'composed-history-probe.json').read_text());assert not probe['resolved'] and probe['native_return']==probe['source_return']==19795 and probe['first_trace_difference']['index']==1
 print('GXT frame correction:5376 comparisons including3456 temperature compositions;exact pointers;18 main imports;old failure retained')
if __name__=='__main__':audit()
