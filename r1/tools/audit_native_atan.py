#!/usr/bin/env python3
"""Authenticate native atan source, numeric data and bounded execution receipts."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 out=BASE/'native-atan';r=read(out/'verification.json');g=read(out/'consumer-verification.json');ev=read(out/'evidence.json');report=read(out/'report.json');bp=BASE/'native-atan-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['trace_sha256']=='28a52b362986a534edecbca990642886ef55cc8ed9748cade43191ab7df1d8c8'
 assert r['errno_writes_per_side']=={'atan':0}
 assert r['comparisons']==37436 and r['counts']=={'atan':37436}
 assert r['application_sha256']==g['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for flag in ['all_binary64_exponents','both_signs','all_four_rounding_modes','selected_values_all_fz_dn_initial_inexact_controls','initial_inexact_flag_zero_and_one_selected_values','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_atan_and_dependencies','independent_calls_reset_xpsr','runtime_no_unresolved']:assert r[flag]
 assert 'all_binary32_and_binary64_exponents' not in r and not r['instruction_identity'] and not g['instruction_identity']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_atan.py') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_atan_consumers.py')
 assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_atan.o')
 for receipt in [r,g]:
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-atan-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked']
 assert set(report['units'][0]['undefined'])=={'r1_binary64_classify_bits','r1_binary64_reverse_subtract_bits','r1_binary64_subtract_bits','r1_format_double_add_bits','r1_format_double_divide_bits','r1_format_double_multiply_bits','r1_math_low_square64','r1_math_self_add64','r1_native_fabs_core_bits','r1_native_polynomial'}
 for p,h in r['evidence'].items():assert sha(out/p)==h,p
 raw=read(out/'rea-381f0.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
 assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['ranges']==[{'start':'0x381f0','end':'0x3845d'}]
 assert bytes(read(out/'ghidra-381f0.json')['data'])==app.read_bytes()[0x111f0:0x1145e]
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13'
 assert ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x000381f0') and not ev['locked_ownership_changed'] and ev['new_source_routes']==1 and ev['native_body_bytes']==622
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(out/'pseudocode-381f0.c.txt')
 from audit_source_frontier import section_bytes
 assert ev['initial_harness_error_sha256']==sha(out/'initial-harness-error.log')
 assert ev['source_owned_numeric_bytes']==r['source_owned_numeric_bytes']==240 and ev['pcrel_pointer_words']==4
 for name,address,length in [('local',0x38460,88),('high',0xbd6f0,32),('low',0xbd710,32),('even',0xbd730,40),('odd',0xbd758,48)]:
  data=section_bytes(out/'native_atan.o','.r1.math.atan_'+name,executable=False);assert len(data)==length and data==app.read_bytes()[address-0x27000:address-0x27000+length]
 for address,pc,target in [(0x384b8,0x3838e,0xbd758),(0x384bc,0x383b0,0xbd730),(0x384c0,0x38406,0xbd710),(0x384c4,0x3842e,0xbd6f0)]:assert (int.from_bytes(app.read_bytes()[address-0x27000:address-0x27000+4],'little')+pc)&0xffffffff==target
 for address,length in [(0x38460,88),(0x384b8,16),(0xbd6f0,152)]:assert bytes(read(out/f'ghidra-{address:x}.json')['data'])==app.read_bytes()[address-0x27000:address-0x27000+length]
 previous=read(BASE/'native-tanf/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies']+['atan'] and g['remaining_consumer_bodies_native']==5
 assert g['helper_observations']=={side:{**values,'atan':56,**({'class64':20,'subtract':744,'reverse_subtract':488,'polynomial':108,'fabs_core':64,'self64':16,'low64':12} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='58c245da834ecb8ccb85f447a4ee51843af972ed9196ed78093fe7c4c86401d9'
 for flag in ['runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','independent_calls_reset_xpsr']:assert g[flag]
 for key,p in [('report_sha256',BASE/'native-float-bits/report.json'),('object_sha256',BASE/'native-float-bits/native_float_bits.o'),('math_report_sha256',BASE/'native-formatter-math/report.json'),('math_object_sha256',BASE/'native-formatter-math/native-formatter-math.o')]:assert g[key]==sha(p)
 print('Native atan: direct, consumer, source/runtime/data evidence authenticated; full ABI and image identity remain gated')
if __name__=='__main__':audit()
