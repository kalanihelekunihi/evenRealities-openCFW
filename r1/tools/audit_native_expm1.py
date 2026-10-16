#!/usr/bin/env python3
"""Audit source expm1 and source-dependent tanh, preserving the fixture history."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-expm1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_tanh_fixture import audit as fixture_audit
 fixture_audit()
 r=read(OUT/'verification.json');t=read(BASE/'native-tanh/source-verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');rp=OUT/'report.json';report=read(rp);bp=BASE/'native-expm1-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==37696 and r['counts']=={'expm1':37696} and r['errno_writes_per_side']=={'expm1':8648} and r['trace_sha256']=='135629ef3b2fe832fe885d7e710826d4d8113763b1e66929328922b778e6213f'
 assert t['comparisons']==37316 and t['trace_sha256']=='973f3a6a6eb6c2182814014d805cede8cbb6880004f9279c4c9ba208b5395024' and t['errno_writes_per_side']=={'tanh':0}
 for receipt,driver in [(r,'verify_native_expm1.py'),(t,'verify_native_tanh_source.py'),(g,'verify_native_expm1_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and receipt['runtime_no_unresolved'] and not receipt['instruction_identity']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-expm1-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
  for p,h in receipt.get('evidence',{}).items():assert sha((OUT if receipt is r else BASE/'native-tanh')/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked'] and not bundle['original_instruction_identity'] and 'PROVIDE(r1_native_expm1' not in (ROOT/g['layout']).read_text()
 assert t['source_expm1_complete'] and g['source_expm1_complete'] and not t['native_expm1_fixture'] and not g['native_expm1_fixture']
 for rp2 in [report,bundle]:
  for p,h in rp2['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 for receipt,directory,obj in [(r,OUT,'native_expm1.o'),(t,BASE/'native-tanh','native_tanh.o')]:assert receipt['report_sha256']==sha(directory/'report.json') and receipt['object_sha256']==sha(directory/obj)
 for receipt in [r,t]:
  for flag in ['all_binary64_exponents','both_signs','all_four_rounding_modes','selected_values_all_fz_dn_initial_inexact_controls','initial_inexact_flag_zero_and_one_selected_values','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','independent_calls_reset_xpsr']:assert receipt[flag]
 assert r['actual_source_expm1_and_dependencies'] and t['actual_source_tanh_body']
 raw=read(OUT/'rea-3b5c0.json')['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and raw['normalized_result']['body']['ranges']==[{'start':'0x3b5c0','end':'0x3b9e7'},{'start':'0x3ba98','end':'0x3bab3'}]
 for a,n in [(0x3b5c0,1064),(0x3ba98,28),(0x3b9e8,176),(0xbdb28,40)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
 from audit_source_frontier import section_bytes
 for name,a,n in [('prefix',0x3b9e8,112),('suffix',0x3ba5c,60),('polynomial',0xbdb28,40)]:assert section_bytes(OUT/'native_expm1.o','.r1.math.expm1_'+name,executable=False)==app.read_bytes()[a-0x27000:a-0x27000+n]
 assert (int.from_bytes(app.read_bytes()[0x14a58:0x14a5c],'little')+0x3b7ac)&0xffffffff==0xbdb28
 assert section_bytes(OUT/'native_expm1.o','.r1.math.expm1_polynomial',executable=False)[-8:]==section_bytes(BASE/'native-trig-reduce/native_trig_reduce.o','.r1.math.trig_reduce_table',executable=False)[:8]
 assert ev['new_source_routes']==2 and ev['expm1_numeric_bytes']==r['source_owned_numeric_bytes']==212 and ev['unique_new_expm1_numeric_bytes']==r['unique_new_numeric_bytes']==204 and ev['shared_existing_numeric_bytes']==r['shared_existing_numeric_bytes']==8
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13' and not ev['locked_ownership_changed']
 assert ev['ownership_rows']==[row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry'] in ['0x0003b5c0','0x0003b1c8']]
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-3b5c0.c.txt') and ev['initial_overlap_error_sha256']==sha(OUT/'initial-layout-overlap.log')
 previous=read(BASE/'native-tanh/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies'] and g['remaining_consumer_bodies_native']==4
 assert g['helper_observations']=={side:{**values,'expm1':20,**({'signed_to64':68,'to_signed':8,'subtract':616,'reverse_subtract':364,'polynomial':88,'expm1':0} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='021d7cd9158f198bb3ffdfc41b8f73a0ac533bdaea0d0f1950a01bbb23e58fee'
 print('Source expm1 and tanh authenticated: no native expm1 fixture; full ABI/placement/image gates remain open')
if __name__=='__main__':audit()
