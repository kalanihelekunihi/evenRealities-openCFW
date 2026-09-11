# SPDX-License-Identifier: MIT
import json,subprocess,struct
from itertools import product
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_subtract_prepare import execute
from execute_gx8002_double_unpack import execute as unpack

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13364','--stop-address=0x13d74',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};new=decode((path.parent/'runtime.disassembly.txt').read_text())
    values={i/256 for i in range(4097)}
    import math
    for n in range(17):
        values.update((math.nextafter(float(n),0),math.nextafter(float(n),math.inf)))
    executions=0
    for value in sorted(values):
        wanted=struct.unpack('<Q',struct.pack('<d',value+0.5))[0]
        for code,start,up,add,pack in ((old,0x13628,0x13c90,0x13364,0x13b00),(new,symbols['__adddf3'],symbols['__unpack_d'],symbols['_fpadd_parts'],symbols['__pack_d'])):
            result=execute(code,start,value,0.5,up,add,pack)
            if result!=wanted:raise ValueError(('Baud rounding addition',value,result,wanted))
            executions+=1
    return {'candidate':candidate,'input_cases':len(values),'executions':executions,'source_admitted':False,'limits':['Decoded add wrapper, unpack, core and pack in separate frames. Finite baud-rounding inputs only; not full IEEE special-value qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-rounding-add.json').write_text(json.dumps(result,indent=2)+'\n');print('Baud addition executions:',result['executions'])
