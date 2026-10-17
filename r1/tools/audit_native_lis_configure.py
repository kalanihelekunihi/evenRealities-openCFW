#!/usr/bin/env python3
"""Audit compiled LIS configure candidate and its unresolved composed-frame gate."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-lis-configure';b=json.loads((out/'report.json').read_text());f=json.loads((out/'composed-frame-probe.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for path,h in b['inputs'].items():assert sha(ROOT/path)==h,path
 assert sha(out/'report.json')==f['report_sha256'] and sha(out/'configure-source.o')==f['graph_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_configure.py')==f['driver_sha256'] and sha(out/'failed-verification.log')==f['log_sha256']
 parent=BASE/'native-lis-setup';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-setup-runtime.o')==b['parent_object_sha256'] and sha(out/'native_lis_configure.o')==b['unit_object_sha256'] and sha(out/'native-lis-configure-runtime.o')==b['linked_sha256']
 assert undefined_symbols(out/'native-lis-configure-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==28 and undefined_symbols(out/'configure-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==21
 n=json.loads((out/'rea-configure-bytes.json').read_text())['structuredContent']['normalized_result'];assert n['complete'] and int(n['address'],16)==0x75510 and n['returned_bytes']==444 and bytes.fromhex(n['bytes_hex'])==binary[0x75510-0x27000:0x756cc-0x27000]
 sections=allocated_sections(out/'native_lis_configure.o')
 for name,a,size in [('id_ring',0x75664,28),('id_sdk',0x75680,24),('reset_ring',0x75698,28),('reset_sdk',0x756b4,24)]:
  section=sections['.r1.lis.config.'+name];assert section[2]==size and section[4]==hashlib.sha256(binary[a-0x27000:a-0x27000+size]).hexdigest()
 assert f['first_trace_difference_index']==1 and f['return_context_outer_frame_register_model_poll_count_match'] and not f['bus_request_pointer_matches'] and f['register_data_pointer_matches']
 native=f['first_native_observation'];source=f['first_source_observation'];assert native[1][2]==0x2003cf80 and source[1][2]==0x2003cf70 and native[2]==source[2]=='180021000000000000000000b0cf032001000000'
 assert f['native_result']!=f['source_result'] and f['native_result'][1][0]==f['source_result'][1][0] and not f['composed_runtime_verified'] and not f['whole_image_complete'] and not f['hardware_write_executed']
 assert 'r1_lis2dw12_configure_boundary' in b['closed_parent_imports'] and not b['newly_exposed_imports'] and not b['whole_image_complete'] and not b['instruction_identity'] and not b['hardware_write_executed']
 h=out/'pre-call-boundary-fix'
 for name in ['report.json','configure-source.o','native-lis-configure-runtime.o','native_lis_configure.o','composed-frame-probe.json']:assert sha(h/name)==sha(out/name)
 print('LIS configure candidate compiled;104 exact text bytes; composed bus-frame mismatch retained, not verified')
if __name__=='__main__':audit()
