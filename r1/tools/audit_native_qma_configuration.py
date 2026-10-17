#!/usr/bin/env python3
"""Authenticate QMA configuration bodies, native state prefix and scoped comparisons."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-qma-configuration';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';binary=app.read_bytes();assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in b['comparison_only_inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-qma-transport';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-qma-transport-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-qma-configuration-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-qma-configuration-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==19
 assert sha(out/'qma-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'qma-source.o')[0]==b['graph_undefined_symbols']==[] and b['closed_parent_imports']==['r1_qma6100_configure_boundary'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_qma_configuration.py')==r['driver_sha256']
 assert r['trace_sha256']=='7fe598835eeb3fab480e878d470217b5561342b1fba273d294d3ba7cede2474f' and r['observation_counts']==dict(read=162035,write=203573,cycles=1123250)
 assert r['comparisons']==5806 and r['counts']==dict(configure=555,setup=555,motion=1138,range=1054,reset=228,steps=1138,tap=1138)
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for a,size in [('86e68',110),('86ee4',194),('86d40',238),('87188',56),('871c4',138),('87250',144),('872e4',268)]:
  n=json.loads((out/('rea-'+a+'.json')).read_text())['structuredContent']['normalized_result'];assert n['procedure']['address']=='0x'+a and n['procedure']['body']['total_bytes']==size
 sections=allocated_sections(out/'native_qma_configuration.o');axis=struct.pack('<6H',1,1,1,0,1,2);assert binary[0x9a6a6-0x27000:0x9a6b2-0x27000]==axis and sections['.r1.qma.axis'][2:]==[12,2,hashlib.sha256(axis).hexdigest()]
 assert sections['.r1.qma.sensor'][2:4]==[24,4] and b['sensor_prefix_bytes']==24 and b['axis_defaults_bytes']==12
 for a,value in [(0x86ed8,0x1312),(0x86edc,0x2001e4b0),(0x86ee0,0x9a6a6),(0x86e30,0x2001e4b0),(0x871c0,0x2001e4b0),(0x872e0,0x2001e4b0)]:assert struct.unpack_from('<I',binary,a-0x27000)[0]==value
 assert b['owner_authorized_native_reconstruction'] and not b['unlicensed_qst_source_is_build_input'] and not b['existing_hardened_reconstruction_substituted'] and not b['full_sensor_state_extent_proven']
 assert r['unwritten_composed_setup_history_excluded'] and sha(out/'unwritten-setup-history-probe.json')==r['unwritten_setup_history_probe_sha256']
 probe=json.loads((out/'unwritten-setup-history-probe.json').read_text());assert not probe['resolved'] and probe['native_return']==probe['source_return']==1 and probe['first_trace_difference']['index']==1698 and probe['first_trace_difference']['native'][3]=='fb' and probe['first_trace_difference']['source'][3]=='f3'
 for name,h in probe['preserved_files'].items():assert sha(out/'pre-unwritten-setup-history'/name)==h,name
 assert sha(out/'pre-unwritten-setup-history/native_qma_configuration.c')==b['units'][0]['source_sha256']
 for flag in ['actual_seven_qma_bodies_transports_requests_and_registry','only_bus_and_cycle_callbacks_are_fixtures','raw_returns_saved_registers_sp_state_and_request_records_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('QMA configuration:5806 composed comparisons;24-byte state prefix+12-byte axis defaults;19 main imports')
if __name__=='__main__':audit()
