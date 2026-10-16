#!/usr/bin/env python3
"""Audit complete source powf dispatch/core and retain the native-fixture history."""
import contextlib,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-powf-core';OLD=BASE/'native-powf-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_powf_dispatch import audit as history
 with contextlib.redirect_stdout(io.StringIO()):history()
 r=read(OLD/'source-verification.json');b=read(OLD/'core-boundary-verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');report=read(OUT/'report.json');bp=BASE/'native-powf-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==427168 and r['counts']=={'powf':427168} and r['trace_sha256']=='5b07862522891d3e21365cca57afaebf4436dcaf3ba32adea5430a22da0cc091' and r['trace_sha256']==read(OLD/'verification.json')['trace_sha256']
 assert b['comparisons']==67840 and b['trace_sha256']=='21b07c5e4af3a4cca727821ab80645d8abac7eee2a92a94229e44d97c2618b19' and b['core_bucket_and_near_one_boundaries'] and not b['all_binary32_exponents'] and not b['seeded_random_pairs'] and not b['signed_zero_and_infinity_pairs']
 assert r['all_binary32_exponents'] and r['seeded_random_pairs'] and r['signed_zero_and_infinity_pairs']
 for receipt,driver in [(r,'verify_native_powf_source.py'),(b,'verify_native_powf_core_boundaries.py'),(g,'verify_native_powf_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and receipt['runtime_no_unresolved'] and receipt['source_powf_complete'] and not receipt['native_powf_core_fixture'] and 'fixture_source' not in receipt and not receipt['instruction_identity']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-powf-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert 'PROVIDE(r1_stock_powf' not in (ROOT/g['layout']).read_text() and not bundle['undefined_symbols'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-powf-core/report.json','native-powf-dispatch-runtime/report.json']}
 for receipt in [r,b]:
  assert receipt['report_sha256']==sha(OLD/'report.json') and receipt['object_sha256']==sha(OLD/'native_powf_dispatch.o') and receipt['actual_source_powf_dispatch_and_core']
  for p,h in receipt['evidence'].items():assert sha(OLD/p)==h,p
  for flag in ['both_signs','all_four_rounding_modes','float_flush_to_zero_and_default_nan_modes','initial_inexact_flag_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','base_and_exponent_signs','integer_parity_cases','independent_calls_reset_xpsr']:assert receipt[flag]
 assert ev['new_source_routes']==1 and ev['full_native_body_bytes']==1524 and ev['dispatcher_native_bytes']==580 and ev['core_native_bytes']==944 and ev['core_numeric_bytes']==396 and ev['dispatcher_numeric_bytes']==16 and ev['total_numeric_bytes']==412 and not ev['locked_ownership_changed']
 for key,p in [('prior_evidence_sha256',OLD/'evidence.json'),('core_contract_sha256',OLD/'core-contract.json'),('core_table_evidence_sha256',OLD/'core-table-evidence.json'),('boundary_label_counterexample_sha256',OLD/'core-boundary-label-counterexample.json')]:assert ev[key]==sha(p)
 from audit_source_frontier import section_bytes
 total=0
 for name,a,n in [('prefix',0x3aa38,32),('exponential',0x3aa5c,12),('scaling',0x3aa74,20),('near_one',0x3ac78,12),('log_table',0xbd950,128),('exp_head',0xbda10,64),('exp_scale',0xbda50,64),('exp_tail',0xbd9d0,64)]:
  data=section_bytes(OUT/'native_powf_core.o','.r1.math.powf_'+name,executable=False);assert len(data)==n and data==app.read_bytes()[a-0x27000:a-0x27000+n];total+=n
 assert total==396
 counter=read(OLD/'core-boundary-label-counterexample.json');assert counter['incorrect_label']=='signed_zero_and_infinity_pairs=True' and counter['corrected_label']=='signed_zero_and_infinity_pairs=False' and counter['comparisons']==b['comparisons'] and counter['trace_sha256']==b['trace_sha256']==read(OLD/'core-boundary-initial-verification.json')['trace_sha256']
 previous=read(OLD/'consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies'] and g['remaining_consumer_bodies_native']==1
 expected={side:{**values,'powf_core':132 if side=='compiled_entries' else 0,**({'class32':0,'environment':0,'errno':16,'low32':0} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['helper_observations']==expected and g['trace_sha256']=='f50e11f0c2c6bde75a7750fd928ebab9f75a4816b3d602d271ed5bb3ccc1f42c'
 assert g['helper_observations']['compiled_entries']['powf']==144 and g['helper_observations']['compiled_entries']['powf_core']==132
 print('Source powf dispatcher/core authenticated: no native core fixture; full ABI/placement/image gates remain open')
if __name__=='__main__':audit()
