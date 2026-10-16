#!/usr/bin/env python3
"""Authenticate native atan source, numeric data and bounded execution receipts."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 out=BASE/'native-log';r=read(out/'verification.json');g=read(out/'consumer-verification.json');ev=read(out/'evidence.json');report=read(out/'report.json');bp=BASE/'native-log-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['trace_sha256']=='6cee6f5e004aac3a38d882022be81739d8035b07ac2ab355d583eaaff29ec2b2'
 assert r['errno_writes_per_side']=={'log':18688}
 assert r['comparisons']==37716 and r['counts']=={'log':37716}
 assert r['application_sha256']==g['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for flag in ['all_binary64_exponents','both_signs','all_four_rounding_modes','selected_values_all_fz_dn_initial_inexact_controls','initial_inexact_flag_zero_and_one_selected_values','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_log_and_dependencies','independent_calls_reset_xpsr','runtime_no_unresolved']:assert r[flag]
 assert 'all_binary32_and_binary64_exponents' not in r and not r['instruction_identity'] and not g['instruction_identity']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_log.py') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_log_consumers.py')
 assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_log.o')
 for receipt in [r,g]:
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-log-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked']
 assert set(report['units'][0]['undefined'])=={'r1_binary64_compare_reverse_flags','r1_binary64_reverse_subtract_bits','r1_binary64_subtract_bits','r1_format_double_add_bits','r1_format_double_divide_bits','r1_format_double_multiply_bits','r1_math_divzero64','r1_math_invalid64','r1_math_self_add64','r1_native_errno_set','r1_native_polynomial','r1_signed32_to_binary64_bits'}
 for p,h in r['evidence'].items():assert sha(out/p)==h,p
 raw=read(out/'rea-39320.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
 assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['ranges']==[{'start':'0x39320','end':'0x39687'}]
 assert bytes(read(out/'ghidra-39320.json')['data'])==app.read_bytes()[0x12320:0x12688]
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13'
 assert ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x00039320') and not ev['locked_ownership_changed'] and ev['new_source_routes']==1 and ev['native_body_bytes']==872
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(out/'pseudocode-39320.c.txt')
 from audit_source_frontier import section_bytes
 assert ev['source_owned_numeric_bytes']==r['source_owned_numeric_bytes']==144 and ev['shared_existing_numeric_bytes']==r['shared_existing_numeric_bytes']==8 and ev['unique_new_numeric_bytes']==r['unique_new_numeric_bytes']==136
 for name,address,length in [('prefix',0x39688,48),('suffix',0x396bc,32),('zero',0xbdb50,8),('even',0xbd810,24),('odd',0xbd828,32)]:
  data=section_bytes(out/'native_log.o','.r1.math.log_'+name,executable=False);assert len(data)==length and data==app.read_bytes()[address-0x27000:address-0x27000+length]
 assert section_bytes(out/'native_log.o','.r1.math.log_zero',executable=False)==section_bytes(BASE/'native-trig-reduce/native_trig_reduce.o','.r1.math.trig_reduce_table',executable=False)[8:16]
 assert ev['pointer_contracts']==[dict(address=hex(a),pc=hex(pc),target=hex(t)) for a,pc,t in [(0x396b8,0x393f8,0xbdb50),(0x396dc,0x3953e,0xbd810),(0x396e0,0x39560,0xbd828)]]
 for contract in ev['pointer_contracts']:
  a=int(contract['address'],16);assert (int.from_bytes(app.read_bytes()[a-0x27000:a-0x27000+4],'little')+int(contract['pc'],16))&0xffffffff==int(contract['target'],16)
 for address,length in [(0x39688,92),(0xbdb50,8),(0xbd810,56)]:assert bytes(read(out/f'ghidra-{address:x}.json')['data'])==app.read_bytes()[address-0x27000:address-0x27000+length]
 previous=read(BASE/'native-exp/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies']+['log'] and g['remaining_consumer_bodies_native']==2
 assert g['helper_observations']=={side:{**values,'log':56,**({'signed_to64':32,'subtract':472,'reverse_subtract':272,'polynomial':60,'errno':36,'reverse':0,'divzero64':0,'self64':0,'invalid64':12} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='d1c9c764946d52752e65c10729acc2f82650c8a0b2f4db49a4140e14d39d3b2e'
 for flag in ['runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','independent_calls_reset_xpsr']:assert g[flag]
 for key,p in [('report_sha256',BASE/'native-float-bits/report.json'),('object_sha256',BASE/'native-float-bits/native_float_bits.o'),('math_report_sha256',BASE/'native-formatter-math/report.json'),('math_object_sha256',BASE/'native-formatter-math/native-formatter-math.o')]:assert g[key]==sha(p)
 print('Native log: direct, consumer, source/runtime/data evidence authenticated; full ABI and image identity remain gated')
if __name__=='__main__':audit()
