# SPDX-License-Identifier: MIT
"""Execute negative-base fractional-exponent domain paths with symbolic FP results."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-powf-placed/power.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-powf-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x489fc','--stop-address=0x49c14',str(wrapper)],text=True))
    rng=random.Random(190)
    bases=[0x80000000|x for x in [1,0x7fffff,0x800000,0x3f7fffff,0x3f800000,0x3f800001,0x7f7fffff]+[rng.randrange(1,0x7f800000) for _ in range(1000)]]
    pairs=[(x,y) for x in bases for y in (0x3e800000,0x3f000000,0x3f400000,0x3fc00000,0xbe800000,0xbfc00000)]
    for x,y in pairs:
        traces=[]
        for instructions,entry in ((code,0x100100bc),(old,0x489fc)):
            calls=[]
            def arithmetic(op,a,b=None):
                calls.append((op,a,b))
                if op=='frecips':
                    assert a==0x3f800000
                    return a
                if op=='fsubs':
                    assert a==b
                    return 0
                assert op=='fdivs' and a==b==0
                return 0x7fc12345
            args=[x,y]+[0x76540000+i for i in range(2,16)]
            actual=execute(instructions,entry,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
            assert actual==0x7fc12345,(hex(x),hex(y),hex(actual))
            assert [c[0] for c in calls] in (['fsubs','fdivs'],['frecips','fsubs','fdivs'])
            traces.append(calls)
        # Some paths take absolute value first. Both must subtract equal operands
        # and propagate the symbolic invalid-division result unchanged.
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(pairs),'source_admitted':False,'limits':['Negative finite nonzero bases and six fractional exponents. Both execute equal-operand subtraction then zero/zero division and propagate a symbolic NaN. FP invalid flags, traps and actual NaN policy are not modeled.']}
    (ROOT/'docs/research/gx8002-powf-domain.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
