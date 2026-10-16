#!/usr/bin/env python3
"""Authenticate native tanf source, numeric data and bounded execution receipts."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 out=BASE/'native-tanf';r=read(out/'verification.json');g=read(out/'consumer-verification.json');ev=read(out/'evidence.json');report=read(out/'report.json');bp=BASE/'native-tanf-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['trace_sha256']=='345011d61a1103609953f0d5448f050b42692a3c2a3fdb6eb264667e31c781c9'
 assert r['errno_writes_per_side']=={'tanf':64}
 assert r['comparisons']==474016 and r['counts']=={'tanf':474016}
 assert r['application_sha256']==g['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for flag in ['all_binary32_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','initial_inexact_flag_zero_and_one','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_tanf_and_dependencies','independent_calls_reset_xpsr','runtime_no_unresolved']:assert r[flag]
 assert 'all_binary32_and_binary64_exponents' not in r and not r['instruction_identity'] and not g['instruction_identity']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_tanf.py') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_tanf_consumers.py')
 assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_tanf.o')
 for receipt in [r,g]:
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-tanf-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked']
 assert set(report['units'][0]['undefined'])=={'r1_binary32_classify_bits','r1_math_low_square32','r1_math_invalid32','r1_math_self_add32','r1_native_errno_set','r1_native_trig_reduce32'}
 for p,h in r['evidence'].items():assert sha(out/p)==h,p
 raw=read(out/'rea-3b048.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
 assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['ranges']==[{'start':'0x3b048','end':'0x3b189'},{'start':'0x3bad4','end':'0x3badd'}]
 assert bytes(read(out/'ghidra-3b048.json')['data'])==app.read_bytes()[0x14048:0x1418a]
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13'
 assert ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x0003b048') and not ev['locked_ownership_changed'] and ev['new_source_routes']==1 and ev['native_body_bytes']==332
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(out/'pseudocode-3b048.c.txt')
 from audit_source_frontier import section_bytes
 data=section_bytes(out/'native_tanf.o','.r1.math.tanf_data',executable=False);assert data==bytes(read(out/'ghidra-3b18c.json')['data'])==app.read_bytes()[0x1418c:0x141c4] and len(data)==r['source_owned_numeric_bytes']==ev['source_owned_numeric_bytes']==56 and hashlib.sha256(data).hexdigest()==r['source_owned_data_sha256']
 previous=read(BASE/'native-sinf/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies']+['tanf'] and g['remaining_consumer_bodies_native']==6
 assert g['helper_observations']=={side:{**values,'tanf':56,**({'class32':8,'errno':56,'self32':0,'invalid32':12,'low32':8,'trig_reduce':0} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='47ad0ed07dda23461f031a66121269131618b9a156b88cea59f8fb5e059238d9'
 for flag in ['runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','independent_calls_reset_xpsr']:assert g[flag]
 for key,p in [('report_sha256',BASE/'native-float-bits/report.json'),('object_sha256',BASE/'native-float-bits/native_float_bits.o'),('math_report_sha256',BASE/'native-formatter-math/report.json'),('math_object_sha256',BASE/'native-formatter-math/native-formatter-math.o')]:assert g[key]==sha(p)
 assert ev['native_disassembly_sha256']==sha(out/'native-disassembly.txt') and ev['native_main_bytes']==ev['new_unique_native_bytes']==322 and ev['shared_existing_tail_bytes']==10
 assert bytes(read(out/'ghidra-3bad4.json')['data'])==app.read_bytes()[0x14ad4:0x14ade] and q['normalized_result']['body']['total_bytes']==332 and q['normalized_result']['body']['non_contiguous']
 print('Native tanf: direct, consumer, source/runtime/data evidence authenticated; full ABI and image identity remain gated')
if __name__=='__main__':audit()
