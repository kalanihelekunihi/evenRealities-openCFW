#!/usr/bin/env python3
"""Audit shared special-value entry contracts without promoting parent bodies."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-math-special';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-math-special-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    counts={'divzero64':32,'self64':69632,'add64':4292,'invalid64':32,'high64':32,'low64':32,'divzero32':32,'self32':196608,'add32':39040,'invalid32':32,'high32':32,'low32':32}
    assert r['comparisons']==309828 and r['counts']==counts and r['trace_sha256']=='0f9fca43f711506f29e36bd2392625c58a17bedc4b1fd62690221c98db1c8391'
    for flag in ('all_binary32_and_binary64_exponents','both_signs','seeded_random_pairs','all_four_rounding_modes','float_flush_to_zero_and_default_nan_modes','initial_inexact_flag_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_double_add_multiply_divide','source_float_vfp_arithmetic','runtime_no_unresolved'):assert r[flag]
    assert r['application_sha256']==app_hash and not r['instruction_identity'] and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_special.py') and r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_math_special.o')
    assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-math-special-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-math-special/report.json','native-math-round-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    entries={0x3b508:28,0x3b538:20,0x3b54c:20,0x3b560:24,0x3b580:24,0x3b5a0:24,0x3bab4:14,0x3bac8:6,0x3bace:6,0x3bad4:10,0x3bae4:10,0x3baf4:10};owners={0x3b538:0x3b1c8,0x3b54c:0x399d0,0x3b560:0x399d0,0x3bac8:0x3b328,0x3bad4:0x3b048}
    for a,n in entries.items():
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        if a==0x3bace:
            assert q['error']['code']=='invalid_request' and q['error']['details']['diagnostics']['target_sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and 'No procedure exists' in q['error']['details']['issues'][0]['message']
            assert 'Function not found' in read(out/'ghidra-function-3bace.json')['error']
            text=(out/'disassembly-3bace.txt').read_text();assert all(word in text for word in ['3bace:','vadd.f32','3bad2:','bx'])
        else:
            assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(owners.get(a,a))
            assert any(int(row['start'],16)<=a and int(row['end'],16)>=a+n-1 for row in q['normalized_result']['body']['ranges'])
            if a not in owners:assert q['normalized_result']['body']['total_bytes']==n
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['leaf_entry_count']==12 and ev['routed_leaf_instruction_bytes']==196 and ev['source_owned_data_bytes']==56
    assert ev['shared_entries']=={hex(a):hex(o) for a,o in owners.items()} and ev['missing_live_function_metadata']==['0x3bace'] and ev['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
    for path,digest in ev['metadata_gap_evidence'].items():assert sha(out/path)==digest,path
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in entries]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==12
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    from audit_source_frontier import section_bytes
    for section,a,n in [('divzero64',0x3b528,16),('invalid64',0x3b578,8),('high64',0x3b598,8),('low64',0x3b5b8,8),('divzero32',0x3bac4,4),('invalid32',0x3bae0,4),('high32',0x3baf0,4),('low32',0x3bb00,4)]:
        data=section_bytes(out/'native_math_special.o','.r1.math.'+section+'_data',executable=False);assert data==bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        assert r['source_owned_data_spans'][section]==dict(address=hex(a),bytes=n,sha256=hashlib.sha256(data).hexdigest())
    previous=read(BASE/'native-math-round/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==15 and graph['source_consumer_bodies']==previous['source_consumer_bodies']
    calls={'divzero64':8,'self64':20,'add64':0,'invalid64':20,'high64':4,'low64':20,'divzero32':16,'self32':36,'add32':0,'invalid32':52,'high32':4,'low32':48}
    assert graph['helper_observations']=={side:{**values,**calls} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='704c25125ceecb9ab9e15546bc140fe5e67f4ead7e9d9af536fac9041d9c4483' and graph['application_sha256']==app_hash and not graph['instruction_identity'] and graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_special_consumers.py')
    assert graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
    spans=read(out/'instruction-span-verification.json');assert not spans['instruction_identity'] and not spans['image_integration_proven'] and spans['report_sha256']==sha(out/'report.json') and spans['object_sha256']==sha(out/'native_math_special.o') and spans['driver_sha256']==sha(ROOT/'r1/tools/verify_native_math_special_spans.py') and spans['application_sha256']==app_hash
    assert len(spans['compiled_instruction_byte_spans'])==2
    for row,a,name,digest in zip(spans['compiled_instruction_byte_spans'],[0x3bac8,0x3bace],['r1_math_self_add32','r1_math_add32'],['f9eab617bc9a82ea9fe3a5e4a5b0f3b9bee4d8d4ebd271074ab8ebca954b71a9','8f8fe57ae09b74be4d9432839ced1dac7baa02c4300dacbf4f1427ab7cd22586']):
        assert row==dict(entry=f'0x{a:08x}',bytes=6,object='native-math-special/native_math_special.o',section='.text.'+name,sha256=digest,relocations=False,image_placement_proven=False)
        data=section_bytes(BASE/row['object'],row['section']);assert len(data)==6 and hashlib.sha256(data).hexdigest()==digest and data==app.read_bytes()[a-0x27000:a-0x27000+6]
    return spans['compiled_instruction_byte_spans']
if __name__=='__main__':audit()
