#!/usr/bin/env python3
"""Audit native float logarithm bodies, source numeric data and pointer contracts."""
import csv,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    out=BASE/'native-float-logs';report=read(out/'report.json');r=read(out/'verification.json');ev=read(out/'evidence.json');bp=BASE/'native-float-logs-runtime/report.json';bundle=read(bp);graph=read(out/'consumer-verification.json')
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert r['comparisons']==694592 and r['counts']=={'logf':347296,'log10f':347296} and r['errno_writes_per_side']=={'logf':171856,'log10f':171856}
    for flag in ('all_binary32_exponents','both_signs','all_rounding_flush_to_zero_default_nan_modes','initial_inexact_flag_zero_and_one','threshold_adjacent_bits','dense_numeric_grid','return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked','actual_source_logs_and_dependencies','runtime_no_unresolved'):assert r[flag]
    assert r['trace_sha256']=='65dbe13e2d00846183e97d54c37a423bcc07402b1c56bd5d4063fc5b40c978c5' and r['application_sha256']==app_hash and not r['instruction_identity'] and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_logs.py')
    assert r['report_sha256']==sha(out/'report.json') and r['object_sha256']==sha(out/'native_float_logs.o') and r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-float-logs-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
    assert bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-float-logs/report.json','native-expf-tanhf-runtime/report.json']}
    for rp in [report,bundle]:
        for path,digest in rp['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
    for path,digest in r['evidence'].items():assert sha(out/path)==digest,path
    for a,n in [(0x396e4,332),(0x39864,320)]:
        raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==n and not q['normalized_result']['body']['non_contiguous']
        assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert ev['ownership_sha256']==sha(ownership) and not ev['locked_ownership_changed'] and ev['new_source_routes']==2 and ev['native_body_bytes']==652 and ev['source_owned_numeric_bytes']==208
    assert ev['ownership_rows']==[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and int(row['entry'],16) in [0x396e4,0x39864]]
    assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and len(ev['pseudocode_slices'])==2
    for path,digest in ev['pseudocode_slices'].items():assert sha(out/path)==digest,path
    assert [(int(row['literal'],16),int(row['pc_base'],16),int(row['resolved_target'],16)) for row in ev['table_pointer_contracts']]==[(0x39838,0x39750,0xbd848),(0x39840,0x3976c,0xbd868),(0x399ac,0x398d0,0xbd888),(0x399b4,0x398ec,0xbd8a8)]
    for row in ev['table_pointer_contracts']:
        p=out/row['file'];a=int(row['literal'],16);data=bytes(read(p)['data']);assert sha(p)==row['sha256'] and data==app.read_bytes()[a-0x27000:a-0x27000+4]
        assert struct.unpack('<I',data)[0]==int(row['encoded_offset'],16) and int(row['pc_base'],16)+int(row['encoded_offset'],16)==int(row['resolved_target'],16)
    from audit_source_frontier import section_bytes
    tabledata=bytes(read(out/'ghidra-bd848.json')['data']);assert tabledata==app.read_bytes()[0x96848:0x968c8]
    for section,a,n in [('log10f_coeff',0x39830,8),('log10f_high',0x3983c,4),('log10f_tail',0x39844,32),('logf_coeff',0x399a4,8),('logf_high',0x399b0,4),('logf_tail',0x399b8,24),('float_log_tables',0xbd848,128)]:
        data=section_bytes(out/'native_float_logs.o','.r1.math.'+section,executable=False);assert data==(tabledata if section=='float_log_tables' else bytes(read(out/f'ghidra-{a:x}.json')['data']))==app.read_bytes()[a-0x27000:a-0x27000+n]
        assert r['source_owned_data_spans'][section]==dict(address=hex(a),bytes=n,sha256=hashlib.sha256(data).hexdigest())
    previous=read(BASE/'native-expf-tanhf/consumer-verification.json');assert graph['comparisons']==1952 and graph['consumer_counts']==previous['consumer_counts'] and graph['remaining_consumer_bodies_native']==11 and graph['source_consumer_bodies']==previous['source_consumer_bodies']+['logf','log10f']
    assert graph['helper_observations']=={side:{**values,'logf':56,'log10f':56,**({'errno':80,'divzero32':0,'self32':16,'invalid32':36} if side=='redirected' else {})} for side,values in previous['helper_observations'].items()}
    assert graph['trace_sha256']=='d2225e0fb6bccfc1c743a0e48da37fd5c369b8bbb6f087ba788b40c7983f5eef' and graph['application_sha256']==app_hash and not graph['instruction_identity'] and graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_logs_consumers.py')
    assert graph['runtime_report_sha256']==sha(bp) and graph['runtime_object_sha256']==r['runtime_object_sha256']
    for flag in ('runtime_no_unresolved','internal_helper_counts_are_not_equivalence_claim','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
    assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for receipt in [r,graph]:
        assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==sha(ROOT/receipt['layout'])==ev['verification_layout_sha256'] and receipt['parent_layouts']==ev['parent_layouts']
        for path,digest in receipt['parent_layouts'].items():assert sha(ROOT/path)==digest,path
if __name__=='__main__':audit()
