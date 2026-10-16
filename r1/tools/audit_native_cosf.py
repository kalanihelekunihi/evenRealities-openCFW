#!/usr/bin/env python3
"""Authenticate native cosf source, numeric data and bounded execution receipts."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 out=BASE/'native-cosf';r=read(out/'verification.json');g=read(out/'consumer-verification.json');ev=read(out/'evidence.json');report=read(out/'report.json');bp=BASE/'native-cosf-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['trace_sha256']=='430911711942338b0ca7d29c6b02f2ae1762abb8ba6941dfa07ddac313cabd6c' and r['errno_writes_per_side']=={'cosf':64}
 assert r['comparisons']==470752 and r['counts']=={'cosf':470752}
 assert r['application_sha256']==g['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for flag in ['all_binary32_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','initial_inexact_flag_zero_and_one','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_cosf_and_dependencies','independent_calls_reset_xpsr','runtime_no_unresolved']:assert r[flag]
 assert 'all_binary32_and_binary64_exponents' not in r and not r['instruction_identity'] and not g['instruction_identity']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_cosf.py') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_cosf_consumers.py')
 assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_cosf.o')
 for receipt in [r,g]:
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-cosf-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked']
 assert set(report['units'][0]['undefined'])=={'r1_math_invalid32','r1_math_self_add32','r1_native_errno_set','r1_native_trig_reduce32'}
 for p,h in r['evidence'].items():assert sha(out/p)==h,p
 raw=read(out/'rea-38a5c.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
 assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['ranges']==[{'start':'0x38a5c','end':'0x38b73'}]
 assert bytes(read(out/'ghidra-38a5c.json')['data'])==app.read_bytes()[0x11a5c:0x11b74]
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13'
 assert ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x00038a5c') and not ev['locked_ownership_changed'] and ev['new_source_routes']==1 and ev['native_body_bytes']==280
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(out/'pseudocode-38a5c.c.txt')
 from audit_source_frontier import section_bytes
 data=section_bytes(out/'native_cosf.o','.r1.math.cosf_data',executable=False);assert data==bytes(read(out/'ghidra-38b74.json')['data'])==app.read_bytes()[0x11b74:0x11bac] and len(data)==r['source_owned_numeric_bytes']==ev['source_owned_numeric_bytes']==56 and hashlib.sha256(data).hexdigest()==r['source_owned_data_sha256']
 previous=read(BASE/'native-trig-reduce/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies']+['cosf'] and g['remaining_consumer_bodies_native']==8
 assert g['helper_observations']=={side:{**values,'cosf':56,**({'errno':72,'self32':8,'invalid32':28,'trig_reduce':32} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='a2833f57696326f217f2a7bdcbbb2ec76a0e0e1a35056e2c4d7de96c9967b0a6'
 for flag in ['runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','independent_calls_reset_xpsr']:assert g[flag]
 for key,p in [('report_sha256',BASE/'native-float-bits/report.json'),('object_sha256',BASE/'native-float-bits/native_float_bits.o'),('math_report_sha256',BASE/'native-formatter-math/report.json'),('math_object_sha256',BASE/'native-formatter-math/native-formatter-math.o')]:assert g[key]==sha(p)
 print('Native cosf: direct, consumer, source/runtime/data evidence authenticated; full ABI and image identity remain gated')
if __name__=='__main__':audit()
