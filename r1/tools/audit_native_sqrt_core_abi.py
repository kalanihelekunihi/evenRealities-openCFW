#!/usr/bin/env python3
"""Audit the raw-register sqrt wrapper used by native pow."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sqrt-core-abi';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');rp=OUT/'report.json';report=read(rp);bp=BASE/'native-sqrt-core-abi-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==37436 and r['counts']=={'sqrt_core_abi':37436} and r['trace_sha256']=='ebbf766b322434f0aa0887a4b06a0b88058435efe79ff46ecb42cb291a310078' and r['errno_writes_per_side']=={'sqrt_core_abi':0}
 for flag in ['all_binary64_exponents','both_signs','all_four_rounding_modes','selected_values_all_fz_dn_initial_inexact_controls','initial_inexact_flag_zero_and_one_selected_values','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_sqrt_wrapper_and_dependencies','raw_core_register_result_and_independent_d0','independent_calls_reset_xpsr','runtime_no_unresolved']:assert r[flag]
 for receipt,driver in [(r,'verify_native_sqrt_core_abi.py'),(g,'verify_native_sqrt_core_abi_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and receipt['runtime_no_unresolved'] and not receipt['instruction_identity']
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-sqrt-core-abi-runtime.o')==bundle['linked_sha256']
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert not bundle['undefined_symbols'] and not bundle['application_linked']
 for rp2 in [report,bundle]:
  for p,h in rp2['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-sqrt-core-abi/report.json','native-powf-runtime/report.json']}
 assert r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_sqrt_core_abi.o') and set(report['units'][0]['undefined'])=={'r1_binary64_square_root_bits','r1_native_errno_set'}
 for p,h in r['evidence'].items():assert sha(OUT/p)==h,p
 raw=read(OUT/'rea-90e8c.json')['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and raw['normalized_result']['body']['ranges']==[{'start':'0x90e8c','end':'0x90ef9'}]
 assert bytes(read(OUT/'ghidra-90e8c.json')['data'])==app.read_bytes()[0x69e8c:0x69efa] and ev['native_body_bytes']==110 and ev['new_source_routes']==1 and ev['source_owned_numeric_bytes']==r['source_owned_numeric_bytes']==0
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13' and ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x00090e8c') and not ev['locked_ownership_changed']
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-90e8c.c.txt')
 counter=read(OUT/'write-counter-counterexample.json');assert sha(OUT/'write-counter-counterexample.json')==ev['write_counter_counterexample_sha256'] and counter['comparisons']==r['comparisons'] and counter['trace_sha256']==r['trace_sha256']==read(OUT/'initial-verification.json')['trace_sha256'] and counter['incorrect_counter']=={'sqrt_core_abi':299488}
 previous=read(BASE/'native-powf-core/consumer-verification.json');assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies'] and g['remaining_consumer_bodies_native']==1
 assert g['helper_observations']=={side:{**values,'sqrt_core_abi':16,**({'sqrt64':0} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='32bd45f0235b9e78676af6a56f7f98fffdb1eaadd9130a830f81f8270d164f72'
 print('Raw-register sqrt wrapper and source dependencies authenticated; pow body and full image gates remain open')
if __name__=='__main__':audit()
