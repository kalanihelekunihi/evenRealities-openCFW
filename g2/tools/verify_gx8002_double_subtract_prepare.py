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
    values=(-1e300,-2147483648.0,-1.5,-5e-324,-0.0,0.0,5e-324,0.5,1.0,16.0,2147483648.0,4294967295.0,1e300);cases=0
    for left,right in product(values,repeat=2):
        a=execute(old,0x13658,left,right,0x13c90,0x13364)
        b=execute(new,symbols['__subdf3'],left,right,symbols['__unpack_d'],symbols['_fpadd_parts'])
        expected=[]
        for i,value in enumerate((left,right)):
            bits=struct.unpack('<Q',struct.pack('<d',value))[0]
            fields=unpack(old,0x13c90,bits)
            if i:fields[4]^=1
            expected.append(fields)
        if a!=b or a!=expected:raise ValueError('Subtraction input preparation')
        cases+=1
    full_cases=0
    for left in (2147483648.0,2147483648.5,2147483649.0,3000000000.25,4294967295.0):
        right=2147483648.0
        expected=struct.unpack('<Q',struct.pack('<d',left-right))[0]
        for code,start,up,add,pack in ((old,0x13658,0x13c90,0x13364,0x13b00),(new,symbols['__subdf3'],symbols['__unpack_d'],symbols['_fpadd_parts'],symbols['__pack_d'])):
            if execute(code,start,left,right,up,add,pack)!=expected:raise ValueError('Full subtraction result')
            full_cases+=1
    return {'full_subtraction_executions':full_cases,'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded subtraction wrapper through addition-core boundary, with decoded unpacking. Operand sign inversion and core pointers checked. Five unsigned-conversion subtraction inputs also execute the core and pack through return. Broader full subtraction remains unverified.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-double-subtract-prepare.json').write_text(json.dumps(result,indent=2)+'\n');print('Subtraction preparation pairs:',result['cases'])
