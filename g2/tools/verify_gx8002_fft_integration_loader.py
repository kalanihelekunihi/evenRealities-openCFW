# SPDX-License-Identifier: MIT
"""Check complete integration experiment bytes through the stock backup loader."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_backup_memset_loader import execute
from verify_gx8002_memcpy_source import decode

def verify(include_fill=False, tail_layout=False, include_unpack=False, include_compare=False, include_core=False, include_wrappers=False, include_conversion=False, include_reverse_conversion=False, include_addsub=False, include_muldiv=False, include_exp=False, include_twins=False, include_make=False, include_uint=False, include_float=False, include_muldi=False, include_widen=False, include_udiv=False, include_fixunsigned=False, include_sign=False, include_tokenizer=False, include_copy=False, include_memset=False, include_scale=False, include_sqrt=False, include_power=False, include_logexp=False, include_math_wrappers=False, include_fmod=False, include_polynomial=False, include_sine=False, include_cosine=False, include_reducer_scale=False, include_centered=False, include_exception=False, include_uart=False, include_uart_cluster=False, include_clock=False):
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
    out=ROOT/('build/gx8002-fft-q15-clock-integration-experiment' if include_clock else 'build/gx8002-fft-q15-uart-cluster-integration-experiment' if include_uart_cluster else 'build/gx8002-fft-q15-uart-integration-experiment' if include_uart else 'build/gx8002-fft-q15-exception-integration-experiment' if include_exception else 'build/gx8002-fft-q15-centered-integration-experiment' if include_centered else 'build/gx8002-fft-q15-reducer-scale-integration-experiment' if include_reducer_scale else 'build/gx8002-fft-q15-cosine-integration-experiment' if include_cosine else 'build/gx8002-fft-q15-sine-integration-experiment' if include_sine else 'build/gx8002-fft-q15-polynomial-integration-experiment' if include_polynomial else 'build/gx8002-fft-q15-fmod-integration-experiment' if include_fmod else 'build/gx8002-fft-q15-math-wrappers-integration-experiment' if include_math_wrappers else 'build/gx8002-fft-q15-logexp-integration-experiment' if include_logexp else 'build/gx8002-fft-q15-power-integration-experiment' if include_power else 'build/gx8002-fft-q15-sqrt-integration-experiment' if include_sqrt else 'build/gx8002-fft-q15-scale-integration-experiment' if include_scale else 'build/gx8002-fft-q15-memset-integration-experiment' if include_memset else 'build/gx8002-fft-q15-copy-integration-experiment' if include_copy else 'build/gx8002-fft-q15-tokenizer-integration-experiment' if include_tokenizer else 'build/gx8002-fft-q15-sign-integration-experiment' if include_sign else 'build/gx8002-fft-q15-fixunsigned-integration-experiment' if include_fixunsigned else 'build/gx8002-fft-q15-udiv-integration-experiment' if include_udiv else 'build/gx8002-fft-q15-widen-integration-experiment' if include_widen else 'build/gx8002-fft-q15-muldi-integration-experiment' if include_muldi else 'build/gx8002-fft-q15-float-integration-experiment' if include_float else 'build/gx8002-fft-q15-uint-integration-experiment' if include_uint else 'build/gx8002-fft-q15-make-integration-experiment' if include_make else 'build/gx8002-fft-q15-twins-integration-experiment' if include_twins else 'build/gx8002-fft-q15-exp-integration-experiment' if include_exp else 'build/gx8002-fft-q15-muldiv-integration-experiment' if include_muldiv else 'build/gx8002-fft-q15-addsub-integration-experiment' if include_addsub else 'build/gx8002-fft-q15-bidirectional-integration-experiment' if include_reverse_conversion else 'build/gx8002-fft-q15-conversion-integration-experiment' if include_conversion else 'build/gx8002-fft-q15-wrappers-integration-experiment' if include_wrappers else 'build/gx8002-fft-q15-core-integration-experiment' if include_core else 'build/gx8002-fft-q15-compare-integration-experiment' if include_compare else 'build/gx8002-fft-q15-unpack-integration-experiment' if include_unpack else 'build/gx8002-fft-q15-tail-integration-experiment' if tail_layout else 'build/gx8002-placed-fft-fill-integration-experiment' if include_fill else 'build/gx8002-placed-fft-integration-experiment')
    report_path=out/'build-report.json';report=json.loads(report_path.read_text())
    image=(out/'firmware_codec.unadmitted.bin').read_bytes();assert sha(image)==report['firmware_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x396a0','--stop-address=0x396ee',str(wrapper)],text=True))
    cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,image,mode,seed)
            loaded=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10003000,0x1001708c,4))
            assert result==0 and loaded==image[0x3b940:0x4f9cc]
            cases+=1
    result={'include_clock':include_clock,'include_uart_cluster':include_uart_cluster,'include_uart':include_uart,'include_exception':include_exception,'include_centered':include_centered,'include_reducer_scale':include_reducer_scale,'include_cosine':include_cosine,'include_sine':include_sine,'include_polynomial':include_polynomial,'include_fmod':include_fmod,'include_math_wrappers':include_math_wrappers,'include_logexp':include_logexp,'include_power':include_power,'include_sqrt':include_sqrt,'include_scale':include_scale,'include_memset':include_memset,'include_copy':include_copy,'include_tokenizer':include_tokenizer,'include_sign':include_sign,'include_fixunsigned':include_fixunsigned,'include_udiv':include_udiv,'include_widen':include_widen,'include_muldi':include_muldi,'include_float':include_float,'include_uint':include_uint,'include_make':include_make,'include_twins':include_twins,'include_exp':include_exp,'include_muldiv':include_muldiv,'include_addsub':include_addsub,'include_reverse_conversion':include_reverse_conversion,'include_conversion':include_conversion,'include_wrappers':include_wrappers,'include_core':include_core,'include_compare':include_compare,'include_unpack':include_unpack,'tail_layout':tail_layout,'include_fill':include_fill,'integration_report_sha256':sha(report_path.read_bytes()),'firmware_sha256':sha(image),
            'loader_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded stock loader applied to full composed integration image. Does not execute the full application or qualify hardware/timing.']}
    (ROOT/('docs/research/gx8002-fft-q15-clock-integration-loader.json' if include_clock else 'docs/research/gx8002-fft-q15-uart-cluster-integration-loader.json' if include_uart_cluster else 'docs/research/gx8002-fft-q15-uart-integration-loader.json' if include_uart else 'docs/research/gx8002-fft-q15-exception-integration-loader.json' if include_exception else 'docs/research/gx8002-fft-q15-centered-integration-loader.json' if include_centered else 'docs/research/gx8002-fft-q15-reducer-scale-integration-loader.json' if include_reducer_scale else 'docs/research/gx8002-fft-q15-cosine-integration-loader.json' if include_cosine else 'docs/research/gx8002-fft-q15-sine-integration-loader.json' if include_sine else 'docs/research/gx8002-fft-q15-polynomial-integration-loader.json' if include_polynomial else 'docs/research/gx8002-fft-q15-fmod-integration-loader.json' if include_fmod else 'docs/research/gx8002-fft-q15-math-wrappers-integration-loader.json' if include_math_wrappers else 'docs/research/gx8002-fft-q15-logexp-integration-loader.json' if include_logexp else 'docs/research/gx8002-fft-q15-power-integration-loader.json' if include_power else 'docs/research/gx8002-fft-q15-sqrt-integration-loader.json' if include_sqrt else 'docs/research/gx8002-fft-q15-scale-integration-loader.json' if include_scale else 'docs/research/gx8002-fft-q15-memset-integration-loader.json' if include_memset else 'docs/research/gx8002-fft-q15-copy-integration-loader.json' if include_copy else 'docs/research/gx8002-fft-q15-tokenizer-integration-loader.json' if include_tokenizer else 'docs/research/gx8002-fft-q15-sign-integration-loader.json' if include_sign else 'docs/research/gx8002-fft-q15-fixunsigned-integration-loader.json' if include_fixunsigned else 'docs/research/gx8002-fft-q15-udiv-integration-loader.json' if include_udiv else 'docs/research/gx8002-fft-q15-widen-integration-loader.json' if include_widen else 'docs/research/gx8002-fft-q15-muldi-integration-loader.json' if include_muldi else 'docs/research/gx8002-fft-q15-float-integration-loader.json' if include_float else 'docs/research/gx8002-fft-q15-uint-integration-loader.json' if include_uint else 'docs/research/gx8002-fft-q15-make-integration-loader.json' if include_make else 'docs/research/gx8002-fft-q15-twins-integration-loader.json' if include_twins else 'docs/research/gx8002-fft-q15-exp-integration-loader.json' if include_exp else 'docs/research/gx8002-fft-q15-muldiv-integration-loader.json' if include_muldiv else 'docs/research/gx8002-fft-q15-addsub-integration-loader.json' if include_addsub else 'docs/research/gx8002-fft-q15-bidirectional-integration-loader.json' if include_reverse_conversion else 'docs/research/gx8002-fft-q15-conversion-integration-loader.json' if include_conversion else 'docs/research/gx8002-fft-q15-wrappers-integration-loader.json' if include_wrappers else 'docs/research/gx8002-fft-q15-core-integration-loader.json' if include_core else 'docs/research/gx8002-fft-q15-compare-integration-loader.json' if include_compare else 'docs/research/gx8002-fft-q15-unpack-integration-loader.json' if include_unpack else 'docs/research/gx8002-fft-q15-tail-integration-loader.json' if tail_layout else 'docs/research/gx8002-fft-fill-integration-loader.json' if include_fill else 'docs/research/gx8002-fft-integration-loader.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['loader_cases'],'integration loader cases')
