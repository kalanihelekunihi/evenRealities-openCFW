#!/usr/bin/env python3
"""Audit binary64 pow dispatcher without promoting its native reduced-core fixture."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-pow-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');report=read(OUT/'report.json');bp=BASE/'native-pow-dispatch-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==90708 and r['counts']=={'pow':90708} and r['trace_sha256']=='9557ee8189de7e3ec42c433b87b501af2e6255730b923c7f47148223480032c7'
 assert g['comparisons']==1952 and g['trace_sha256']=='be63cba86b484f1f20515439b326d5518aa46a6c807015dea3c08e2d771510f3' and g['helper_observations']['compiled_entries']['pow']==144
 for receipt,driver in [(r,'verify_native_pow_dispatch.py'),(g,'verify_native_pow_dispatch_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and not receipt['runtime_no_unresolved'] and receipt['native_pow_core_fixture'] and not receipt['source_pow_complete'] and receipt['unresolved_source_provider']=='r1_pow_reduced' and not receipt['instruction_identity']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-pow-dispatch-runtime.o')==bundle['linked_sha256']
  assert receipt['fixture_source']=='r1/tools/fixtures/pow_reduced_native_fixture.c' and receipt['fixture_source_sha256']==sha(ROOT/receipt['fixture_source'])
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert bundle['undefined_symbols']==['r1_pow_reduced'] and not bundle['application_linked']
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert r['report_sha256']==sha(OUT/'report.json') and r['object_sha256']==sha(OUT/'native_pow_dispatch.o')
 for p,h in r['evidence'].items():assert sha(OUT/p)==h,p
 for flag in ['all_binary64_exponents','both_signs','seeded_random_pairs','all_four_rounding_modes','selected_edge_pairs_all_fz_dn_controls','selected_edge_pairs_initial_inexact_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_pow_dispatch','base_and_exponent_signs','integer_parity_cases','independent_calls_reset_xpsr','signed_zero_and_infinity_pairs']:assert r[flag]
 assert 'float_flush_to_zero_and_default_nan_modes' not in r
 ranges=[(0x399d0,1056),(0x39e68,1056),(0x3a2e8,744),(0x3b54c,44)]
 for a,n in ranges+[(0x39df0,120),(0xbdb50,8)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
 raw=read(OUT/'rea-399d0.json')['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and raw['normalized_result']['body']['total_bytes']==2900 and raw['normalized_result']['body']['ranges']==[dict(start=hex(a),end=hex(a+n-1)) for a,n in ranges]
 from audit_source_frontier import section_bytes
 total=0
 for name,a,n in [('prefix',0x39df0,48),('suffix',0x39e24,28),('zero',0xbdb50,8)]:
  data=section_bytes(OUT/'native_pow_dispatch.o','.r1.math.pow_dispatch_'+name,executable=False);assert len(data)==n and data==app.read_bytes()[a-0x27000:a-0x27000+n];total+=n
 assert section_bytes(OUT/'native_pow_dispatch.o','.r1.math.pow_dispatch_zero',executable=False)==section_bytes(BASE/'native-trig-reduce/native_trig_reduce.o','.r1.math.trig_reduce_table',executable=False)[8:16]
 assert (int.from_bytes(app.read_bytes()[0x12e20:0x12e24],'little')+0x39b6a)&0xffffffff==0xbdb50
 assert total==r['source_owned_numeric_bytes']==ev['source_owned_numeric_bytes']==84 and r['shared_existing_numeric_bytes']==ev['shared_existing_numeric_bytes']==8 and r['unique_new_numeric_bytes']==ev['unique_new_numeric_bytes']==76
 assert ev['new_source_routes_admitted']==0 and ev['dispatcher_native_bytes']==850 and ev['pending_core_native_bytes']==2006 and ev['shared_existing_tail_bytes']==44 and ev['full_native_body_bytes']==2900
 contract=read(OUT/'core-contract.json');assert sha(OUT/'core-contract.json')==ev['core_contract_sha256'] and contract['native_entry']=='0x39d04' and contract['native_private_frame_bytes']==192 and not contract['external_blocker']
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13' and ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x000399d0') and not ev['locked_ownership_changed']
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-399d0.c.txt')
 print('Pow dispatcher verified with native reduced core fixture; one source provider remains unresolved and frontier is unchanged')
if __name__=='__main__':audit()
