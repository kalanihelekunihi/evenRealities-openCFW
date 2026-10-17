#!/usr/bin/env python3
"""Authenticate Bosch setup scope and preserve its unresolved private-input frame alias."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-bma-setup';b=json.loads((out/'report.json').read_text());r=json.loads((out/'setup-verification.json').read_text());v=json.loads((out/'validator-verification.json').read_text());f=json.loads((out/'private-input-frame-alias-probe.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']==v['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-fifo';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-fifo-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-setup-runtime.o')==b['linked_sha256']==r['object_sha256']==f['object_sha256'] and undefined_symbols(out/'native-bma-setup-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==24 and sha(out/'setup-source.o')==b['graph_object_sha256'] and not undefined_symbols(out/'setup-source.o')[0]
 assert r['comparisons']==6966 and r['counts']==dict(enable=1960,accel_config=3046,fifo_config=1960) and r['matching_faults']==729 and r['failed_write_followed_by_25000_delay_cases']==405 and r['observation_counts']==dict(read=3890,write=6772,delay=6549) and r['trace_sha256']=='a7221a9b06ed1a3b007c84622cf9b230c803afd39204ba4d09d7e0b3f814c89f'
 assert v['comparisons']==262144 and v['result_counts']=={'0':95,'-8':262012,'-15':37} and v['trace_sha256']=='a10ddf6d9fe8623200f165df93194c023eda7a7d1e8825b3447338ce8c79e947' and sha(out/'bosch-setup-kernels.o')==v['object_sha256']
 for proof,driver in [(r,'verify_native_bma_setup.py'),(v,'verify_native_bma_validator.py')]:assert sha(out/'report.json')==proof['report_sha256'] and sha(ROOT/('r1/tools/'+driver))==proof['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and len(b['source_slices'])==6
 vendor=ROOT/'third-party/upstream/bosch-bma456';raw=(vendor/'bma4.c').read_bytes();generated=(out/'bosch-setup-kernels.c').read_text();assert (vendor/'LICENSE').read_text() in generated
 for row in b['source_slices']:
  assert hashlib.sha256(raw[row['start']:row['end']]).hexdigest()==row['original_slice_sha256'] and raw[row['start']:row['end']].decode()==row['body']
  if row['function'] in b['validator_renames']:
   adapted=row['body'].replace('\r\n','\n')
   for old,new in b['validator_renames'].items():adapted=adapted.replace(old,new)
   if row['function']=='validate_odr_bandwidth_perfmode':adapted=adapted.replace('static int8_t','int8_t',1)
   assert adapted in generated
 assert b['accel_enable_assignment'] in generated and b['fifo_logic'].replace('\r\n','\n') in generated and not undefined_symbols(out/'bosch-setup-kernels.o')[0]
 for flag in ['actual_three_setters_attributed_kernels_read_write_graph_requests_and_registry','only_bus_raw_transport_and_delay_callbacks_are_fixtures','failed_write_delay_fresh_callback_public_ram_alias_and_full_enable_word_checked','private_stack_input_aliases_explicitly_gated','fifo_configuration_against_independent_mask_oracle','native_callback_scratch_pointer_callee_sp_context_ram_checked']:assert r[flag]
 for flag in ['all_65536_odr_bandwidth_byte_pairs_at_perf_0_1_2_255','independent_limits_oracle','actual_pinned_validator_bodies_no_fixtures','raw_r0_callee_sp_checked']:assert v[flag]
 for proof in [r,v,f]:
  for flag in ['full_private_frame_history_verified','full_raw_abi_verified','whole_image_complete','hardware_write_executed']:assert not proof[flag]
 h=out/'pre-private-alias-scope';assert sha(h/'report.json')==f['report_sha256']==sha(out/'report.json') and sha(h/'verify_native_bma_setup.py')==f['driver_sha256'] and sha(h/'r1-bma-setup-verification.log')==f['log_sha256'] and sha(h/'native-bma-setup-runtime.o')==f['object_sha256'] and sha(h/'private-input-frame-alias-probe.json')==sha(out/'private-input-frame-alias-probe.json')
 assert f['case']['pointer']==0x2003cfef and f['raw_r0_context_match'] and not f['register_payload_match'] and f['native_result'][-1]['64']==0 and f['source_result'][-1]['64']==17
 print('Bosch setup:6966 scoped setter +262144 validator comparisons;private-stack input alias remains an explicit failed probe')
if __name__=='__main__':audit()
