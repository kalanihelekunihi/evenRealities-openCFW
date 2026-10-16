#!/usr/bin/env python3
"""Audit compiled binary64 pow without promoting ABI or image identity gates."""
import contextlib,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-pow-core';OLD=BASE/'native-pow-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_pow_dispatch import audit as history
 with contextlib.redirect_stdout(io.StringIO()):history()
 r=read(OLD/'source-verification.json');b=read(OLD/'core-boundary-verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');report=read(OUT/'report.json');bp=BASE/'native-pow-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==90708 and r['counts']=={'pow':90708} and r['trace_sha256']==read(OLD/'verification.json')['trace_sha256']
 assert b['comparisons']==4480 and b['trace_sha256']=='be4ebf96257bbee0405f4b22c96cbc6d23fd6604a8394661a343a0cefa7592c3' and b['core_bucket_near_one_and_product_boundaries']
 assert not any(b[k] for k in ['all_binary64_exponents','both_signs','seeded_random_pairs','signed_zero_and_infinity_pairs','selected_edge_pairs_all_fz_dn_controls','selected_edge_pairs_initial_inexact_zero_and_one'])
 for receipt,driver in [(r,'verify_native_pow_source.py'),(b,'verify_native_pow_core_boundaries.py'),(g,'verify_native_pow_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and receipt['runtime_no_unresolved'] and receipt['source_pow_complete'] and not receipt['native_pow_core_fixture'] and 'fixture_source' not in receipt and not receipt['instruction_identity']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-pow-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert 'PROVIDE(r1_stock_pow' not in (ROOT/g['layout']).read_text() and not bundle['undefined_symbols'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-pow-core/report.json','native-pow-dispatch-runtime/report.json']}
 assert r['report_sha256']==sha(OLD/'report.json') and r['object_sha256']==sha(OLD/'native_pow_dispatch.o') and r['actual_source_pow_dispatch']
 for p,h in r['evidence'].items():assert sha(OLD/p)==h,p
 for flag in ['both_signs','all_binary64_exponents','seeded_random_pairs','all_four_rounding_modes','selected_edge_pairs_all_fz_dn_controls','selected_edge_pairs_initial_inexact_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','base_and_exponent_signs','integer_parity_cases','independent_calls_reset_xpsr']:assert r[flag]
 assert ev['new_source_routes']==1 and ev['full_native_body_bytes']==2900 and ev['dispatcher_native_bytes']==850 and ev['core_native_bytes']==2006 and ev['shared_native_tail_bytes']==44 and ev['core_numeric_bytes']==324 and ev['dispatcher_numeric_bytes']==84 and ev['total_numeric_bytes']==408 and ev['unique_numeric_bytes']==400 and not ev['locked_ownership_changed']
 assert ev['prior_evidence_sha256']==sha(OLD/'evidence.json') and ev['core_contract_sha256']==sha(OLD/'core-contract.json')
 for p,h in ev['ghidra_evidence'].items():assert sha(OUT/p)==h,p
 assert ev['rea_sha256']==sha(OUT/'rea-399d0.json')
 from audit_source_frontier import section_bytes
 total=0
 for name,a,n in [('near',0x39e40,40),('normal',0x3a288,40),('log',0x3a2bc,36),('limits',0x3a5d0,32),('scaling',0x3a5f4,28),('tail',0x3a614,12),('base',0xbd8c8,16),('log_high',0xbd8d8,16),('log_low',0xbd8e8,16),('log_poly',0xbd8f8,48),('exp_poly',0xbd928,40)]:
  data=section_bytes(OUT/'native_pow_core.o','.r1.math.pow_'+name,executable=False);assert len(data)==n and data==app.read_bytes()[a-0x27000:a-0x27000+n];total+=n
  assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==data
 assert total==324
 previous=read(OLD/'consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies'] and g['remaining_consumer_bodies_native']==0
 expected={side:{**values,'pow_core':32 if side=='compiled_entries' else 0,**(dict.fromkeys(['signed_to64','subtract','reverse_subtract','polynomial','errno','low64'],0) if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['helper_observations']==expected and g['trace_sha256']=='acbe7fc39478350b2db231b452cf7c71338fc1da5dc225075a6d1c82a7b3458d'
 print('Source binary64 pow authenticated: no native core fixture; full ABI/placement/image gates remain open')
if __name__=='__main__':audit()
