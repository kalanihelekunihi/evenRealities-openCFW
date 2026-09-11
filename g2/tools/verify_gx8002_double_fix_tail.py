# SPDX-License-Identifier: MIT
import json,math,subprocess,struct
from execute_gx8002_double_unpack import execute as unpack
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_fix_tail import execute

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x139ec','--stop-address=0x13d80',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-uart-configure/runtime.disassembly.txt').read_text())
    linked=ROOT/'build/gx8002-uart-configure/runtime.elf'
    target=Elf32(linked.read_bytes(),str(linked))
    entry=next(s['value'] for s in target.symbols() if s['name']=='__fixdfsi')+16
    if new[entry][:2]!=('ld.w','r3, (r14, 0x8)'):raise ValueError('Fix tail entry changed')
    unpack_entry=next(s['value'] for s in target.symbols() if s['name']=='__unpack_d')
    compositions=0;full_calls=0
    values={i/256 for i in range(-4352,4353)}
    for n in (-2147483648,-2147483647,-1,0,1,2147483647):
        values.update(x for x in (float(n),math.nextafter(float(n),0),math.nextafter(float(n),math.inf)) if -2147483648<=x<2147483648)
    for value in values:
        if not value:fields={0:2,4:0,8:0,12:0,16:0}
        else:
            fraction,exponent=math.frexp(abs(value));scaled=int(fraction*(1<<61))
            fields={0:3,4:int(value<0),8:(exponent-1)&0xffffffff,12:scaled&0xffffffff,16:scaled>>32}
        bits=struct.unpack('<Q',struct.pack('<d',value))[0]
        for program,start,unpack_start in ((old,0x139ec,0x13c90),(new,entry-16,unpack_entry)):
            for seed in (0,0xffffffff):
                result=execute(program,start,{},seed,bits=bits,unpack_entry=unpack_start)
                if result!=(int(value)&0xffffffff):raise ValueError('Full signed conversion')
                full_calls+=1
        for producer,producer_entry in ((old,0x13c90),(new,unpack_entry)):
            decoded_fields=unpack(producer,producer_entry,bits)
            for offset,actual in decoded_fields.items():
                if fields[offset]!=actual:raise ValueError('Unpack to conversion field')
            for consumer,consumer_entry in ((old,0x139fc),(new,entry)):
                for seed in (0,0xffffffff):
                    result=execute(consumer,consumer_entry,decoded_fields,seed)
                    if result!=(int(value)&0xffffffff):raise ValueError(('Composed signed conversion',value,result))
                    compositions+=1
    return {'candidate':candidate,'cases':len(values),'composed_executions':compositions,'full_function_executions':full_calls,'source_admitted':False,'limits':['Decoded unpack output feeds decoded conversion tail across all stock/source producer-consumer combinations. Full function entry, spills, unpack call and return also executed; unpack has a separate decoded frame. Unwritten zero fields tested with two seeds. Finite in-range doubles, no NaN/overflow claim. Out-of-range shift intermediates modeled zero before conditional selection.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-double-fix-tail.json').write_text(json.dumps(result,indent=2)+'\n');print('Signed fix tail cases:',result['cases'])
