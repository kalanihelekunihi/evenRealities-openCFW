#!/usr/bin/env python3
"""Audit source/native double ceil/floor contracts and owned constant spans."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-double-directed';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-double-directed-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==403328 and r['counts']=={'ceil':201664,'floor':201664}
    for flag in ('all_binary64_exponents','both_signs','all_low16_fraction_words_at_exponent20','high_low_carry_samples','all_four_rounding_modes','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_add_subtract_and_flag_providers','runtime_no_unresolved'):assert r[flag]
    assert r['trace_sha256']=='883f4b2f23d00c1bb5e1fed4af20b7522edcbb0927087bcaefd897456f26daa0' and r['application_sha256']==app_hash and not r['instruction_identity']
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_double_directed.o') and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_double_directed.py')
    assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-double-directed-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-double-directed/report.json','native-double-flags-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a in [0x388d8,0x39108]:
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+252]
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==252
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['body_count']==2 and ev['native_body_bytes']==504 and ev['source_owned_data_bytes']==48
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in [0x388d8,0x39108]]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==2
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    from audit_source_frontier import section_bytes
    for section,a in [('.r1.math.ceil_data',0x389d8),('.r1.math.floor_data',0x39208)]:
        data=section_bytes(out/'native_double_directed.o',section,executable=False);assert data==bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+24]
        assert r['source_owned_data_spans'][section]==dict(address=hex(a),bytes=24,sha256=hashlib.sha256(data).hexdigest())
    previous=read(BASE/'native-double-flags/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==17 and graph['source_consumer_bodies']==previous['source_consumer_bodies']+['ceil','floor']
    assert graph['helper_observations']=={side:{**values,'ceil':56,'floor':56,**({'forward':80} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='bc5cdab0bfc616ff713bf9eb7c0133c43ea2b9e67dcce3687545ac062cb1e6e8' and graph['application_sha256']==app_hash and not graph['instruction_identity']
    assert graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_double_directed_consumers.py') and graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
if __name__=='__main__':audit()
