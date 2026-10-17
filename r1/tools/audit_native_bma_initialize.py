#!/usr/bin/env python3
"""Authenticate Bosch initialization/configuration scope and retained private-history gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-bma-initialize';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());f=json.loads((out/'partial-read-history-probe.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-setup';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-setup-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-initialize-runtime.o')==b['linked_sha256']==r['object_sha256']==f['object_sha256'] and undefined_symbols(out/'native-bma-initialize-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==23 and not any('bma' in x for x in b['undefined_symbols']) and sha(out/'initialize-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'initialize-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_bma456w_configure_boundary'] and not b['newly_exposed_imports']
 assert r['comparisons']==13248 and r['counts']==dict(base=5184,variant=5184,configure=2880) and r['matching_faults']==3 and r['observation_counts']==dict(read=13950,write=18051,delay=0,cycles=22725,mode=6320,ring=1580,sdk=1202) and r['trace_sha256']=='43010b1e931a1a5bda16ea62803787b66f62269d486509a630cd88bffd982bbb'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_bma_initialize.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and b['upstream_config_array_bytes']==5016 and not b['feature_stream_uploaded_by_this_sequence'] and b['default_remap_typed_bytes']==6 and b['observed_literal_read_bytes']==8 and b['observed_following_bytes_hex']=='802e' and not b['following_bytes_semantic_origin_proven'] and not b['exact_vendor_checkout_proven']
 vendor=ROOT/'third-party/upstream/bosch-bma456'
 for row in b['source_slices']:assert hashlib.sha256((vendor/row['file']).read_bytes()[row['start']:row['end']]).hexdigest()==row['original_slice_sha256']
 spans=out/'configuration-text-spans.json';assert sha(spans)==b['configuration_text_spans_sha256'];rows=json.loads(spans.read_text());assert len(rows)==18 and sum(x['size'] for x in rows)==724;sections=allocated_sections(out/'native_bma_initialize.o')
 for row in rows:
  a=int(row['address'],16);data=binary[a-0x27000:a-0x27000+row['size']];assert data.split(b'\0')[0].decode()==row['text'] and sections[row['section']][2]==row['size'] and sections[row['section']][4]==hashlib.sha256(data).hexdigest()
 remap=binary[0x9a768-0x27000:0x9a770-0x27000];assert remap.hex()=='000102000000802e' and sections['.r1.bma.remap.span'][2:]==[8,4,hashlib.sha256(remap).hexdigest()]
 for flag in ['actual_three_initialization_configuration_bodies_full_bosch_graph_requests_registry','only_bus_raw_transport_delay_cycle_and_logging_callbacks_are_fixtures','raw_restored_r2_r3_observed_span_fresh_logging_failures_and_rates_checked','prior_private_stack_input_alias_gate_retained','partial_successful_configuration_read_histories_explicitly_gated','native_callback_scratch_pointer_callee_sp_context_ram_checked']:assert r[flag]
 for proof in [r,f]:
  for flag in ['full_private_frame_history_verified','full_raw_abi_verified','whole_image_complete','hardware_write_executed']:assert not proof[flag]
 h=out/'pre-partial-read-scope';assert sha(h/'report.json')==f['report_sha256']==sha(out/'report.json') and sha(h/'verify_native_bma_initialize.py')==f['driver_sha256'] and sha(h/'r1-bma-initialize-verification.log')==f['log_sha256'] and sha(h/'native-bma-initialize-runtime.o')==f['object_sha256'] and sha(h/'partial-read-history-probe.json')==sha(out/'partial-read-history-probe.json')
 assert f['case']['written']==2 and f['case']['kind']=='configure' and f['raw_return_and_context_match'] and f['first_difference_index']==16 and f['native_observation'][-2]=='80' and f['source_observation'][-2]=='00' and f['native_observation'][2]==f['source_observation'][2]
 prior=json.loads((parent/'private-input-frame-alias-probe.json').read_text());assert not prior['register_payload_match']
 print('Bosch initialize/configure:13248 scoped comparisons;732 exact data bytes;23 main imports;private-history gates retained')
if __name__=='__main__':audit()
