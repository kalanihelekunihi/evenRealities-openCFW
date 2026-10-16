#!/usr/bin/env python3
"""Audit native atan2f classification words, live FP state and quadrant source."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-atan2f';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-atan2f-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==942112 and r['counts']=={'atan2f':942112}
    for flag in ('all_binary32_exponents','both_signs','seeded_random_pairs','all_four_rounding_modes','float_flush_to_zero_and_default_nan_modes','initial_inexact_flag_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_atan2f_and_dependencies','source_float_vfp_arithmetic','all_quadrant_signs','exponent_gap_boundaries','signed_zero_and_infinity_pairs','runtime_no_unresolved'):assert r[flag]
    assert 'all_binary32_and_binary64_exponents' not in r
    assert ev['coverage_label_counterexample_sha256']==sha(out/'coverage-label-counterexample.json')
    regression=read(out/'coverage-label-counterexample.json');assert regression['incorrect_label']=='all_binary32_and_binary64_exponents' and regression['actual_scope']=='binary32 exponent pairs only' and regression['trace_sha256']==r['trace_sha256'] and regression['comparisons']==r['comparisons']
    assert r['trace_sha256']=='595b817cb220e0defd3e1bf926f7be6f4a18d7e9b8b8b21056512ed6a86a433a' and r['application_sha256']==app_hash and not r['instruction_identity'] and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_atan2f.py')
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_atan2f.o') and r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-atan2f-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-atan2f/report.json','native-atanf-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    raw=read(out/'rea-384c8.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
    assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x384c8' and q['normalized_result']['body']['total_bytes']==594 and not q['normalized_result']['body']['non_contiguous']
    assert bytes(read(out/'ghidra-384c8.json')['data'])==app.read_bytes()[0x114c8:0x1171a]
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['new_source_routes']==1 and ev['native_body_bytes']==594 and ev['source_owned_numeric_bytes']==88
    assert ev['ownership_row']==next(row for row in csv.DictReader(ownership.open()) if row['image']=='application' and row['entry']=='0x000384c8')
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(out/'pseudocode-384c8.c.txt')
    from audit_source_frontier import section_bytes
    data=section_bytes(out/'native_atan2f.o','.r1.math.atan2f_data',executable=False);assert data==bytes(read(out/'ghidra-3871c.json')['data'])==app.read_bytes()[0x1171c:0x11774] and len(data)==r['source_owned_numeric_bytes']==88 and hashlib.sha256(data).hexdigest()==r['source_owned_data_sha256']
    previous=read(BASE/'native-atanf/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==9 and graph['source_consumer_bodies']==previous['source_consumer_bodies']+['atan2f']
    assert graph['helper_observations']=={side:{**values,'atan2f':144,**({'class32':48,'low32':24} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='d93bbf826049e376274dbc8ebfdb32e64535ad8a2ff1dee23741808814f74728' and graph['application_sha256']==app_hash and not graph['instruction_identity'] and graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_atan2f_consumers.py')
    assert graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
if __name__=='__main__':audit()
