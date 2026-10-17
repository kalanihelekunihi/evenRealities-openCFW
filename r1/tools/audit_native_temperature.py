#!/usr/bin/env python3
"""Authenticate temperature source, boundary comparisons and unresolved composed probe."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-temperature';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';binary=app.read_bytes();assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in b['comparison_only_inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-qma-configuration';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-qma-configuration-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-temperature-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-temperature-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==18 and b['closed_parent_imports']==['r1_temperature_pair_read_calibrated'] and not b['newly_exposed_imports']
 assert sha(out/'temperature-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'temperature-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==11 and set(b['graph_undefined_symbols'])<=set(b['undefined_symbols'])
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_temperature.py')==r['driver_sha256']
 assert r['comparisons']==69964 and r['counts']==dict(r1_temperature_pair_read_calibrated=1782,r1_gxt310_temperature_read=65776,r1_gxt310_temperature_channel0=240,r1_gxt310_temperature_channel2=240,r1_gxt310_one_shot=48,r1_gxt310_one_shot_channel0=48,r1_gxt310_one_shot_channel2=48,r1_temperature_calibration_read=1782)
 assert r['trace_sha256']=='25954065685c7ace271e27f6234c4cdb194753b57240bf34d3e919867c42a139' and r['observation_counts']==dict(r1_gxt310_bus_acquire=1782,r1_gxt310_enable_pair_native=1782,osDelay=1782,r1_gxt310_disable_pair_native=1782,r1_gxt310_bus_release=1782,r1_kv_class_read=3564,r1_gxt310_transfer_read_native=69820,r1_gxt310_transfer_write_native=3708,r1_structured_log_mode_get=3660,r1_structured_log_format=24,nrf_log_frontend_std_1=18)
 for p,h in r['evidence'].items():
  path=BASE/'native-temperature-analysis'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 sections=allocated_sections(out/'native_temperature.o');assert sections['.r1.temp.calibration'][2:]==[6,1,hashlib.sha256(bytes(6)).hexdigest()] and b['calibration_bytes']==6
 cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and cold.read_bytes()[0x200076f0-0x200064a8:0x200076f6-0x200064a8]==bytes(6)
 assert sha(out/'text-spans.json')==b['text_spans_sha256'] and sha(out/'contracts.json')==b['contracts_sha256'];spans=json.loads((out/'text-spans.json').read_text());assert len(spans)==2 and sum(x['size'] for x in spans)==100
 for x in spans:
  a=int(x['address'],16);data=binary[a-0x27000:a-0x27000+x['size']];assert data.split(b'\0')[0].decode()==x['text'] and sections[x['section']][2]==x['size'] and sections[x['section']][4]==hashlib.sha256(data).hexdigest()
 assert struct.unpack_from('<I',binary,0x50ec8-0x27000)[0]==0x200076f0 and struct.unpack_from('<I',binary,0x7bb00-0x27000)[0]+4==0x20007dfc and binary[0x6f638-0x27000:0x6f640-0x27000].hex()=='0000003c00007a44'
 probe=json.loads((out/'composed-history-probe.json').read_text());assert not probe['resolved'] and probe['native_return']==probe['source_return']==19795 and probe['first_trace_difference']['index']==1
 for name,h in probe['preserved_files'].items():assert sha(out/probe['preserved_directory']/name)==h,name
 assert probe['driver_sha256']==sha(ROOT/'r1/tools/probe_native_temperature_composed.py') and probe['report_sha256']==sha(out/'report.json') and probe['object_sha256']==b['linked_sha256']
 diff=probe['first_trace_difference'];assert diff['native'][2][0]=='90000100c8cf0320020000000000000001000000' and diff['source'][2][0]=='90000100cccf0320020000000000000001000000' and diff['native'][2][1]==diff['source'][2][1]=='00c20000'
 fix=json.loads((out/'cold-calibration-correction.json').read_text());assert fix['native_cold_bytes']=='000000000000' and fix['earlier_incorrect_candidate_bytes']=='ffffffffffff'
 for name,h in fix['preserved_files'].items():assert sha(out/'pre-cold-calibration-fix'/name)==h,name
 for flag in ['all_65536_sample_words_checked_with_independent_integer_oracle','actual_eight_temperature_bodies','bus_mode_registry_nv_rtos_and_log_dependencies_are_fixtures','raw_r0_callee_sp_fp_state_data_and_typed_call_records_checked']:assert r[flag]
 for flag in ['whole_source_consumer_graph_executed','full_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Temperature:69964 scoped comparisons;6 cold calibration+100 diagnostic bytes;18 main imports;composed frame gate open')
if __name__=='__main__':audit()
