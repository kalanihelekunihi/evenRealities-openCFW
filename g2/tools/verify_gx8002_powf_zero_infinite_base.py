# SPDX-License-Identifier: MIT
"""Execute signed zero/infinite-base power paths and sign/parity decisions."""
import json,random,subprocess,struct
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
    rng=random.Random(925)
    exponents=[(sign<<31)|y for sign in (0,1) for y in [0,1,0x7fffff,0x3e800000,0x3f000000,0x3f800000,0x40000000,0x40400000,0x4b7fffff,0x4b800000,0x7f7fffff]+[rng.randrange(0x7f800000) for _ in range(1000)]]
    pairs=[(x,y) for x in (0,0x80000000,0x7f800000,0xff800000) for y in exponents]
    def arithmetic(op,a,b=None,c=None):
        if op=='fmacs':
            assert a==b==c==0x7f800000
            return a
        if op=='fnegs':return a^0x80000000
        if op=='frecips':
            assert a&0x7fffffff in (0,0x7f800000)
            return (a&0x80000000)|(0x7f800000 if a&0x7fffffff==0 else 0)
        if op=='fmuls':
            assert a==b and a&0x7fffffff in (0,0x7f800000)
            return a&0x7fffffff
        raise AssertionError((op,a,b))
    for x,y in pairs:
        exponent=struct.unpack('<f',struct.pack('<I',y))[0]
        odd=exponent.is_integer() and int(exponent)%2!=0
        sign=0x80000000 if x>>31 and odd else 0
        expected=0x3f800000 if exponent==0 else sign|(0x7f800000 if ((x&0x7fffffff)!=0)==(exponent>0) else 0)
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        actual=execute(code,0x100100bc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        assert actual==original==expected,(hex(x),hex(y),hex(actual),hex(original),hex(expected))
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(pairs),'source_admitted':False,'limits':['Signed zero/infinite bases with sampled finite exponents. Explicit reciprocal, square and negation of zero/infinity; no exception flags or traps modeled.']}
    (ROOT/'docs/research/gx8002-powf-zero-infinite-base.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
