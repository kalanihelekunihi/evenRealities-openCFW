#!/usr/bin/env python3
"""Audit native public round/roundf source and complete noncontiguous spans."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-math-round';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-math-round-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==376832 and r['counts']=={'round':81920,'roundf':294912} and r['halfway_integer_range']==[-2048,2047]
    for flag in ('all_binary32_and_binary64_exponents','both_signs','halfway_and_adjacent_bits','all_four_rounding_modes','roundf_flush_to_zero_and_default_nan_modes','roundf_preexisting_inexact_flag','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_integral_round_subtract_add_and_flags','runtime_no_unresolved'):assert r[flag]
    assert r['trace_sha256']=='5725cb9ef79dcfadcd9ee0ed69d14a5539f9f33974210b4e3c2fcf4679647726' and r['application_sha256']==app_hash and not r['instruction_identity']
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_math_round.o') and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_round.py')
    assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-math-round-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-math-round/report.json','native-double-directed-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a,n in [(0x3ac88,192),(0x3ad68,154)]:
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==n
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        if a==0x3ac88:
            assert q['normalized_result']['body']['ranges']==[dict(start='0x3ac88',end='0x3ace9'),dict(start='0x3acec',end='0x3ad49')] and q['normalized_result']['body']['span_bytes']==194 and q['normalized_result']['body']['non_contiguous']
    noncontiguous=ev['noncontiguous_double_body'];assert noncontiguous['body_bytes']==192 and noncontiguous['span_bytes']==194 and noncontiguous['excluded_gap']==dict(address='0x0003acea',bytes=2)
    assert [(int(row['address'],16),row['bytes']) for row in noncontiguous['ranges']]==[(0x3ac88,98),(0x3acec,94)]
    for row in noncontiguous['ranges']:
        p=out/row['file'];a=int(row['address'],16);assert sha(p)==row['sha256'] and bytes(read(p)['data'])==app.read_bytes()[a-0x27000:a-0x27000+row['bytes']]
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['body_count']==2 and ev['native_body_bytes']==346 and ev['source_owned_data_bytes']==24
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in [0x3ac88,0x3ad68]]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==2
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    from audit_source_frontier import section_bytes
    data=section_bytes(out/'native_math_round.o','.r1.math.round_data',executable=False);assert data==bytes(read(out/'ghidra-3ad50.json')['data'])==app.read_bytes()[0x13d50:0x13d68] and len(data)==r['source_owned_data_bytes']==24 and hashlib.sha256(data).hexdigest()==r['source_owned_data_sha256']
    previous=read(BASE/'native-double-directed/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==15 and graph['source_consumer_bodies']==previous['source_consumer_bodies']+['round','roundf']
    assert graph['helper_observations']=={side:{**values,'round':56,'roundf':56,**({'subtract':800,'integral32':0,'integral64':0,'forward':24,'reverse':28} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='e846b31e4031abf45daee1a2a6f4996694d4cc000ae1535bf5dac1e0efcf9a77' and graph['application_sha256']==app_hash and not graph['instruction_identity']
    assert graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_round_consumers.py') and graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
if __name__=='__main__':audit()
