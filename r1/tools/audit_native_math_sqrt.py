#!/usr/bin/env python3
"""Strict source, ownership, native span and comparison audit for square roots."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=list(csv.DictReader(ownership.open()));previous=read(BASE/'native-float-rounding/consumer-verification.json')
    specs=[('native-float-sqrt','native_float_sqrt','native-float-sqrt-runtime',[(0x2820a,162)]),('native-math-sqrt','native_math_sqrt','native-math-sqrt-runtime',[(0x3af94,122),(0x3b00e,58),(0x3bc9c,6)])]
    for directory,stem,bundle_dir,entries in specs:
        out=BASE/directory;report=read(out/'report.json');receipt=read(out/'verification.json');evidence=read(out/'evidence.json');bundle_path=BASE/bundle_dir/'report.json';bundle=read(bundle_path)
        assert receipt['report_sha256']==sha(out/'report.json') and receipt['object_sha256']==sha(out/(stem+'.o')) and receipt['driver_sha256']==sha(ROOT/('r1/tools/verify_'+stem+'.py')) and receipt['application_sha256']==app_hash and not receipt['instruction_identity']
        assert receipt['runtime_report_sha256']==sha(bundle_path) and receipt['runtime_object_sha256']==sha(bundle_path.parent/(bundle_dir+'.o')) and receipt['runtime_no_unresolved']
        assert not bundle['undefined_symbols'] and bundle['linked_sha256']==receipt['runtime_object_sha256']
        expected=['native-float-sqrt/report.json','native-float-rounding-runtime/report.json'] if directory=='native-float-sqrt' else ['native-math-sqrt/report.json','native-float-sqrt-runtime/report.json']
        assert bundle['provider_reports']=={path:sha(BASE/path) for path in expected}
        for r in [report,bundle]:
            for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
        for path,digest in bundle['objects'].items():assert sha(BASE/path)==digest,path
        assert evidence['ownership_sha256']==sha(ownership) and not evidence['locked_ownership_changed'] and evidence['body_count']==len(entries) and evidence['native_body_bytes']==sum(n for a,n in entries)
        assert evidence['ownership_rows']==[r for r in rows if r['image']=='application' and int(r['entry'],16) in [a for a,n in entries]]
        assert evidence['pseudocode_sha256']==sha(ROOT/evidence['pseudocode_source'])
        for path,digest in evidence['pseudocode_slices'].items():assert sha(out/path)==digest,path
        for path,digest in receipt['evidence'].items():assert sha(out/path)==digest,path
        for a,n in entries:
            assert bytes(read(out/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
            raw=read(out/f'rea-{a:x}.json');q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
            assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==n
        graph=read(out/'consumer-verification.json');assert graph['comparisons']==1552 and graph['consumer_counts']==previous['consumer_counts'] and graph['internal_helper_counts_are_not_equivalence_claim'] and not graph['instruction_identity']
        assert graph['driver_sha256']==sha(ROOT/('r1/tools/verify_'+stem+'_consumers.py')) and graph['application_sha256']==app_hash and graph['runtime_report_sha256']==sha(bundle_path) and graph['runtime_object_sha256']==receipt['runtime_object_sha256'] and graph['runtime_no_unresolved']
        assert graph['report_sha256']==sha(BASE/'native-float-bits/report.json') and graph['object_sha256']==sha(BASE/'native-float-bits/native_float_bits.o') and graph['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and graph['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
        for flag in ('all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture'):assert graph[flag]
        if directory=='native-float-sqrt':
            assert receipt['comparisons']==73728 and receipt['counts']=={'sqrt64':73728} and receipt['positive_cases']==38928 and receipt['nonpositive_return_zero_cases']==34800 and receipt['perfect_integer_square_samples']==4096
            for flag in ('all_binary64_exponents','both_signs','seeded_random_patterns','return_values_stack_callee_saved_and_fpscr_checked','source_round_and_shifts'):assert receipt[flag]
            assert receipt['trace_sha256']=='f18df3347df6e67e20b8739c39106b913e08599f0fa326f856338618ae7f3fce' and graph['trace_sha256']=='aa07bdaba6ba540e3c14e71f314c23ce9260e20a82bea7317fa35ed6e22c3af7' and graph['consumer_bodies_remain_native']
            assert graph['helper_observations']=={side:{**values,'sqrt64':72} for side,values in previous['helper_observations'].items()}
        else:
            assert receipt['comparisons']==237568 and receipt['counts']=={'sqrt':69632,'sqrtf':98304,'errno':69632} and receipt['errno_writes_per_side']=={'sqrt':0,'sqrtf':48504,'errno':69632}
            for flag in ('all_binary32_and_binary64_exponents','both_signs','all_four_rounding_modes','sqrtf_flush_to_zero_and_default_nan_modes','sqrtf_preexisting_inexact_flag','all_low16_errno_words','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_root_errno_and_memory'):assert receipt[flag]
            assert receipt['trace_sha256']=='2d03770a6d2140cc3e62b45e3ca157034e21de84f6493ea0e331c54513432f36' and graph['trace_sha256']=='a118f2029dd7615e0799790fd0dae580972dcce3a5876e313354a9e5ccd2b436'
            assert graph['remaining_consumer_bodies_native']==21 and graph['source_consumer_bodies']==['sqrt','sqrtf']
            assert graph['helper_observations']=={'native':{**previous['helper_observations']['native'],'sqrt64':72,'public_sqrt':56,'public_sqrtf':56,'errno':124},'redirected':{**previous['helper_observations']['redirected'],'sqrt64':16,'public_sqrt':56,'public_sqrtf':56,'errno':116},'compiled_entries':{**previous['helper_observations']['compiled_entries'],'sqrt64':72,'public_sqrt':56,'public_sqrtf':56,'errno':116}}
            cell=evidence['source_owned_errno'];assert cell['address']=='0x20007dbc' and cell['bytes']==4 and not cell['cold_initialization_proven'] and not cell['final_image_placement_proven'] and receipt['errno_storage_address']==cell['address']
            assert bytes(read(out/'ghidra-3bca4.json')['data'])==bytes.fromhex('bc7d0020')==app.read_bytes()[0x14ca4:0x14ca8]
            for r in [receipt,graph]:assert r['layout']==cell['verification_layout'] and r['layout_sha256']==sha(ROOT/r['layout'])==cell['verification_layout_sha256']
if __name__=='__main__':audit()
