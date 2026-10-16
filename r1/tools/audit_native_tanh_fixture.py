#!/usr/bin/env python3
"""Audit the tanh body candidate with an explicit native expm1 fixture."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-tanh';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');report=read(OUT/'report.json');bp=BASE/'native-tanh-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==37316 and r['counts']=={'tanh':37316} and r['errno_writes_per_side']=={'tanh':0} and r['trace_sha256']=='973f3a6a6eb6c2182814014d805cede8cbb6880004f9279c4c9ba208b5395024'
 assert g['comparisons']==1952 and g['trace_sha256']=='872d1265fdd5ba2929b1b83b50585856d5551cbff045dcfe342fad6c5ba315cf' and g['helper_observations']['compiled_entries']['tanh']==56
 for flag in ['all_binary64_exponents','both_signs','all_four_rounding_modes','selected_values_all_fz_dn_initial_inexact_controls','initial_inexact_flag_zero_and_one_selected_values','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_tanh_body','independent_calls_reset_xpsr']:assert r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_tanh_fixture.py') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_tanh_fixture_consumers.py')
 for receipt in [r,g]:
  assert not receipt['runtime_no_unresolved'] and not receipt['source_expm1_complete'] and receipt['native_expm1_fixture'] and receipt['unresolved_source_provider']=='r1_native_expm1' and not receipt['instruction_identity']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-tanh-runtime.o')==bundle['linked_sha256']
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert bundle['undefined_symbols']==['r1_native_expm1'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert r['report_sha256']==sha(OUT/'report.json') and r['object_sha256']==sha(OUT/'native_tanh.o')
 for p,h in r['evidence'].items():assert sha(OUT/p)==h,p
 for a,n in [(0x3b1c8,306),(0x3b538,20),(0x3b300,40)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
 from audit_source_frontier import section_bytes
 assert section_bytes(OUT/'native_tanh.o','.r1.math.tanh_local',executable=False)==app.read_bytes()[0x14300:0x14328]
 raw=read(OUT/'rea-3b1c8.json')['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and raw['normalized_result']['body']['ranges']==[{'start':'0x3b1c8','end':'0x3b2f9'},{'start':'0x3b538','end':'0x3b54b'}]
 dep=ev['source_dependency_gate'];assert dep['evidence_sha256']==sha(OUT/'rea-expm1-3b5c0.json') and dep['rea_ranges']==read(OUT/'rea-expm1-3b5c0.json')['structuredContent']['normalized_result']['body']['ranges'] and not dep['external_blocker']
 assert ev['new_source_routes_admitted']==0 and ev['native_main_bytes']==306 and ev['shared_existing_tail_bytes']==20 and ev['native_body_bytes']==326 and ev['source_owned_numeric_bytes']==r['source_owned_numeric_bytes']==40
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13' and ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x0003b1c8') and not ev['locked_ownership_changed']
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-3b1c8.c.txt')
 print('Tanh candidate authenticated: 37316 direct/1952 graph cases with native expm1 fixture; source expm1 gate remains open')
if __name__=='__main__':audit()
