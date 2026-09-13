# SPDX-License-Identifier: MIT
"""Check source and stock uint conversion including runtime out-of-range conventions."""
import json,random,struct,math,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-fixunsdfsi-cluster/fix.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-fixunsdfsi-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old={}
    for start,end in [(0x49da4,0x49ddc),(0x4a460,0x4b17c)]:old.update(decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True)))
    values=[(s<<63)|(exp<<52)|frac for s in (0,1) for exp in range(2048) for frac in (0,1,1<<51,(1<<52)-1)]
    rng=random.Random(6432);values += [rng.getrandbits(64) for _ in range(2000)]
    for bits in values:
        args=[bits&0xffffffff,bits>>32]
        actual=execute(code,0x49da4-0x3b940+0x10003000,bytes(20),arguments=args)
        original=execute(old,0x49da4,bytes(20),arguments=args)
        x=struct.unpack('<d',bits.to_bytes(8,'little'))[0]
        if math.isnan(x):expected=0
        elif x>=2**31:expected=(min(int(x-2**31),2**31-1)+2**31) if math.isfinite(x) else 0xffffffff
        else:expected=max(int(x),-2**31) if math.isfinite(x) else -2**31
        expected&=0xffffffff
        assert actual==original==expected,(hex(bits),hex(actual),hex(original),hex(expected))
    result={'source_elf_sha256':sha(data),'cases':len(values),'source_admitted':False,'limits':['Sampled actual source/stock execution, including runtime saturation/wrapping outside the ISO C conversion domain. Integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-fixunsdfsi-stock.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
