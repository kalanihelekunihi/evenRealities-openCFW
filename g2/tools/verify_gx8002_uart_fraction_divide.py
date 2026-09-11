# SPDX-License-Identifier: MIT
import json,subprocess,struct,random
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uint_double_prepare import execute as uint_double
from execute_gx8002_double_multiply import execute
from execute_gx8002_double_subtract_prepare import execute as add
from execute_gx8002_double_fix_tail import execute as signed_fix
from execute_gx8002_double_ge import execute as ge
from verify_gx8002_double_uint_wrapper import execute as unsigned_fix

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12ff8','--stop-address=0x13e36',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};new=decode((path.parent/'runtime.disassembly.txt').read_text())
    rng=random.Random(0x8002)
    pairs=set()
    denominators={16,32,48,256,115200*16,0xfffffff0}
    denominators.update(16<<i for i in range(28))
    for denominator in denominators:
        for numerator in (0,1,denominator//2-1,denominator//2,denominator//2+1,denominator-1):
            pairs.add((numerator,denominator))
    for _ in range(2048):
        denominator=rng.randrange(1,0x10000000)*16
        pairs.add((rng.randrange(denominator),denominator))
    def as_float(bits):return struct.unpack('<d',struct.pack('<Q',bits))[0]
    executions=0
    chain_executions=0
    for numerator,denominator in sorted(pairs):
        wanted=struct.unpack('<Q',struct.pack('<d',numerator/denominator))[0]
        for code,start,up,pack,mul in ((old,0x13894,0x13c90,0x13b00,None),(new,symbols['__divdf3'],symbols['__unpack_d'],symbols['__pack_d'],None)):
            uint_entry=0x13a5c if code is old else symbols['__floatunsidf']
            numerator_bits=uint_double(code,uint_entry,numerator,pack,full=True)
            denominator_bits=uint_double(code,uint_entry,denominator,pack,full=True)
            result=execute(code,start,as_float(numerator_bits),as_float(denominator_bits),up,pack,mul)
            if result!=wanted:raise ValueError(('Baud division',numerator,denominator,result,wanted))
            executions+=1
            stock=code is old
            multiply_entry=0x13694 if stock else symbols['__muldf3']
            add_entry=0x13628 if stock else symbols['__adddf3']
            core=0x13364 if stock else symbols['_fpadd_parts']
            fix=0x139ec if stock else symbols['__fixdfsi']
            compare=0x139ac if stock else symbols['__gedf2']
            compare_parts=0x13d74 if stock else symbols['__fpcmp_parts_d']
            subtract=0x13658 if stock else symbols['__subdf3']
            scaled=execute(code,multiply_entry,as_float(result),16.0,up,pack,0x13ab4 if stock else None)
            rounded=add(code,add_entry,as_float(scaled),0.5,up,core,pack)
            converted,trace=unsigned_fix(code,0x12ff8 if stock else symbols['__fixunsdfsi'],as_float(rounded),{compare:'compare',subtract:'subtract',fix:'fix'},
                lambda value:signed_fix(code,fix,{},bits=struct.unpack('<Q',struct.pack('<d',value))[0],unpack_entry=up),
                lambda a,b:ge(code,compare,a,b,up,compare_parts),
                lambda a,b:add(code,subtract,a,b,up,core,pack))
            if converted!=int((numerator/denominator)*16.0+0.5):raise ValueError(('Baud fraction chain',numerator,denominator,converted))
            if [item[0] for item in trace]!=['compare','fix']:raise ValueError('Baud conversion call sequence')
            chain_executions+=1
    return {'candidate':candidate,'input_cases':len(pairs),'executions':executions,'chain_executions':chain_executions,'source_admitted':False,'limits':['Decoded divide then multiply, add and unsigned conversion including nested unpack/pack/compare/fix in separate frames. Integer inputs pass through decoded uint-to-double wrappers and pack. UART MMIO is not covered. Finite nonnegative scaling inputs (zero or normal); excludes subnormal results and exceptional values; not full IEEE special-value qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-fraction-divide.json').write_text(json.dumps(result,indent=2)+'\n');print('Baud division executions:',result['executions'])
