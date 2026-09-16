# SPDX-License-Identifier: MIT
"""Execute NaN dispatch and canonical result construction without an FP model."""
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
    rng=random.Random(34741);nans=[(s<<31)|0x7f800000|p for s in (0,1) for p in [1,0x3fffff,0x400000,0x7fffff]+[rng.randrange(1,1<<23) for _ in range(100)]]
    other=[0,0x80000000,1,0x80000001,0x3f000000,0xbf000000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f800000,0xff800000]
    pairs=[pair for n in nans for x in other for pair in ((n,x),(x,n))]+[(n,n) for n in nans]
    for x,y in pairs:
        expected=0x3f800000 if (y&0x7fffffff)==0 or (x&0x7fffffff)==0x3f800000 else 0x7fc00000
        args=[x,y]+[0x76540000+i for i in range(2,16)]
        actual=execute(code,0x100100bc,bytes(20),float_arguments=args,return_float=True)
        original=execute(old,0x489fc,bytes(20),float_arguments=args,return_float=True)
        assert actual==original==expected,(hex(x),hex(y),hex(actual),hex(original),hex(expected))
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(pairs),'source_admitted':False,'limits':['Actual compiled integer NaN dispatch and canonical bit construction; no floating arithmetic callback. Preserves observed +/-1 to NaN exponent behavior. Architectural effects of moving signaling NaNs and FP status are not modeled; other exceptional paths pending.']}
    (ROOT/'docs/research/gx8002-powf-nan.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
