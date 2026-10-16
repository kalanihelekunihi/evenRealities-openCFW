#!/usr/bin/env python3
"""Audit native selection/rounding/absolute-value source admission."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-math-selection';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-math-selection-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    entries={0x28364:54,0x389f0:98,0x39220:98,0x39290:72,0x392d8:72,0x390f0:20,0x620f4:24,0x98eca:16}
    assert r['comparisons']==483940 and r['counts']=={'compare':1508,'ceilf':98304,'floorf':98304,'fmaxf':24128,'fminf':24128,'fabs':69632,'fabs_core':69632,'compare_absf':98304}
    for flag in ('all_binary32_and_binary64_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','preexisting_inexact_flag','compare_return_and_apsr_nzcvq_checked','compare_initial_q_zero_and_one','core_fabs_d0_side_result_checked','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','runtime_no_unresolved'):assert r[flag]
    assert not r['instruction_identity'] and r['application_sha256']==app_hash and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_selection.py')
    assert r['trace_sha256']=='8d5a0fa475e256f2d8efe1b5a6060c256ee145bf4565fea3fa8c6632a91d0502'
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_math_selection.o')
    assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-math-selection-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols'] and not report['units'][0]['undefined']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-math-selection/report.json','native-math-sqrt-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a,n in entries.items():
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        if a!=0x98eca:
            assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==n
        else:
            assert q['error']['details']['diagnostics']['target_sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['error']['code']=='invalid_request' and 'No procedure exists at the requested address: 0x98eca' in q['error']['details']['issues'][0]['message']
            gap=ev['metadata_gaps']['0x00098eca'];assert sha(ROOT/gap['analysis_elf'])==gap['analysis_elf_sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
            for key in ['rea_result','ghidra_function_result','disassembly']:assert sha(out/gap[key])==gap[key+'_sha256']
            assert 'Function not found' in read(out/gap['ghidra_function_result'])['error']
            disassembly=(out/gap['disassembly']).read_text();assert all(word in disassembly for word in ['98eca:','vcmpe.f32','vmrs','bcs.n','vneg.f32','98ed8:','bx'])
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['body_count']==8 and ev['native_body_bytes']==454
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in entries]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==8
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    from audit_source_frontier import section_bytes
    for section,a,n in [('.r1.math.ceilf_data',0x38a54,8),('.r1.math.floorf_data',0x39284,12)]:
        data=section_bytes(out/'native_math_selection.o',section,executable=False);assert data==bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        assert r['source_owned_data_spans'][section]==dict(address=hex(a),bytes=n,sha256=hashlib.sha256(data).hexdigest())
    assert graph['comparisons']==1952 and graph['consumer_counts']=={**read(BASE/'native-math-sqrt/consumer-verification.json')['consumer_counts'],'fmaxf':144,'fminf':144,'fabs':56,'compare_absf':56}
    assert graph['remaining_consumer_bodies_native']==19 and graph['source_consumer_bodies']==['sqrt','sqrtf','ceilf','floorf','fmaxf','fminf','fabs','compare_absf']
    assert graph['trace_sha256']=='7c23c402e208af3aecce389f045c47168b75230c186d1173d43eef2002d324b5' and graph['application_sha256']==app_hash and not graph['instruction_identity']
    assert graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_selection_consumers.py') and graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    previous=read(BASE/'native-math-sqrt/consumer-verification.json')['helper_observations'];extra={'ceilf':56,'floorf':56,'fmaxf':144,'fminf':144,'fabs':56,'fabs_core':84,'compare_absf':56}
    assert graph['helper_observations']=={side:{**values,**extra,'compare':288 if side=='native' else 0} for side,values in previous.items()}
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_math_verification.ld')==ev['parent_layout_sha256']
if __name__=='__main__':audit()
