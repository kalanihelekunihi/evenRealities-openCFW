# SPDX-License-Identifier: MIT
"""Finite scaling execution using exact integer binary32 multiplication, nearest-even."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def parts(bits):
    e=(bits>>23)&255;assert e!=255
    return bits>>31,(bits&0x7fffff)|((1<<23) if e else 0),e-150 if e else -149

def rounded(sign,mant,power):
    if not mant:return sign<<31
    high=mant.bit_length()-1+power
    if high>127:return (sign<<31)|0x7f800000
    if high< -150:return sign<<31
    quantum=max(high-23,-149);shift=quantum-power
    if shift>0:
        q,r=divmod(mant,1<<shift);half=1<<(shift-1);q+=r>half or (r==half and q&1)
    else:q=mant<<-shift
    if not q:return sign<<31
    high=q.bit_length()-1+quantum
    if high>127:return (sign<<31)|0x7f800000
    if high< -126:return (sign<<31)|q
    if q.bit_length()>24:q>>=1
    return (sign<<31)|((high+127)<<23)|(q&0x7fffff)

def operation(op,a,b):
    assert op=='fmuls', 'Finite scaling should only multiply'
    sa,ma,pa=parts(a);sb,mb,pb=parts(b)
    return rounded(sa^sb,ma*mb,pa+pb)

def verify(corrected=False,placed=False):
    path=ROOT/('build/gx8002-scalbnf-placed/scale.elf' if placed else 'build/gx8002-scalbnf-corrected/scale.elf' if corrected else 'build/gx8002-scalbnf-probe/scale.elf');data=path.read_bytes()
    report=json.loads((ROOT/('docs/research/gx8002-scalbnf-placed.json' if placed else 'docs/research/gx8002-scalbnf-corrected.json' if corrected else 'docs/research/gx8002-scalbnf-probe.json')).read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x49ad4','--stop-address=0x49c04',str(wrapper)],text=True))
    pairs=[((s<<31)|(e<<23)|f,n) for s in (0,1) for e in range(255) for f in (0,1,0x7fffff) for n in (-50001,-300,-25,-1,0,1,25,300,50001)]
    rng=random.Random(325);pairs += [(rng.randrange(0x7f800000)|(rng.randrange(2)<<31),rng.randrange(-300,301)) for _ in range(3000)]
    if corrected:
        pairs += [((s<<31)|(e<<23)|f,n) for s in (0,1) for e in range(255) for f in (0,1,0x3fffff,0x400000,0x7fffff) for n in (-e-25,-e-24,-e-23,-e-22,-e-21, -2147483648,2147483647)]
    mismatches=[];stock_differences=[]
    for bits,n in pairs:
        kw={'arguments':[n&0xffffffff],'float_arguments':[bits],'return_float':True,'float_operation':operation}
        actual=execute(code,0x49ad4-0x3b940+0x10003000 if placed else 0x10019000,bytes(20),**kw);original=execute(old,0x49ad4,bytes(20),**kw)
        sign,mant,power=parts(bits);expected=rounded(sign,mant,power+n)
        if corrected:
            assert actual==expected,(hex(bits),n,hex(actual),hex(expected))
            if actual!=original:stock_differences.append({'input':hex(bits),'exponent':n,'stock':hex(original),'corrected':hex(actual)})
        else:assert actual==original,(hex(bits),n,hex(actual),hex(original))
        if actual!=expected:mismatches.append({'input':hex(bits),'exponent':n,'source_and_stock':hex(actual),'nearest_even':hex(expected)})
    result={'placed':placed,'corrected':corrected,'stock_differences':stock_differences,'source_elf_sha256':sha(data),'cases':len(pairs),'rounding_mismatches':mismatches,'source_admitted':False,'limits':['Finite values with explicit nearest-even integer multiplication model, not hardware execution. Nonfinite behavior, FP status/other rounding modes, full int32 exponent range, placement and integration pending.']}
    (ROOT/('docs/research/gx8002-scalbnf-placed-finite.json' if placed else 'docs/research/gx8002-scalbnf-corrected-finite.json' if corrected else 'docs/research/gx8002-scalbnf-finite.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],len(r['rounding_mismatches']),r['rounding_mismatches'][:3])
