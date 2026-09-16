# SPDX-License-Identifier: MIT
"""Compare general finite power paths under explicit nearest-even arithmetic."""
import json,subprocess,struct,random
from decimal import Decimal,localcontext
from fractions import Fraction
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from gx8002_binary32_rational import operation,fused_operation

def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]

def value(raw):return struct.unpack('<f',struct.pack('<I',raw))[0]

def reference(x,y):
    # All sampled outputs are finite; use Decimal distances to choose
    # binary32 neighbors, avoiding reliance on intermediate binary64 rounding.
    exponent=value(y)
    if exponent.is_integer():
        exact=Fraction.from_float(value(x))**int(exponent)
        center=bits(float(exact))
        return min(range(max(0,center-1),center+2),key=lambda raw:(abs(Fraction.from_float(value(raw))-exact),raw&1))
    with localcontext() as context:
        context.prec=90
        exact=context.power(Decimal.from_float(value(x)),Decimal.from_float(value(y)))
        center=bits(float(exact))
        nearest=min(range(max(0,center-1),center+2),key=lambda raw:(abs(Decimal.from_float(value(raw))-exact),raw&1))
        return nearest

def verify(fused=False,wide=False):
    arithmetic=fused_operation if fused else operation
    path=ROOT/'build/gx8002-powf-placed/power.elf'
    report=json.loads((ROOT/'docs/research/gx8002-powf-placed.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x489fc','--stop-address=0x49c14',str(wrapper)],text=True))
    pairs=[(bits(x/16),bits(y/4)) for x in range(4,65) for y in range(-16,17)]
    rng=random.Random(7411);pairs += [(bits(rng.uniform(.25,4)),bits(rng.uniform(-4,4))) for _ in range(1000)]
    pairs += [(bits(-x/16),bits(y)) for x in range(4,65) for y in range(-16,17)]
    if wide:
        pairs += [(bits((1+f/8)*2.0**e),bits(y/4)) for e in range(-120,121,20) for f in (0,1,4,7) for y in (-4,-3,-1,1,3,4)]
        pairs += [(x,bits(y)) for x in (1,2,3,0x3fffff,0x7ffffe,0x7fffff,0x800000,0x800001) for y in (.25,.5,.75,1.0)]
        pairs += [(bits(2.0),bits(y)) for y in range(-150,128)]
    differences=[];accuracy_errors=[];max_ulp=0
    for x,y in pairs:
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        try:
            actual=execute(code,0x100100bc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
            original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        except Exception as error:raise RuntimeError('inputs %08x %08x'%(x,y)) from error
        expected=reference(x,y);ulp=abs(actual-expected);max_ulp=max(max_ulp,ulp)
        if ulp>1:accuracy_errors.append({'x':hex(x),'y':hex(y),'source':hex(actual),'reference':hex(expected),'ulp':ulp})
        if actual!=original:differences.append({'x':hex(x),'y':hex(y),'source':hex(actual),'stock':hex(original)})
    result={'wide':wide,'fused_accumulates':fused,'elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'cases':len(pairs),'differences':differences,'reference_precision':90,'integer_exponent_reference':'exact Fraction','max_ulp':max_ulp,'accuracy_errors':accuracy_errors,'source_admitted':False,'limits':['Positive bases .25..4 and exponents -4..4; negative bases -.25..-4 with integer exponents -16..16. Explicit finite nearest-even model with accumulator policy recorded by fused_accumulates, not hardware qualification. Exact Fraction for integer exponents and 90-digit Decimal otherwise; wider inputs and rounding-boundary proof remain pending.']}
    (ROOT/('docs/research/gx8002-powf-general-wide-fused.json' if wide and fused else 'docs/research/gx8002-powf-general-wide.json' if wide else 'docs/research/gx8002-powf-general-fused.json' if fused else 'docs/research/gx8002-powf-general.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],len(r['differences']),r['max_ulp'],r['accuracy_errors'][:3])
