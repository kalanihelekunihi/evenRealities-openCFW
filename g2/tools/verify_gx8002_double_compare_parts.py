# SPDX-License-Identifier: MIT
import json,struct,subprocess,math
from itertools import product
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_unpack import execute as unpack
from execute_gx8002_double_compare_parts import execute
from execute_gx8002_double_ge import execute as ge

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x139ac','--stop-address=0x13e36',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};new=decode((path.parent/'runtime.disassembly.txt').read_text())
    values=[-1e300,-2147483648.0,-17.0,-1.5,-1.0,-5e-324,-0.0,0.0,5e-324,0.5,1.0,1.5,16.0,17.0,2147483648.0,4294967295.0,1e300]
    values += [math.nextafter(v,direction) for v in (1.0,16.0,2147483648.0) for direction in (0,math.inf)]
    fields=[]
    for value in values:
        bits=struct.unpack('<Q',struct.pack('<d',value))[0];a=unpack(old,0x13c90,bits);b=unpack(new,symbols['__unpack_d'],bits)
        if a!=b:raise ValueError('Compare unpack')
        fields.append(a)
    cases=0
    for i,j in product(range(len(values)),repeat=2):
        expected=(values[i]>values[j])-(values[i]<values[j])
        for code,entry in ((old,0x13d74),(new,symbols['__fpcmp_parts_d'])):
            if execute(code,entry,fields[i],fields[j])!=expected:raise ValueError(('Double parts comparison',i,j))
        if ge(old,0x139ac,values[i],values[j],0x13c90,0x13d74)!=expected or ge(new,symbols['__gedf2'],values[i],values[j],symbols['__unpack_d'],symbols['__fpcmp_parts_d'])!=expected:raise ValueError('Full GE wrapper')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Finite comparison corpus with decoded unpack inputs. GE wrapper executes with both decoded unpack calls and decoded comparison; separate helper frames; NaN/Infinity excluded. No full arithmetic equivalence claim.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-double-compare-parts.json').write_text(json.dumps(result,indent=2)+'\n');print('Compare pairs:',result['cases'])
