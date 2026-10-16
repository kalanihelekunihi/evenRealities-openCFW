#!/usr/bin/env python3
"""Audit recovered expf/tanhf kernels, shared-tail ownership and table offsets."""
import csv,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-expf-tanhf';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-expf-tanhf-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==672832 and r['counts']=={'expf':336416,'tanhf':336416} and r['errno_writes_per_side']=={'expf':127084,'tanhf':0}
    for flag in ('all_binary32_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','initial_inexact_flag_zero_and_one','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_expf_tanhf_and_dependencies','runtime_no_unresolved'):assert r[flag]
    assert r['trace_sha256']=='d600dd3fac9505a166f324e82fb0f63bdaa8604644abae6137e0048e4ec11d3d' and r['application_sha256']==app_hash and not r['instruction_identity'] and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_expf_tanhf.py')
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_expf_tanhf.o') and r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-expf-tanhf-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-expf-tanhf/report.json','native-math-special-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a,n,ranges in [(0x38f08,426,[dict(start='0x38f08',end='0x390b1')]),(0x3b328,214,[dict(start='0x3b328',end='0x3b3f7'),dict(start='0x3bac8',end='0x3bacd')])]:
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==n and q['normalized_result']['body']['ranges']==ranges
    for a,n in [(0x38f08,426),(0x3b328,208),(0x3bac8,6)]:assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['new_source_routes']==2 and ev['full_native_body_bytes']==640 and ev['unique_new_native_body_bytes']==634 and ev['reused_tail_bytes']==6
    assert ev['reused_tail_entry']=='0x0003bac8' and ev['reused_tail_report']=='native-math-special/report.json' and ev['source_owned_numeric_bytes']==116
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in [0x38f08,0x3b328]]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==2
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    offsets=bytes(read(out/ev['table_pointer_literal_file'])['data']);assert sha(out/ev['table_pointer_literal_file'])==ev['table_pointer_literal_sha256'] and offsets==app.read_bytes()[0x120d4:0x120e0]
    assert ev['table_pointer_contracts']==[dict(literal=hex(a),pc_base=hex(pc),encoded_offset=hex(off),resolved_target=hex(target)) for (a,pc,target),off in zip([(0x390d4,0x38f86,0xbd7f0),(0x390d8,0x38f92,0xbd800),(0x390dc,0x38fa2,0xbd7e0)],struct.unpack('<3I',offsets))]
    for row in ev['table_pointer_contracts']:assert int(row['pc_base'],16)+int(row['encoded_offset'],16)==int(row['resolved_target'],16)
    from audit_source_frontier import section_bytes
    for section,a,n in [('expf_coeff',0x390b4,32),('expf_scale',0x390e0,16),('expf_tables',0xbd7e0,48),('tanhf_coeff',0x3b3f8,20)]:
        data=section_bytes(out/'native_expf_tanhf.o','.r1.math.'+section,executable=False);assert data==bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
        assert r['source_owned_data_spans'][section]==dict(address=hex(a),bytes=n,sha256=hashlib.sha256(data).hexdigest())
    previous=read(BASE/'native-math-special/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==13 and graph['source_consumer_bodies']==previous['source_consumer_bodies']+['expf','tanhf']
    assert graph['helper_observations']=={side:{**values,'expf':72,'tanhf':56,**({'class32':132,'errno':112,'self32':24,'high32':0,'low32':40,'expf':56} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='3f1d7906378828381771f9cdb5495f91bd2dde757572e7f9414de296a5041bb5' and graph['application_sha256']==app_hash and not graph['instruction_identity'] and graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_expf_tanhf_consumers.py')
    assert graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
if __name__=='__main__':audit()
