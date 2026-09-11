# SPDX-License-Identifier: MIT
import json,subprocess,struct,random
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_multiply import execute

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13364','--stop-address=0x13d74',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};new=decode((path.parent/'runtime.disassembly.txt').read_text())
    values={i/256 for i in range(4097)}
    import math
    for n in range(1,17):
        values.update((math.nextafter(float(n),0),math.nextafter(float(n),math.inf)))
    values.update((2.0**-32,math.nextafter(2.0**-32,0),math.nextafter(2.0**-32,math.inf)))
    rng=random.Random(0x8002)
    values.update(math.ldexp(1.0+rng.getrandbits(52)/2**52,rng.randrange(-32,0)) for _ in range(2048))
    integer_cases=[(a,b) for a in (0,1,0xffff,0x10000,0xffffffff,0x100000000,0xffffffffffffffff) for b in (0,1,0xffff,0x10000,0xffffffff,0x100000000,0xffffffffffffffff)]
    integer_cases.extend((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(2048))
    for a,b in integer_cases:
        if execute(old,0x13ab4,a,b,raw=True)!=(a*b)&0xffffffffffffffff:raise ValueError(('Integer multiply',a,b))
    executions=0
    for value in sorted(values):
        wanted=struct.unpack('<Q',struct.pack('<d',value*16.0))[0]
        for code,start,up,pack,mul in ((old,0x13694,0x13c90,0x13b00,0x13ab4),(new,symbols['__muldf3'],symbols['__unpack_d'],symbols['__pack_d'],None)):
            result=execute(code,start,value,16.0,up,pack,mul)
            if result!=wanted:raise ValueError(('Baud scaling multiplication',value,result,wanted))
            executions+=1
    return {'candidate':candidate,'integer_helper_cases':len(integer_cases),'input_cases':len(values),'executions':executions,'source_admitted':False,'limits':['Decoded multiply, integer multiply helper, unpack and pack in separate frames. Finite nonnegative scaling inputs (zero or normal); excludes subnormal results and exceptional values; not full IEEE special-value qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-scaling-multiply.json').write_text(json.dumps(result,indent=2)+'\n');print('Baud scaling executions:',result['executions'])
