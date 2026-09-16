# SPDX-License-Identifier: MIT
"""Compare stock/source exceptional expf instruction paths without inventing FP policy."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-log-exp-placed/math.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-log-exp-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x49300','--stop-address=0x4950c',str(wrapper)],text=True))
    rng=random.Random(94315)
    nonfinite=[(sign<<31)|0x7f800000|f for sign in (0,1) for f in [0,1,0x3fffff,0x400000,0x7fffff]+[rng.randrange(1<<23) for _ in range(100)]]
    cases=0
    for bits in nonfinite:
        for result_bits in (0x7fc00001,0xffa12345,0x7fc98765):
            nan=(bits&0x7fffffff)>0x7f800000
            expected=[('fadds',bits,bits)] if nan else []
            expected_result=result_bits if nan else (0 if bits>>31 else bits)
            for code,entry in ((source,0x49300-0x3b940+0x10003000),(old,0x49300)):
                calls=[]
                def operation(op,*args):
                    calls.append((op,*args))
                    return result_bits
                actual=execute(code,entry,bytes(20),float_arguments=[bits],return_float=True,float_operation=operation)
                assert calls==expected and actual==expected_result,(hex(bits),calls,expected,hex(actual))
            cases+=1
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'paired_cases':cases,'nonfinite_inputs':len(nonfinite),'source_admitted':False,'limits':['NaN paths issue x+x and propagate symbolic result; positive infinity is returned unchanged and negative infinity returns positive zero. No hardware NaN/status/trap policy modeled.']}
    (ROOT/'docs/research/gx8002-expf-special-paths.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
