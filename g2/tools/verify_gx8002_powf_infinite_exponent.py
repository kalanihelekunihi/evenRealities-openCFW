# SPDX-License-Identifier: MIT
"""Execute infinite-exponent power dispatch with exact expected limiting values."""
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
    rng=random.Random(517)
    bases=[(sign<<31)|x for sign in (0,1) for x in [0,1,0x7fffff,0x800000,0x3f7fffff,0x3f800000,0x3f800001,0x7f7fffff,0x7f800000]+[rng.randrange(0x7f800000) for _ in range(1000)]]
    pairs=[(x,y) for x in bases for y in (0x7f800000,0xff800000)]
    def arithmetic(op,a,*args):
        assert op=='fnegs' and a==0xff800000
        return 0x7f800000
    for x,y in pairs:
        magnitude=x&0x7fffffff
        expected=0x3f800000 if magnitude==0x3f800000 else (0x7f800000 if ((magnitude>0x3f800000)==(y==0x7f800000)) else 0)
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        actual=execute(code,0x100100bc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True,float_operation=arithmetic)
        assert actual==original==expected,(hex(x),hex(y),hex(actual),hex(original),hex(expected))
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(pairs),'source_admitted':False,'limits':['Sampled signed finite/infinite bases and infinite exponents, excluding NaN bases. Only FP callback is sign negation of negative infinity; status effects and other exceptional paths remain unmodeled.']}
    (ROOT/'docs/research/gx8002-powf-infinite-exponent.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
