# SPDX-License-Identifier: MIT
"""Execute placed/stock power identity paths against exact binary32 results."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_sqrtf_source import oracle as sqrt_oracle
from verify_gx8002_scalbnf_finite import operation as multiply
from gx8002_binary32_rational import divide

def operation(op,a,b=None):
    if op=='frecips':return divide(0x3f800000,a)
    return divide(a,b) if op=='fdivs' else multiply(op,a,b)

def verify():
    path=ROOT/'build/gx8002-powf-placed/power.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-powf-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x489fc','--stop-address=0x49c14',str(wrapper)],text=True))
    rng=random.Random(7135)
    values=[(e<<23)|f for e in range(255) for f in (0,1,0x3fffff,0x400000,0x7fffff)]
    values += [rng.randrange(0x7f800000) for _ in range(2000)]
    pairs=[(x,y,expected) for x in values for y,expected in ((0,0x3f800000),(0x80000000,0x3f800000),(0x3f800000,x),(0x3f000000,sqrt_oracle(x)))]
    pairs += [(x|0x80000000,y,expected) for x in values for y,expected in ((0,0x3f800000),(0x80000000,0x3f800000),(0x3f800000,x|0x80000000))]
    pairs += [(x|(sign<<31),0x40000000,multiply('fmuls',x,x)) for x in values for sign in (0,1)]
    pairs += [(x|(sign<<31),0xbf800000,divide(0x3f800000,x|(sign<<31))) for x in values if x for sign in (0,1)]
    for x,y,expected in pairs:
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        actual=execute(source,0x489fc-0x3b940+0x10003000,bytes(20),float_arguments=args,return_float=True,float_operation=operation)
        original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True,float_operation=operation)
        assert actual==original==expected,(hex(x),hex(y),hex(actual),hex(original),hex(expected))
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'paired_cases':len(pairs),'source_admitted':False,'limits':['Finite x with signed-zero/one/two exponents and nonzero finite bases with minus-one exponents and nonnegative finite x with exponent one-half only. Exact oracle with nearest-even integer multiplication and rational division; actual compiled dependency calls. General power approximation, nonfinite inputs, negative fractional powers, FP status/modes and hardware pending.']}
    (ROOT/'docs/research/gx8002-powf-identities.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
