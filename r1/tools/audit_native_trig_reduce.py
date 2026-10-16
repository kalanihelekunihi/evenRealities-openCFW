#!/usr/bin/env python3
"""Audit the separately gated trig reducer candidate, without frontier promotion."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-trig-reduce';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 r=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());bpath=BASE/'native-trig-reduce-runtime/report.json';b=json.loads(bpath.read_text())
 assert v['comparisons']==212992 and v['trace_sha256']=='1813170576092c526368c8e632810db22e57b560aed0f72625168893003d7d51'
 for key,p in [('report_sha256',OUT/'report.json'),('object_sha256',OUT/'native_trig_reduce.o'),('layout_sha256',ROOT/'r1/source-config/runtime/native_trig_reduce_verification.ld'),('driver_sha256',ROOT/'r1/tools/verify_native_trig_reduce.py'),('application_sha256',ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')]:assert v[key]==sha(p),key
 for name,h in v['evidence'].items():assert sha(OUT/name)==h
 for report in [r,b]:
  for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in b['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in b['objects'].items():assert sha(BASE/p)==h,p
 assert not r['units'][0]['undefined'] and not b['undefined_symbols'] and sha(bpath.parent/'native-trig-reduce-runtime.o')==b['linked_sha256']
 assert not v['instruction_identity'] and not b['application_linked'] and v['source_owned_numeric_bytes']==68
 for key in ['all_binary32_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','initial_inexact_flag_zero_and_one','independent_incoming_s0','return_fpscr_quadrant_write_order_stack_and_callee_registers_checked']:assert v[key]
 ev=json.loads((OUT/'evidence.json').read_text());g=json.loads((OUT/'consumer-verification.json').read_text());previous=json.loads((BASE/'native-atan2f/consumer-verification.json').read_text())
 assert ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13'
 assert ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0003bb04')
 assert ev['new_source_routes']==1 and ev['native_body_bytes']==316 and not ev['locked_ownership_changed']
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-3bb04.c.txt')
 assert ev['harness_counterexample_sha256']==sha(OUT/'harness-counterexample.json')
 raw=json.loads((OUT/'rea-3bb04.json').read_text())['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 assert g['comparisons']==1952 and g['consumer_counts']==previous['consumer_counts'] and g['source_consumer_bodies']==previous['source_consumer_bodies'] and g['remaining_consumer_bodies_native']==9
 assert g['helper_observations']=={side:{**values,'trig_reduce':48} for side,values in previous['helper_observations'].items()}
 assert g['trace_sha256']=='f61fa27ae528dacde61f6a2d83d51df75e0e1650977fc7773babdcc2df208e86' and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_trig_reduce_consumers.py')
 assert g['runtime_report_sha256']==sha(bpath) and g['runtime_object_sha256']==b['linked_sha256'] and g['application_sha256']==v['application_sha256'] and not g['instruction_identity']
 assert g['layout_sha256']==sha(ROOT/g['layout']) and g['parent_layouts']==ev['parent_layouts']
 for p,h in g['parent_layouts'].items():assert sha(ROOT/p)==h,p
 for flag in ['independent_calls_reset_xpsr','reducer_raw_r0_r1_s0_slots_preserved','runtime_no_unresolved','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','all_four_fpscr_rounding_modes']:assert g[flag]
 for key,p in [('report_sha256',BASE/'native-float-bits/report.json'),('object_sha256',BASE/'native-float-bits/native_float_bits.o'),('math_report_sha256',BASE/'native-formatter-math/report.json'),('math_object_sha256',BASE/'native-formatter-math/native-formatter-math.o')]:assert g[key]==sha(p)
 print('Trig reducer: 212992 direct cases, 1952 consumer cases and zero-undefined partial runtime authenticated; ABI/image gates remain open')
if __name__=='__main__':audit()
