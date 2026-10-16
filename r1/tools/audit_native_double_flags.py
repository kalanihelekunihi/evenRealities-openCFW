#!/usr/bin/env python3
"""Strict native binary64 physical comparison contract admission."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-double-flags';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-double-flags-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==312896 and r['counts']=={'forward':156448,'reverse':156448}
    for flag in ('all_binary64_exponents','both_signs','equal_high_and_low_word_variants','seeded_random_pairs','both_initial_q_values','all_r0_r1_r2_r3_and_apsr_nzcvq_checked','r12_preserved','lr_preserved','return_stack_callee_saved_and_fpscr_checked','runtime_no_unresolved'):assert r[flag]
    assert r['flag_counts']=={'1610612736':34862,'1744830464':34862,'2415919104':17030,'2550136832':17030,'2147483648':30386,'2281701376':30386,'536870912':30386,'671088640':30386,'0':13377,'134217728':13377,'805306368':17013,'939524096':17013,'2684354560':13394,'2818572288':13394}
    assert r['trace_sha256']=='dfd36b0ebd5ccb727c6b83d2fbb6b44356e661f152ae09054d9c1e43b7df9086' and not r['instruction_identity'] and r['application_sha256']==app_hash
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_double_flags.o') and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_double_flags.py')
    assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-double-flags-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols'] and not report['units'][0]['undefined']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-double-flags/report.json','native-math-selection-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a in [0x27f0c,0x27f3c]:
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+48]
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==48
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['body_count']==2 and ev['native_body_bytes']==96
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in [0x27f0c,0x27f3c]]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==2
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    previous=read(BASE/'native-math-selection/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==19 and graph['source_consumer_bodies']==previous['source_consumer_bodies']
    assert graph['helper_observations']=={side:{**values,'forward':136,'reverse':84} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='a64d6fd4ed9e0bf303ad3a97c3d733845180db00fc333632e2c7999a10df0d7a' and graph['application_sha256']==app_hash and not graph['instruction_identity']
    assert graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_double_flags_consumers.py') and graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    assert graph['layout_sha256']==sha(ROOT/graph['layout']) and graph['parent_layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_math_verification.ld')
if __name__=='__main__':audit()
