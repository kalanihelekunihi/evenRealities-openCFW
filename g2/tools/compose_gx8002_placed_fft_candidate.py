# SPDX-License-Identifier: MIT
"""Compose an explicitly unadmitted FFT integration experiment from a verified build."""
import json
from build_gx8002_source_candidate import compose
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from build_gx8002_placed_rfft_cluster import build

def experiment(include_fill=False, tail_layout=False, include_unpack=False, include_compare=False, include_core=False, include_wrappers=False, include_conversion=False, include_reverse_conversion=False, include_addsub=False, include_muldiv=False, include_exp=False, include_twins=False, include_make=False, include_uint=False, include_float=False, include_muldi=False, include_widen=False, include_udiv=False, include_fixunsigned=False, include_sign=False, include_tokenizer=False, include_copy=False, include_memset=False, include_scale=False, include_sqrt=False, include_power=False, include_logexp=False, include_math_wrappers=False, include_fmod=False, include_polynomial=False, include_sine=False, include_cosine=False, include_reducer_scale=False, include_centered=False, include_exception=False, include_uart=False, include_uart_cluster=False, include_clock=False):
    assert not include_clock or include_uart_cluster
    assert not include_uart_cluster or include_uart
    assert not include_uart or include_exception
    assert not include_exception or include_centered
    assert not include_centered or include_reducer_scale
    assert not include_reducer_scale or include_cosine
    assert not include_cosine or include_sine
    assert not include_sine or include_polynomial
    assert not include_polynomial or include_fmod
    assert not include_fmod or include_math_wrappers
    assert not include_math_wrappers or include_logexp
    assert not include_logexp or include_power
    assert not include_power or include_sqrt
    assert not include_sqrt or include_scale
    assert not include_scale or include_memset
    assert not include_memset or include_copy
    assert not include_copy or include_tokenizer
    assert not include_tokenizer or include_sign
    assert not include_sign or include_fixunsigned
    assert not include_fixunsigned or include_udiv
    assert not include_udiv or include_widen
    assert not include_widen or include_muldi
    assert not include_muldi or include_float
    assert not include_float or include_uint
    assert not include_uint or include_make
    assert not include_make or include_twins
    assert not include_twins or include_exp
    assert not include_exp or include_muldiv
    assert not include_muldiv or include_addsub
    assert not include_addsub or include_reverse_conversion
    assert not include_reverse_conversion or include_conversion
    assert not include_conversion or include_wrappers
    assert not include_wrappers or include_core
    assert not include_core or include_compare
    assert not include_compare or include_unpack
    assert not include_unpack or tail_layout
    assert not (include_fill and tail_layout)
    base=ROOT/'build/gx8002-source-candidate'
    report_path=base/'build-report.json';report=json.loads(report_path.read_text())
    baseline=(base/'firmware_codec.hybrid-candidate.bin').read_bytes()
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert sha(baseline)==report['firmware_sha256'] and len(baseline)==report['firmware_size']
    rows=report['ownership'];cursor=0;replacements=[]
    from generate_gx8002_image_a_tail import PAD,XIP
    for row in rows:
        offset,size=row['offset'],row['size'];assert offset==cursor;cursor+=size
        body=baseline[offset:offset+size];kind=row['kind']
        if 'sha256' in row:assert sha(body)==row['sha256']
        if kind=='retained_stock':assert body==stock[offset:offset+size];continue
        if kind=='generated_container_metadata' or PAD<=offset<XIP:continue
        if kind=='generated_unreachable_fill':
            prior=replacements[-1];assert prior['package_offset']+prior['bytes']==offset and body==bytes(size)
            prior['bytes']+=size;prior['payload']+=body
            prior['sha256']=sha(stock[prior['package_offset']:offset+size]);continue
        assert kind in ('compiled_c','compiled_assembly','generated_source_data')
        replacements.append({'package_offset':offset,'bytes':size,'payload':body,'compiled_bytes':size,
                             'compiled_sha256':sha(body),'sha256':sha(stock[offset:offset+size]),
                             'ownership_kind':kind,'symbol':row['symbol']})
    assert cursor==len(baseline)
    reproduced,ownership,totals=compose(stock,replacements)
    assert reproduced==baseline and ownership==rows and totals==report['byte_ownership']
    if tail_layout:
        from build_gx8002_fft_q15_tail_layout import build as build_tail
        evidence=build_tail();elf_path=ROOT/'build/gx8002-fft-q15-tail-layout/component.elf'
        section_rows=[dict(item,section=name) for name,item in evidence['sections'].items()]
    else:
        evidence=build(include_fill=include_fill);elf_path=ROOT/('build/gx8002-placed-rfft-fill-cluster/cluster.elf' if include_fill else 'build/gx8002-placed-rfft-cluster/cluster.elf')
        section_rows=evidence['sections']
    elf=Elf32(elf_path.read_bytes(),'FFT');assert sha(elf_path.read_bytes())==evidence['elf_sha256']
    patches=[]
    for item in section_rows:
        section=next(s for s in elf.sections if s['name']==item['section'])
        body=elf.contents(section);assert sha(body)==item['sha256'] and len(body)==item['size']
        off=item['offset'];size=item['size']
        kind='compiled_c' if section['flags']&4 else 'generated_source_data'
        if tail_layout and section['address']==evidence['symbols']['source_copy_entry']:
            assert size==4 and section['flags']&4
            kind='compiled_assembly'
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':kind,'symbol':'placed_rfft'+item['section']})
    unpack_evidence=None
    if include_unpack:
        from build_gx8002_backup_double_unpack import build as build_unpack
        unpack_evidence=build_unpack()
        path=ROOT/'build/gx8002-backup-double-unpack/unpack.elf'
        assert sha(path.read_bytes())==unpack_evidence['elf_sha256']
        unpack=Elf32(path.read_bytes(),'unpack')
        section=next(s for s in unpack.sections if s['name']=='.text');body=unpack.contents(section)
        off=unpack_evidence['package_offset'];size=len(body)
        assert sha(body)==unpack_evidence['compiled_sha256'] and size==176
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'__unpack_d'})
    compare_evidence=None
    if include_compare:
        from build_gx8002_backup_double_compare import build as build_compare
        compare_evidence=build_compare()
        path=ROOT/'build/gx8002-backup-double-compare/compare.elf'
        assert sha(path.read_bytes())==compare_evidence['elf_sha256']
        unpack=Elf32(path.read_bytes(),'compare')
        section=next(s for s in unpack.sections if s['name']=='.text');body=unpack.contents(section)
        off=compare_evidence['package_offset'];size=len(body)
        assert sha(body)==compare_evidence['compiled_sha256'] and size==186
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'__fpcmp_parts_d'})
    core_evidence=None
    if include_core:
        from build_gx8002_double_core_layout import build as build_core
        core_evidence=build_core();path=ROOT/'build/gx8002-double-core-layout/core.elf'
        assert sha(path.read_bytes())==core_evidence['elf_sha256']
        core=Elf32(path.read_bytes(),'core')
        for item in core_evidence['sections']:
            sec=next(s for s in core.sections if s['name']=='.'+item['name']);body=core.contents(sec)
            assert sha(body)==item['sha256'] and len(body)==item['bytes']
            off=item['offset'];size=len(body)
            if item['name'] in ('unpack','compare'):
                prior=next(p for p in patches if p['symbol']==item['symbol'])
                assert prior['package_offset']==off and prior['payload']==body
                continue
            assert item['name'] in ('pack','left','right')
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':item['symbol']})
    wrapper_evidence=None
    if include_wrappers:
        from build_gx8002_double_comparison_wrappers import build as build_wrappers
        if include_conversion:
            from build_gx8002_double_conversion_cluster import build as build_wrappers
        if include_reverse_conversion:
            from build_gx8002_double_bidirectional_conversion_cluster import build as build_wrappers
        wrapper_evidence=build_wrappers();path=ROOT/('build/gx8002-double-bidirectional-conversion-cluster/wrappers.elf' if include_reverse_conversion else 'build/gx8002-double-conversion-cluster/wrappers.elf' if include_conversion else 'build/gx8002-double-comparison-wrappers/wrappers.elf')
        assert sha(path.read_bytes())==wrapper_evidence['elf_sha256']
        wrappers=Elf32(path.read_bytes(),'wrappers')
        for item in wrapper_evidence['wrappers']:
            sec=next(s for s in wrappers.sections if s['name']=='.'+item['name']);body=wrappers.contents(sec)
            assert sha(body)==item['sha256'] and len(body)==item['compiled_bytes']
            off=item['offset'];size=len(body)
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':item['symbol']})
        for item in core_evidence['sections']:
            sec=next(s for s in wrappers.sections if s['name']=='.'+item['name'])
            assert sha(wrappers.contents(sec))==item['sha256']
    addsub_evidence=None
    if include_addsub:
        from build_gx8002_double_addsub_cluster import build as build_addsub
        addsub_evidence=build_addsub(True)
        path=ROOT/'build/gx8002-double-addsub-placed/addsub.elf'
        assert sha(path.read_bytes())==addsub_evidence['elf_sha256']
        arithmetic=Elf32(path.read_bytes(),'addsub')
        names={'.add0':'__adddf3','.add1':'__subdf3','.add2':'_fpadd_parts','.copy':'memcpy','.nan':'__thenan_df'}
        for item in addsub_evidence['placement']:
            sec=next(s for s in arithmetic.sections if s['name']==item['name'])
            body=arithmetic.contents(sec);off=item['offset'];size=item['bytes']
            assert len(body)==size and sha(body)==item['sha256']
            if item['name'] not in names:
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'generated_source_data' if item['name']=='.nan' else 'compiled_c',
                            'symbol':names[item['name']]})
    muldiv_evidence=None
    if include_muldiv:
        from build_gx8002_double_muldiv_cluster import build as build_muldiv
        muldiv_evidence=build_muldiv(True)
        path=ROOT/'build/gx8002-double-muldiv-corrected/muldiv.elf'
        assert sha(path.read_bytes())==muldiv_evidence['elf_sha256']
        arithmetic=Elf32(path.read_bytes(),'muldiv')
        for sec in arithmetic.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=arithmetic.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name'] not in ('.mul','.div'):
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            item=next(r for r in muldiv_evidence['routines'] if '.'+r['name']==sec['name'])
            assert off==item['offset'] and size==item['bytes'] and size<=item['stock_bytes']
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'__'+item['name']+'df3'})
    exp_evidence=None
    if include_exp:
        from build_gx8002_exp_placed_cluster import build as build_exp
        exp_evidence=build_exp();path=ROOT/'build/gx8002-exp-placed-cluster/exp.elf'
        assert sha(path.read_bytes())==exp_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'exp')
        previous=next(p for p in patches if p['symbol']=='memcpy')
        assert previous['package_offset']==0x4a654 and previous['bytes']==156
        patches.remove(previous)
        names={'.exp':'open_cfw_gx8002_backup_exp','.copy':'memcpy','.tiny':'exp_tiny','.scale':'exp_scale'}
        for item in exp_evidence['sections']:
            sec=next(s for s in linked.sections if s['name']==item['name'])
            body=linked.contents(sec);off=item['offset'];size=item['bytes']
            assert sha(body)==item['sha256'] and len(body)==size
            if item['name'] not in names:
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':names[item['name']]})
    twins_evidence=None
    if include_twins:
        from build_gx8002_comparison_twins_cluster import build as build_twins
        twins_evidence=build_twins();path=ROOT/'build/gx8002-comparison-twins-cluster/twins.elf'
        assert sha(path.read_bytes())==twins_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'twins')
        for item in twins_evidence['sections']:
            sec=next(s for s in linked.sections if s['name']==item['name'])
            body=linked.contents(sec);off=item['offset'];size=item['bytes']
            assert sha(body)==item['sha256'] and len(body)==size
            if not item['name'].startswith('.twin_'):
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert off in (0x4ab20,0x4ab98) and size==8
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_double_compare_'+hex(off)[2:]})
    make_evidence=None
    if include_make:
        from build_gx8002_make_dp_cluster import build as build_make
        make_evidence=build_make();path=ROOT/'build/gx8002-make-dp-cluster/make.elf'
        assert sha(path.read_bytes())==make_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'make')
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name']!='.make':
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert off==make_evidence['package_offset']==0x4aca8 and size==make_evidence['bytes']==38
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'__make_dp'})
    uint_evidence=None
    if include_uint:
        from build_gx8002_uint32_double_cluster import build as build_uint
        uint_evidence=build_uint();path=ROOT/'build/gx8002-uint32-double-cluster/uint.elf'
        assert sha(path.read_bytes())==uint_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'make')
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name']!='.uint':
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert off==uint_evidence['package_offset']==0x4ad0c and size==uint_evidence['bytes']==86
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'__floatunsidf'})
    float_evidence=None
    if include_float:
        from build_gx8002_double_to_float_cluster import build as build_float
        float_evidence=build_float();path=ROOT/'build/gx8002-double-to-float-cluster/convert.elf'
        assert sha(path.read_bytes())==float_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'float')
        expected={'.convert':(0x4acd8,52,'__truncdfsf2'),'.make_float':(0x4ae2c,22,'__make_fp'),'.pack_float':(0x4b17c,186,'__pack_f')}
        seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name'] not in expected:
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            offset,length,symbol=expected[sec['name']];assert (off,size)==(offset,length)
            seen.add(sec['name'])
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':symbol})
        assert seen==set(expected)
    muldi_evidence=None
    if include_muldi:
        from build_gx8002_muldi_source import build as build_muldi
        muldi_evidence=build_muldi();path=ROOT/'build/gx8002-muldi-source-cluster/muldi.elf'
        assert sha(path.read_bytes())==muldi_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'muldi')
        allocated=[s for s in linked.sections if s['flags']&2 and s['size']]
        assert len(allocated)==1 and allocated[0]['name']=='.text'
        sec=allocated[0];body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
        assert off==muldi_evidence['package_offset']==0x4ad64 and size==muldi_evidence['bytes']==74
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'__muldi3'})
    widen_evidence=None
    if include_widen:
        from build_gx8002_float_to_double_cluster import build as build_widen
        from analyze_gx8002_widen_reference_context import analyze_context
        widen_evidence=build_widen();widen_evidence['reference_context']=analyze_context()
        path=ROOT/'build/gx8002-float-to-double-cluster/widen.elf'
        assert sha(path.read_bytes())==widen_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'widen');expected={'.widen':(0x4a434,38,'__extendsfdf2'),'.unpack_float':(0x4adb0,114,'__unpack_f')};seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name'] not in expected:
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            offset,length,symbol=expected[sec['name']];assert (off,size)==(offset,length);seen.add(sec['name'])
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':symbol})
        assert seen==set(expected)
    udiv_evidence=None
    if include_udiv:
        from build_gx8002_backup_unsigned_division import build as build_udiv
        from analyze_gx8002_unsigned_division_references import analyze_context
        udiv_evidence=build_udiv();udiv_evidence['reference_context']=analyze_context()
        path=ROOT/'build/gx8002-backup-unsigned-division/division.elf'
        assert sha(path.read_bytes())==udiv_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'division');expected={'.quotient':(0x49ddc,776,'__udivdi3'),'.remainder':(0x4a110,768,'__umoddi3')};seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name']=='.bit_lengths':
                assert off==0x4df14 and body==bytes(i.bit_length() for i in range(256))
                assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
                patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                                'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                                'ownership_kind':'generated_source_data','symbol':'__clz_tab'})
                continue
            offset,length,symbol=expected[sec['name']];assert (off,size)==(offset,length);seen.add(sec['name'])
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':symbol})
        assert seen==set(expected)
    fixunsigned_evidence=None
    if include_fixunsigned:
        from build_gx8002_fixunsdfsi_cluster import build as build_fixunsigned
        fixunsigned_evidence=build_fixunsigned();path=ROOT/'build/gx8002-fixunsdfsi-cluster/fix.elf'
        assert sha(path.read_bytes())==fixunsigned_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'fixunsigned');seen=False
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            if sec['name']!='.fix_unsigned':
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert off==0x49da4 and size==56;seen=True
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'__fixunsdfsi'})
        assert seen
    sign_evidence=None
    if include_sign:
        from build_gx8002_float_sign import build as build_sign
        from analyze_gx8002_double_wrapper_references import analyze as references
        sign_evidence=build_sign()
        sign_evidence['references']=[references(0x49be4,0x49c04),references(0x49c04,0x49c14)]
        path=ROOT/'build/gx8002-float-sign/sign.elf'
        assert sha(path.read_bytes())==sign_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'sign');expected={'.copy':(0x49be4,22,'open_cfw_gx8002_copy_float_sign'),'.absolute':(0x49c04,12,'open_cfw_gx8002_float_absolute')};seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
            offset,length,symbol=expected[sec['name']];assert (off,size)==(offset,length);seen.add(sec['name'])
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':symbol})
        assert seen==set(expected)
    tokenizer_evidence=None
    if include_tokenizer:
        from verify_gx8002_strtok import verify as verify_tokenizer
        from analyze_gx8002_backup_strtok_context import analyze_context
        tokenizer_evidence=verify_tokenizer(backup=True);tokenizer_evidence['context']=analyze_context()
        path=ROOT/'build/gx8002-backup-strtok/candidate.elf'
        assert sha(path.read_bytes())==tokenizer_evidence['candidate']['elf_sha256']
        linked=Elf32(path.read_bytes(),'tokenizer')
        allocated=[s for s in linked.sections if s['flags']&2 and s['size']]
        assert len(allocated)==1 and allocated[0]['name']=='.text'
        sec=allocated[0];body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
        assert off==0x49c14 and size==104
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_backup_strtok'})
    copy_evidence=None
    if include_copy:
        from verify_gx8002_backup_memcpy import verify as verify_copy
        from analyze_gx8002_double_wrapper_references import analyze as references
        copy_evidence=verify_copy();copy_evidence['references']=references(0x49c84,0x49d04)
        path=ROOT/'build/gx8002-backup-memcpy/copy.elf'
        assert sha(path.read_bytes())==copy_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'copy')
        allocated=[s for s in linked.sections if s['flags']&2 and s['size']]
        assert len(allocated)==1 and allocated[0]['name']=='.text'
        sec=allocated[0];body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
        assert off==0x49c84 and size==96
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_backup_memcpy'})
    memset_evidence=None
    if include_memset:
        from compare_gx8002_backup_memset import verify as verify_memset
        from analyze_gx8002_double_wrapper_references import analyze as references
        memset_evidence=verify_memset();memset_evidence['references']=references(0x49d04,0x49da4)
        path=ROOT/'build/gx8002-backup-memset/memset-candidate.elf'
        linked=Elf32(path.read_bytes(),'memset')
        allocated=[s for s in linked.sections if s['flags']&2 and s['size']]
        assert len(allocated)==1 and allocated[0]['name']=='.text'
        sec=allocated[0];body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
        assert off==0x49d04 and size==102 and sha(body)==memset_evidence['build']['compiled_sha256']
        memset_evidence['elf_sha256']=sha(path.read_bytes())
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_backup_memset'})
    scale_evidence=None
    if include_scale:
        from build_gx8002_scalbnf_probe import build as build_scale
        from analyze_gx8002_double_wrapper_references import analyze as references
        scale_evidence=build_scale(corrected=True,placed=True)
        scale_evidence['references']=references(0x49ad4,0x49bd8)
        path=ROOT/'build/gx8002-scalbnf-placed/scale.elf'
        assert sha(path.read_bytes())==scale_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'scale');seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body);seen.add(sec['name'])
            if sec['name']=='.sign':
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert sec['name']=='.scale' and off==0x49ad4 and size==244
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_scale_float'})
        assert seen=={'.scale','.sign'}
    sqrt_evidence=None
    if include_sqrt:
        from build_gx8002_sqrtf_placed import build as build_sqrt
        from analyze_gx8002_double_wrapper_references import analyze as references
        sqrt_evidence=build_sqrt()
        sqrt_evidence['references']=references(0x4950c,0x495e4)
        for report_name in ('gx8002-sqrtf-placed-positive.json','gx8002-sqrtf-special-paths.json'):
            test=json.loads((ROOT/'docs/research'/report_name).read_text())
            assert test['elf_sha256']==sqrt_evidence['elf_sha256']
        path=ROOT/'build/gx8002-sqrtf-placed/sqrt.elf'
        assert sha(path.read_bytes())==sqrt_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'sqrt')
        sections=[sec for sec in linked.sections if sec['flags']&2 and sec['size']]
        assert len(sections)==1 and sections[0]['name']=='.sqrt'
        sec=sections[0];body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body)
        assert off==0x4950c and size==180 and sha(body)==sqrt_evidence['section_sha256']
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'__ieee754_sqrtf'})
    power_evidence=None
    if include_power:
        from build_gx8002_powf_placed import build as build_power
        from analyze_gx8002_powf_reference_context import analyze_context
        power_evidence=build_power()
        power_evidence['references']=analyze_context()
        assert not power_evidence['references']['unresolved_stored_words']
        assert not power_evidence['references']['unresolved_branches']
        power_evidence['validation']={}
        for label in ('identities','general-wide','nan','infinite-exponent','domain','zero-infinite-base'):
            test=json.loads((ROOT/'docs/research'/('gx8002-powf-'+label+'.json')).read_text())
            assert test['elf_sha256']==power_evidence['elf_sha256']
            if 'differences' in test:assert not test['differences']
            power_evidence['validation'][label]=test
        path=ROOT/'build/gx8002-powf-placed/power.elf'
        assert sha(path.read_bytes())==power_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'power');seen=set()
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body);seen.add(sec['name'])
            if sec['name']!='.power':
                prior=next(p for p in patches if p['package_offset']==off)
                assert prior['payload']==body
                continue
            assert off==0x489fc and size==1652
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'__ieee754_powf'})
        assert seen=={'.power','.sqrt','.scale','.sign','.absolute'}
    logexp_evidence=None
    if include_logexp:
        from build_gx8002_log_exp_placed import build as build_logexp
        from analyze_gx8002_logf_reference_context import analyze_context as log_refs
        from analyze_gx8002_expf_reference_context import analyze_context as exp_refs
        logexp_evidence=build_logexp()
        logexp_evidence['references']=[log_refs(),exp_refs()]
        logexp_evidence['validation']={}
        for label in ('logf-finite','logf-special-paths','expf-finite','expf-special-paths'):
            test=json.loads((ROOT/'docs/research'/('gx8002-'+label+'.json')).read_text())
            assert test['elf_sha256']==logexp_evidence['elf_sha256']
            if 'differences' in test:assert not test['differences'] and not test['accuracy_errors']
            logexp_evidence['validation'][label]=test
        path=ROOT/'build/gx8002-log-exp-placed/math.elf'
        assert sha(path.read_bytes())==logexp_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'logexp');seen=set()
        layout={'.log':(0x490a8,568,'__ieee754_logf'),'.exp':(0x49300,436,'__ieee754_expf'),'.exp_constants':(0x494b4,24,'expf_constants')}
        for sec in linked.sections:
            if not sec['flags']&2 or not sec['size']:continue
            body=linked.contents(sec);off=sec['address']-0x10003000+0x3b940;size=len(body);seen.add(sec['name'])
            expected_off,expected_size,symbol=layout[sec['name']]
            assert off==expected_off and size==expected_size
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'generated_source_data' if sec['name']=='.exp_constants' else 'compiled_c','symbol':symbol})
        assert seen==set(layout)
    math_wrappers_evidence=None
    if include_math_wrappers:
        from build_gx8002_math_wrappers import build as build_math_wrappers
        math_wrappers_evidence=build_math_wrappers()
        path=ROOT/'build/gx8002-math-wrappers/wrappers.elf'
        assert sha(path.read_bytes())==math_wrappers_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'math wrappers')
        sections=[s for s in linked.sections if s['flags']&2 and s['size']]
        assert len(sections)==3
        for item in math_wrappers_evidence['sections']:
            sec=next(s for s in sections if s['name']=='.'+item['name'])
            off=item['offset'];body=linked.contents(sec);size=len(body)
            assert sec['address']==off-0x3b940+0x10003000 and size==8
            assert sha(body)==item['sha256'] and body==stock[off:off+size]
            target=next(p for p in patches if p['package_offset']==item['target'])
            assert target['symbol']=='__ieee754_'+item['name'] and target['ownership_kind']=='compiled_c'
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_'+item['name']})
    fmod_evidence=None
    if include_fmod:
        from build_gx8002_fmod_placed import build as build_fmod
        fmod_evidence=build_fmod()
        path=ROOT/'build/gx8002-fmod-placed/fmod.elf'
        linked=Elf32(path.read_bytes(),'fmod')
        assert sha(path.read_bytes())==fmod_evidence['elf_sha256']
        for report_name in ('gx8002-fmod-finite','gx8002-fmod-special'):
            check=json.loads((ROOT/'docs/research'/(report_name+'.json')).read_text())
            if report_name.endswith('finite'):
                assert check['source_elf_sha256']==fmod_evidence['elf_sha256']
                assert check['finite_cases']==check['stock_comparison_cases']==4966
                assert check['stock_sha256']==IMAGE_SHA
            else:
                assert check['source_elf_hashes']['gx8002-fmod-placed']==fmod_evidence['elf_sha256']
                assert check['cases']==3520
                from analyze_gx8002_double_wrapper_references import analyze as fmod_references
                assert check['references']==fmod_references(0x495e4,0x49828)
                dependency=ROOT/'build/gx8002-double-muldiv-corrected/muldiv.elf'
                assert sha(dependency.read_bytes())==check['source_elf_hashes']['gx8002-double-muldiv-corrected']
                depelf=Elf32(dependency.read_bytes(),'fmod arithmetic')
                for symbol,off in fmod_evidence['arithmetic_targets'].items():
                    target=next(p for p in patches if p['package_offset']==off)
                    assert target['symbol']==symbol and target['ownership_kind']=='compiled_c'
                    section=next(s for s in depelf.sections if s['address']==off-0x3b940+0x10003000 and s['size'])
                    assert target['payload']==depelf.contents(section)
            fmod_evidence[report_name]=check
        sec=next(s for s in linked.sections if s['name']=='.fmod')
        body=linked.contents(sec);off=0x495e4;size=len(body)
        assert size==576 and sec['address']==off-0x3b940+0x10003000
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'__ieee754_fmod'})
    polynomial_evidence=None
    if include_polynomial:
        from build_gx8002_polynomial_placed import build as build_polynomial
        from analyze_gx8002_polynomial_reference_context import analyze_context
        polynomial_evidence=build_polynomial()
        polynomial_evidence['reference_context']=analyze_context()
        path=ROOT/'build/gx8002-polynomial-placed/polynomial.elf'
        assert sha(path.read_bytes())==polynomial_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'polynomial')
        check=json.loads((ROOT/'docs/research/gx8002-polynomial-source.json').read_text())
        assert check['source_elf_hashes']['gx8002-polynomial-placed']==polynomial_evidence['elf_sha256']
        assert check['stock_sha256']==IMAGE_SHA
        assert check['finite_cases']==check['stock_comparison_cases']==680
        assert check['identity_cases']==1063 and check['degree_zero_payload_cases']==1072
        dependency=ROOT/'build/gx8002-exp-placed-cluster/exp.elf'
        assert sha(dependency.read_bytes())==check['source_elf_hashes']['gx8002-exp-placed-cluster']
        depelf=Elf32(dependency.read_bytes(),'polynomial arithmetic')
        for symbol,off in [('__muldf3',0x4a790),('__adddf3',0x4a724)]:
            target=next(p for p in patches if p['package_offset']==off)
            assert target['symbol']==symbol and target['ownership_kind']=='compiled_c'
            section=next(s for s in depelf.sections if s['address']==off-0x3b940+0x10003000 and s['size'])
            assert target['payload']==depelf.contents(section)
        polynomial_evidence['execution']=check
        sec=next(s for s in linked.sections if s['name']=='.polynomial')
        body=linked.contents(sec);off=0x49828;size=len(body)
        assert size==50 and sec['address']==off-0x3b940+0x10003000
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_polynomial'})
    sine_evidence=None
    if include_sine:
        from build_gx8002_sine_placed import build as build_sine
        from analyze_gx8002_sine_reference_context import analyze_context as sine_references
        sine_evidence=build_sine()
        sine_evidence['references']=sine_references()
        assert not sine_evidence['references']['unresolved_bounded_findings']
        path=ROOT/'build/gx8002-sine-placed/sine.elf'
        assert sha(path.read_bytes())==sine_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'sine')
        checks=[]
        for suffix,count in [('',201),('-tail',448)]:
            check=json.loads((ROOT/'docs/research'/('gx8002-sine-placed'+suffix+'-source.json')).read_text())
            assert check['source_elf_sha256']==sine_evidence['elf_sha256'] and check['stock_sha256']==IMAGE_SHA
            assert check['results']['sin']['cases']==count
            assert not check['results']['sin']['source_accuracy_errors_over_one_ulp']
            checks.append(check)
        special=json.loads((ROOT/'docs/research/gx8002-sine-special.json').read_text())
        assert special['source_elf_hashes']['gx8002-sine-placed']==sine_evidence['elf_sha256']
        assert special['cases']==3248 and not special['differences']
        sine_evidence['execution']=checks;sine_evidence['special']=special
        # Authenticate all linked source dependencies against the composed bytes.
        for sec in linked.sections:
            if not (sec['flags']&2 and sec['size']) or sec['name'] in ('.sine','.coefficients'):continue
            off=sec['address']-0x10003000+0x3b940
            prior=next(p for p in patches if p['package_offset']==off)
            assert prior['payload']==linked.contents(sec)
        for name,off,size,kind,symbol in [('.sine',0x49890,264,'compiled_c','__kernel_sin'),('.coefficients',0x4f974,40,'generated_source_data','open_cfw_gx8002_sin_coefficients')]:
            sec=next(s for s in linked.sections if s['name']==name);body=linked.contents(sec)
            assert sec['address']==off-0x3b940+0x10003000 and len(body)==size
            if kind=='generated_source_data':assert body==stock[off:off+size]
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':kind,'symbol':symbol})
    cosine_evidence=None
    if include_cosine:
        from build_gx8002_cosine_placed import build as build_cosine
        from analyze_gx8002_double_wrapper_references import analyze as cosine_references
        cosine_evidence=build_cosine()
        cosine_evidence['references']=cosine_references(0x499ac,0x49ac0)
        assert len(cosine_evidence['references']['external_branches'])==5
        assert not cosine_evidence['references']['external_literal_pools'] and not cosine_evidence['references']['stored_address_words']
        path=ROOT/'build/gx8002-cosine-placed/cosine.elf'
        assert sha(path.read_bytes())==cosine_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'cosine')
        checks=[]
        for suffix,count in [('',201),('-tail',448)]:
            check=json.loads((ROOT/'docs/research'/('gx8002-cosine-placed'+suffix+'-source.json')).read_text())
            assert check['source_elf_sha256']==cosine_evidence['elf_sha256'] and check['stock_sha256']==IMAGE_SHA
            assert check['results']['cos']['cases']==count
            assert not check['results']['cos']['source_accuracy_errors_over_one_ulp']
            checks.append(check)
        special=json.loads((ROOT/'docs/research/gx8002-cosine-special.json').read_text())
        assert special['source_elf_hashes']['gx8002-cosine-placed']==cosine_evidence['elf_sha256']
        assert special['cases']==1624 and not special['differences']
        cosine_evidence['execution']=checks;cosine_evidence['special']=special
        # Authenticate all linked source dependencies against the composed bytes.
        for sec in linked.sections:
            if not (sec['flags']&2 and sec['size']) or sec['name'] in ('.cosine','.coefficients'):continue
            off=sec['address']-0x10003000+0x3b940
            prior=next(p for p in patches if p['package_offset']==off)
            assert prior['payload']==linked.contents(sec)
        for name,off,size,kind,symbol in [('.cosine',0x499ac,252,'compiled_c','__kernel_cos'),('.coefficients',0x4f99c,48,'generated_source_data','open_cfw_gx8002_cos_coefficients')]:
            sec=next(s for s in linked.sections if s['name']==name);body=linked.contents(sec)
            assert sec['address']==off-0x3b940+0x10003000 and len(body)==size
            if kind=='generated_source_data':assert body==stock[off:off+size]
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':kind,'symbol':symbol})
    reducer_scale_evidence=None
    if include_reducer_scale:
        from generate_gx8002_reducer_scale import build as build_reducer_scale
        reducer_scale_evidence=build_reducer_scale()
        path=ROOT/'build/gx8002-reducer-scale/scale.elf'
        assert sha(path.read_bytes())==reducer_scale_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'generated reducer scale')
        sec=next(s for s in linked.sections if s['name']=='.reducer_scale')
        body=linked.contents(sec);off=0x4de48;size=144
        assert sec['address']==0x10015508 and len(body)==size
        assert body==stock[off:off+size]
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
        assert not any(max(off,p['package_offset'])<min(off+size,p['package_offset']+p['bytes']) for p in patches)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'generated_source_data','symbol':'open_cfw_gx8002_reducer_scale'})
    centered_evidence=None
    if include_centered:
        from build_gx8002_centered_remainder import build as build_centered
        from analyze_gx8002_double_wrapper_references import analyze as centered_refs
        centered_evidence=build_centered()
        centered_evidence['references']=centered_refs(0x4859c,0x4863c)
        refs=centered_evidence['references']
        assert len(refs['external_branches'])==3
        assert not refs['external_literal_pools'] and not refs['stored_address_words']
        checks=json.loads((ROOT/'docs/research/gx8002-centered-remainder-execution.json').read_text())
        assert checks['source_elf_sha256']==centered_evidence['elf_sha256'] and checks['stock_sha256']==IMAGE_SHA
        assert checks['finite_cases']==checks['stock_helper_comparison_cases']==435
        assert checks['special_comparison_cases']==144
        centered_evidence['execution']=checks
        path=ROOT/'build/gx8002-centered-remainder/centered.elf'
        assert sha(path.read_bytes())==centered_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'centered remainder')
        for sec in linked.sections:
            if not (sec['flags']&2 and sec['size']) or sec['name']=='.centered':continue
            off=sec['address']-0x10003000+0x3b940
            prior=next(p for p in patches if p['package_offset']==off)
            assert prior['payload']==linked.contents(sec)
        sec=next(s for s in linked.sections if s['name']=='.centered')
        body=linked.contents(sec);off=0x4859c;size=140
        assert sec['address']==0x1000fc5c and len(body)==size
        assert any(r['kind']=='retained_stock' and r['offset']<=off and off+160<=r['offset']+r['size'] for r in rows)
        patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                        'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                        'ownership_kind':'compiled_c','symbol':'open_cfw_gx8002_centered_remainder'})
    exception_evidence=None
    if include_exception:
        from build_gx8002_backup_upstream_trap import build as build_trap
        from build_gx8002_backup_irq_restore import build as build_irq_restore
        exception_evidence={'trap':build_trap(),'irq_restore':build_irq_restore()}
        for key,directory,filename,checkfile,casekey,count,specs in [
            ('trap','gx8002-backup-upstream-trap','trap.elf','gx8002-backup-upstream-trap-execution.json','cases',256,
             [('.trap_c',0x3bb30,10,'compiled_c','trap_c'),('.vectors',0x3bb3c,80,'compiled_assembly','trap')]),
            ('irq_restore','gx8002-backup-irq-restore','restore.elf','gx8002-backup-irq-restore-execution.json','ordered_access_cases',164,
             [('.text',0x3d16c,24,'compiled_c','open_cfw_gx8002_backup_irq_restore')])]:
            evidence=exception_evidence[key]
            checks=json.loads((ROOT/'docs/research'/checkfile).read_text())
            assert checks['elf_sha256']==evidence['elf_sha256'] and checks[casekey]==count
            evidence['execution']=checks
            path=ROOT/'build'/directory/filename
            assert sha(path.read_bytes())==evidence['elf_sha256']
            linked=Elf32(path.read_bytes(),key)
            assert all(s['type']==8 or s['name'] in {x[0] for x in specs} for s in linked.sections if s['flags']&2 and s['size'])
            for section,off,size,kind,symbol in specs:
                sec=next(s for s in linked.sections if s['name']==section);body=linked.contents(sec)
                assert sec['address']==off-0x3b940+0x10003000 and len(body)==size
                # Exact full-body identity also preserves the default-handler
                # vector entries and any interior references without rebinding.
                assert body==stock[off:off+size]
                assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
                patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                                'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                                'ownership_kind':kind,'symbol':symbol})
    uart_evidence=None
    if include_uart:
        from build_gx8002_backup_uart_putc import build as build_uart_putc
        from build_gx8002_backup_uart_descriptors import build as build_uart_descriptors
        from analyze_gx8002_double_wrapper_references import analyze as uart_refs
        probe=build_uart_putc();uart_evidence=build_uart_descriptors()
        refs=uart_refs(0x3cee0,0x3cf18)
        assert len(refs['external_branches'])==1 and not refs['external_literal_pools'] and not refs['stored_address_words']
        checks=json.loads((ROOT/'docs/research/gx8002-backup-uart-putc-execution.json').read_text())
        assert checks['elf_sha256']==uart_evidence['putc_elf_sha256'] and checks['stock_sha256']==IMAGE_SHA and checks['cases']==4620
        uart_evidence['execution']=checks;uart_evidence['references']=refs;uart_evidence['probe']=probe
        path=ROOT/'build/gx8002-backup-uart-descriptors/uart.elf'
        assert sha(path.read_bytes())==uart_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'source UART')
        for name,off,size,address,kind,symbol in [
            ('.putc',0x3cee0,52,0x100045a0,'compiled_c','open_cfw_gx8002_uart_putc'),
            ('.descriptors',0x4f4c4,256,0x20016b84,'generated_source_data','open_cfw_gx8002_uart_descriptors')]:
            sec=next(s for s in linked.sections if s['name']==name);body=linked.contents(sec)
            assert sec['address']==address and len(body)==size
            if kind=='generated_source_data':assert body==stock[off:off+size]
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':kind,'symbol':symbol})
    uart_cluster_evidence=None
    if include_uart_cluster:
        from verify_gx8002_backup_uart_cluster import verify as verify_uart_cluster
        uart_cluster_evidence=verify_uart_cluster()
        assert uart_cluster_evidence['total_cases']==4620
        path=ROOT/'build/gx8002-backup-uart-interrupt/interrupt.elf'
        assert sha(path.read_bytes())==uart_cluster_evidence['elf_sha256']
        linked=Elf32(path.read_bytes(),'complete UART cluster')
        for name,off,size,symbol in [('.text',0x3cb90,230,'open_cfw_gx8002_uart_interrupt'),
                                     ('.fifo',0x3cc7c,30,'open_cfw_gx8002_uart_fifo_depth'),
                                     ('.tx',0x3cc9c,22,'uart_write_bytes')]:
            sec=next(s for s in linked.sections if s['name']==name);body=linked.contents(sec)
            assert sec['address']==off-0x3b940+0x10003000 and len(body)==size
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':'compiled_c','symbol':symbol})
    clock_evidence=None
    if include_clock:
        from verify_gx8002_backup_clock_initialize import verify as verify_clock
        from analyze_gx8002_backup_clock_references import verify as clock_references
        clock_evidence=verify_clock()
        clock_evidence['references']=clock_references()
        assert clock_evidence['cases']==432 and clock_evidence['references']['bounded_candidates_resolved']
        path=ROOT/'build/gx8002-backup-clock-initialize/clock.elf'
        assert sha(path.read_bytes())==clock_evidence['build']['elf_sha256']
        linked=Elf32(path.read_bytes(),'complete source clock initializer')
        expected={'.text':(0x3bbd4,568,'compiled_c',0x10003294),
                  '.pll':(0x4f200,56,'generated_source_data',0x200168c0),
                  '.stage2_trim_done':(0x4f238,4,'generated_source_data',0x200168f8),
                  '.clk_src_xtal_table':(0x4f23c,80,'generated_source_data',0x200168fc),
                  '.clk_src_osc_table':(0x4f28c,80,'generated_source_data',0x2001694c)}
        assert {s['name'] for s in linked.sections if s['flags']&2 and s['size']}==set(expected)
        for name,(off,size,kind,address) in expected.items():
            sec=next(s for s in linked.sections if s['name']==name);body=linked.contents(sec)
            assert sec['address']==address and len(body)==size
            if kind=='generated_source_data':assert body==stock[off:off+size]
            assert any(r['kind']=='retained_stock' and r['offset']<=off and off+size<=r['offset']+r['size'] for r in rows)
            patches.append({'package_offset':off,'bytes':size,'payload':body,'compiled_bytes':size,
                            'compiled_sha256':sha(body),'sha256':sha(stock[off:off+size]),
                            'ownership_kind':kind,'symbol':'backup_clock'+name})
    removed=[];kept=[]
    for old in replacements:
        overlaps=[p for p in patches if max(old['package_offset'],p['package_offset'])<min(old['package_offset']+old['bytes'],p['package_offset']+p['bytes'])]
        if not overlaps:kept.append(old);continue
        assert old['symbol'] in ('open_cfw_gx8002_backup_rfft','open_cfw_gx8002_backup_cfft')
        if tail_layout:
            # These two dispatchers are wholly superseded. Unoccupied bytes revert
            # to stock under compose(), and remain explicitly retained_stock.
            assert old['package_offset'] in (0x478a4,0x47b14)
            removed.append(old['symbol']);continue
        covered=old['package_offset'];end=covered+old['bytes']
        for p in sorted(overlaps,key=lambda r:r['package_offset']):
            assert p['package_offset']<=covered
            covered=max(covered,p['package_offset']+p['bytes'])
        assert covered>=end
        removed.append(old['symbol'])
    assert sorted(removed)==['open_cfw_gx8002_backup_cfft','open_cfw_gx8002_backup_rfft']
    firmware,ownership,totals=compose(stock,kept+patches)
    if include_clock:assert firmware[0x3be0c:0x3be14]==stock[0x3be0c:0x3be14]
    if include_uart:assert firmware[0x3cf14:0x3cf18]==stock[0x3cf14:0x3cf18]
    if include_centered:assert firmware[0x48628:0x4863c]==stock[0x48628:0x4863c]
    out=ROOT/('build/gx8002-fft-q15-clock-integration-experiment' if include_clock else 'build/gx8002-fft-q15-uart-cluster-integration-experiment' if include_uart_cluster else 'build/gx8002-fft-q15-uart-integration-experiment' if include_uart else 'build/gx8002-fft-q15-exception-integration-experiment' if include_exception else 'build/gx8002-fft-q15-centered-integration-experiment' if include_centered else 'build/gx8002-fft-q15-reducer-scale-integration-experiment' if include_reducer_scale else 'build/gx8002-fft-q15-cosine-integration-experiment' if include_cosine else 'build/gx8002-fft-q15-sine-integration-experiment' if include_sine else 'build/gx8002-fft-q15-polynomial-integration-experiment' if include_polynomial else 'build/gx8002-fft-q15-fmod-integration-experiment' if include_fmod else 'build/gx8002-fft-q15-math-wrappers-integration-experiment' if include_math_wrappers else 'build/gx8002-fft-q15-logexp-integration-experiment' if include_logexp else 'build/gx8002-fft-q15-power-integration-experiment' if include_power else 'build/gx8002-fft-q15-sqrt-integration-experiment' if include_sqrt else 'build/gx8002-fft-q15-scale-integration-experiment' if include_scale else 'build/gx8002-fft-q15-memset-integration-experiment' if include_memset else 'build/gx8002-fft-q15-copy-integration-experiment' if include_copy else 'build/gx8002-fft-q15-tokenizer-integration-experiment' if include_tokenizer else 'build/gx8002-fft-q15-sign-integration-experiment' if include_sign else 'build/gx8002-fft-q15-fixunsigned-integration-experiment' if include_fixunsigned else 'build/gx8002-fft-q15-udiv-integration-experiment' if include_udiv else 'build/gx8002-fft-q15-widen-integration-experiment' if include_widen else 'build/gx8002-fft-q15-muldi-integration-experiment' if include_muldi else 'build/gx8002-fft-q15-float-integration-experiment' if include_float else 'build/gx8002-fft-q15-uint-integration-experiment' if include_uint else 'build/gx8002-fft-q15-make-integration-experiment' if include_make else 'build/gx8002-fft-q15-twins-integration-experiment' if include_twins else 'build/gx8002-fft-q15-exp-integration-experiment' if include_exp else 'build/gx8002-fft-q15-muldiv-integration-experiment' if include_muldiv else 'build/gx8002-fft-q15-addsub-integration-experiment' if include_addsub else 'build/gx8002-fft-q15-bidirectional-integration-experiment' if include_reverse_conversion else 'build/gx8002-fft-q15-conversion-integration-experiment' if include_conversion else 'build/gx8002-fft-q15-wrappers-integration-experiment' if include_wrappers else 'build/gx8002-fft-q15-core-integration-experiment' if include_core else 'build/gx8002-fft-q15-compare-integration-experiment' if include_compare else 'build/gx8002-fft-q15-unpack-integration-experiment' if include_unpack else 'build/gx8002-fft-q15-tail-integration-experiment' if tail_layout else 'build/gx8002-placed-fft-fill-integration-experiment' if include_fill else 'build/gx8002-placed-fft-integration-experiment');out.mkdir(exist_ok=True)
    (out/'firmware_codec.unadmitted.bin').write_bytes(firmware)
    if include_unpack and not include_core:assert firmware[0x4b084:0x4b0b8]==stock[0x4b084:0x4b0b8]
    if include_compare:assert firmware[0x4b172:0x4b17a]==stock[0x4b172:0x4b17a]
    if include_core:assert firmware[0x4b0aa:0x4b0b8]==stock[0x4b0aa:0x4b0b8]
    if include_wrappers:
        for off in (0x4ab1e,0x4ab96):assert firmware[off:off+2]==stock[off:off+2]
    if include_reverse_conversion:assert firmware[0x4ac96:0x4aca8]==stock[0x4ac96:0x4aca8]
    if include_addsub:
        for a,b in ((0x4a704,0x4a724),(0x4a752,0x4a754),(0x4a78a,0x4a790)):
            assert firmware[a:b]==stock[a:b]
    if include_muldiv:
        for item in muldiv_evidence['routines']:
            a=item['offset']+item['bytes'];b=item['offset']+item['stock_bytes']
            assert firmware[a:b]==stock[a:b]
    if include_exp:
        for a,b in ((0x48448,0x48454),(0x4a6e0,0x4a6f0)):
            assert firmware[a:b]==stock[a:b]
    if include_twins:
        for a,b in ((0x4ab28,0x4ab60),(0x4aba0,0x4abd0)):
            assert firmware[a:b]==stock[a:b]
    if include_make:assert firmware[0x4acce:0x4acd8]==stock[0x4acce:0x4acd8]
    if include_uint:assert firmware[0x4ad62:0x4ad64]==stock[0x4ad62:0x4ad64]
    if include_float:
        assert firmware[0x4ae42:0x4ae44]==stock[0x4ae42:0x4ae44]
        assert firmware[0x4b236:0x4b23c]==stock[0x4b236:0x4b23c]
    if include_muldi:assert firmware[0x4adae:0x4adb0]==stock[0x4adae:0x4adb0]
    if include_widen:
        assert firmware[0x4a45a:0x4a460]==stock[0x4a45a:0x4a460]
        assert firmware[0x4ae22:0x4ae2c]==stock[0x4ae22:0x4ae2c]
    if include_udiv:
        assert firmware[0x4a0e4:0x4a110]==stock[0x4a0e4:0x4a110]
        assert firmware[0x4a410:0x4a434]==stock[0x4a410:0x4a434]
    if include_sign:
        assert firmware[0x49bfa:0x49c04]==stock[0x49bfa:0x49c04]
        assert firmware[0x49c10:0x49c14]==stock[0x49c10:0x49c14]
    if include_tokenizer:assert firmware[0x49c7c:0x49c84]==stock[0x49c7c:0x49c84]
    if include_copy:assert firmware[0x49ce4:0x49d04]==stock[0x49ce4:0x49d04]
    if include_memset:assert firmware[0x49d6a:0x49da4]==stock[0x49d6a:0x49da4]
    if include_logexp:
        assert firmware[0x492e0:0x49300]==stock[0x492e0:0x49300]
        assert firmware[0x494cc:0x4950c]==stock[0x494cc:0x4950c]
    if include_power:assert firmware[0x49070:0x490a8]==stock[0x49070:0x490a8]
    if include_sqrt:assert firmware[0x495c0:0x495e4]==stock[0x495c0:0x495e4]
    if include_scale:assert firmware[0x49bc8:0x49bd8]==stock[0x49bc8:0x49bd8]
    result={'include_clock':include_clock,'clock_evidence':clock_evidence,'include_uart_cluster':include_uart_cluster,'uart_cluster_evidence':uart_cluster_evidence,'include_uart':include_uart,'uart_evidence':uart_evidence,'include_exception':include_exception,'exception_evidence':exception_evidence,'include_centered':include_centered,'centered_evidence':centered_evidence,'include_reducer_scale':include_reducer_scale,'reducer_scale_evidence':reducer_scale_evidence,'cosine_evidence':cosine_evidence,'include_cosine':include_cosine,'sine_evidence':sine_evidence,'include_sine':include_sine,'polynomial_evidence':polynomial_evidence,'include_polynomial':include_polynomial,'fmod_evidence':fmod_evidence,'include_fmod':include_fmod,'math_wrappers_evidence':math_wrappers_evidence,'include_math_wrappers':include_math_wrappers,'logexp_evidence':logexp_evidence,'include_logexp':include_logexp,'power_evidence':power_evidence,'include_power':include_power,'sqrt_evidence':sqrt_evidence,'include_sqrt':include_sqrt,'include_scale':include_scale,'scale_evidence':scale_evidence,'include_memset':include_memset,'memset_evidence':memset_evidence,'include_copy':include_copy,'copy_evidence':copy_evidence,'include_tokenizer':include_tokenizer,'tokenizer_evidence':tokenizer_evidence,'sign_evidence':sign_evidence,'include_sign':include_sign,'include_fixunsigned':include_fixunsigned,'fixunsigned_evidence':fixunsigned_evidence,'udiv_evidence':udiv_evidence,'include_udiv':include_udiv,'include_widen':include_widen,'widen_evidence':widen_evidence,'muldi_evidence':muldi_evidence,'include_muldi':include_muldi,'include_float':include_float,'float_evidence':float_evidence,'include_uint':include_uint,'uint_evidence':uint_evidence,'include_make':include_make,'make_evidence':make_evidence,'include_twins':include_twins,'twins_evidence':twins_evidence,'include_exp':include_exp,'exp_evidence':exp_evidence,'include_muldiv':include_muldiv,'muldiv_evidence':muldiv_evidence,'addsub_evidence':addsub_evidence,'include_addsub':include_addsub,'include_reverse_conversion':include_reverse_conversion,'include_conversion':include_conversion,'include_wrappers':include_wrappers,'wrapper_evidence':wrapper_evidence,'include_core':include_core,'core_evidence':core_evidence,'include_compare':include_compare,'compare_evidence':compare_evidence,'include_unpack':include_unpack,'unpack_evidence':unpack_evidence,'tail_layout':tail_layout,'include_fill':include_fill,'baseline_report_sha256':sha(report_path.read_bytes()),'baseline_firmware_sha256':sha(baseline),
            'baseline_reproduced_exactly':True,'placed_fft':evidence,'firmware_sha256':sha(firmware),
            'firmware_size':len(firmware),'source_only':False,'source_admitted':False,'hardware_qualified':False,
            'superseded_symbols':removed,'byte_ownership':totals,'ownership':ownership,
            'limits':['Separate unadmitted composition experiment, not the reviewed firmware build. Existing source bytes reused from authenticated completed macOS build, not rebuilt here.',
                      'FWPK/UART/image-A checksums and container structure validated by production composer. Execution permissions, external reference closure and hardware qualification remain pending.']}
    (out/'build-report.json').write_text(json.dumps(result,indent=2)+'\n')
    summary={k:v for k,v in result.items() if k not in ('ownership','placed_fft')}
    (ROOT/('docs/research/gx8002-fft-q15-clock-integration-experiment.json' if include_clock else 'docs/research/gx8002-fft-q15-uart-cluster-integration-experiment.json' if include_uart_cluster else 'docs/research/gx8002-fft-q15-uart-integration-experiment.json' if include_uart else 'docs/research/gx8002-fft-q15-exception-integration-experiment.json' if include_exception else 'docs/research/gx8002-fft-q15-centered-integration-experiment.json' if include_centered else 'docs/research/gx8002-fft-q15-reducer-scale-integration-experiment.json' if include_reducer_scale else 'docs/research/gx8002-fft-q15-cosine-integration-experiment.json' if include_cosine else 'docs/research/gx8002-fft-q15-sine-integration-experiment.json' if include_sine else 'docs/research/gx8002-fft-q15-polynomial-integration-experiment.json' if include_polynomial else 'docs/research/gx8002-fft-q15-fmod-integration-experiment.json' if include_fmod else 'docs/research/gx8002-fft-q15-math-wrappers-integration-experiment.json' if include_math_wrappers else 'docs/research/gx8002-fft-q15-logexp-integration-experiment.json' if include_logexp else 'docs/research/gx8002-fft-q15-power-integration-experiment.json' if include_power else 'docs/research/gx8002-fft-q15-sqrt-integration-experiment.json' if include_sqrt else 'docs/research/gx8002-fft-q15-scale-integration-experiment.json' if include_scale else 'docs/research/gx8002-fft-q15-memset-integration-experiment.json' if include_memset else 'docs/research/gx8002-fft-q15-copy-integration-experiment.json' if include_copy else 'docs/research/gx8002-fft-q15-tokenizer-integration-experiment.json' if include_tokenizer else 'docs/research/gx8002-fft-q15-sign-integration-experiment.json' if include_sign else 'docs/research/gx8002-fft-q15-fixunsigned-integration-experiment.json' if include_fixunsigned else 'docs/research/gx8002-fft-q15-udiv-integration-experiment.json' if include_udiv else 'docs/research/gx8002-fft-q15-widen-integration-experiment.json' if include_widen else 'docs/research/gx8002-fft-q15-muldi-integration-experiment.json' if include_muldi else 'docs/research/gx8002-fft-q15-float-integration-experiment.json' if include_float else 'docs/research/gx8002-fft-q15-uint-integration-experiment.json' if include_uint else 'docs/research/gx8002-fft-q15-make-integration-experiment.json' if include_make else 'docs/research/gx8002-fft-q15-twins-integration-experiment.json' if include_twins else 'docs/research/gx8002-fft-q15-exp-integration-experiment.json' if include_exp else 'docs/research/gx8002-fft-q15-muldiv-integration-experiment.json' if include_muldiv else 'docs/research/gx8002-fft-q15-addsub-integration-experiment.json' if include_addsub else 'docs/research/gx8002-fft-q15-bidirectional-integration-experiment.json' if include_reverse_conversion else 'docs/research/gx8002-fft-q15-conversion-integration-experiment.json' if include_conversion else 'docs/research/gx8002-fft-q15-wrappers-integration-experiment.json' if include_wrappers else 'docs/research/gx8002-fft-q15-core-integration-experiment.json' if include_core else 'docs/research/gx8002-fft-q15-compare-integration-experiment.json' if include_compare else 'docs/research/gx8002-fft-q15-unpack-integration-experiment.json' if include_unpack else 'docs/research/gx8002-fft-q15-tail-integration-experiment.json' if tail_layout else 'docs/research/gx8002-placed-fft-fill-integration-experiment.json' if include_fill else 'docs/research/gx8002-placed-fft-integration-experiment.json')).write_text(json.dumps(summary,indent=2)+'\n')
    return summary
if __name__=='__main__':print(json.dumps(experiment(),indent=2))
