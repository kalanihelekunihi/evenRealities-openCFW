# SPDX-License-Identifier: MIT
import json,struct,subprocess
from itertools import product
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_configure import execute
from verify_gx8002_uint_double_prepare import execute as uint_double
from execute_gx8002_double_multiply import execute as multiply
from execute_gx8002_double_subtract_prepare import execute as add
from execute_gx8002_double_fix_tail import execute as signed_fix
from execute_gx8002_double_ge import execute as ge
from verify_gx8002_double_uint_wrapper import execute as unsigned_fix


def arithmetic(code,s):
    def number(a):return struct.unpack('<d',struct.pack('<II',*a))[0]
    def run(kind,r):
        if kind=='uint':return uint_double(code,s['uint'],r[0],s['pack'],full=True)
        a=number(r[:2])
        if kind in ('divide','multiply'):return multiply(code,s[kind],a,number(r[2:]),s['unpack'],s['pack'],s.get('integer'))
        if kind=='add':return add(code,s['add'],a,number(r[2:]),s['unpack'],s['core'],s['pack'])
        if kind!='fix':raise ValueError(kind)
        result,_=unsigned_fix(code,s['fix'],a,{s['compare']:'compare',s['subtract']:'subtract',s['signed']:'fix'},
            lambda v:signed_fix(code,s['signed'],{},bits=struct.unpack('<Q',struct.pack('<d',v))[0],unpack_entry=s['unpack']),
            lambda a,b:ge(code,s['compare'],a,b,s['unpack'],s['compare_parts']),
            lambda a,b:add(code,s['subtract'],a,b,s['unpack'],s['core'],s['pack']))
        return result
    return run


def verify(composed_fifo=False,composed_irq=False,replacement=None):
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc8ec','--stop-address=0x17574',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    new=decode((path.parent/'runtime.disassembly.txt').read_text())
    stock=dict(uint=0x13a5c,divide=0x13894,multiply=0x13694,add=0x13628,fix=0x12ff8,pack=0x13b00,unpack=0x13c90,integer=0x13ab4,core=0x13364,compare=0x139ac,compare_parts=0x13d74,signed=0x139ec,subtract=0x13658,fifo=0xc8ec,irq=0xffe2eac8)
    names=dict(uint='__floatunsidf',divide='__divdf3',multiply='__muldf3',add='__adddf3',fix='__fixunsdfsi',pack='__pack_d',unpack='__unpack_d',core='_fpadd_parts',compare='__gedf2',compare_parts='__fpcmp_parts_d',signed='__fixdfsi',subtract='__subdf3')
    source={k:symbols[v] for k,v in names.items()};source.update(fifo=0x10203360,irq=0x1002553c)
    fifo_candidate=None
    if composed_fifo:
        from build_gx8002_uart_fifo_depth import build as build_fifo
        fifo_candidate=build_fifo()
        new.update(decode((ROOT/'build/gx8002-uart-fifo-depth/fifo_depth.disassembly.txt').read_text()))
    irq_candidate=None
    if composed_irq:
        from link_gx8002_irq import link
        irq_candidate=link()
        irq_path=ROOT/'build/gx8002-irq/irq.elf'
        new.update(decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(irq_path)],text=True)))
    new_entry=symbols['open_cfw_gx8002_uart_configure']
    if replacement is not None:
        replacement_path,new_entry,replacement_helpers=replacement
        new.update(decode(replacement_path.read_text()))
    setups=[(old,0xc954,stock),(new,new_entry,source)]
    helpers=[({s[k]:k for k in ('uint','divide','multiply','add','fix','fifo','irq')},arithmetic(code,s)) for code,_,s in setups]
    if replacement is not None:helpers[1]=(replacement_helpers,helpers[1][1])
    cases=0;arithmetic_cases=0
    depths=(0,1,2,3,4,8,16,32,64,127,128,255) if composed_fifo else (0,16,128,2048)
    for rx,tx,depth_input,mode in product((0,1,2,3,0xffffffff),(0,1,2,3,4),depths, (0,1)):
        depth=(depth_input<<4 if depth_input and not depth_input&(depth_input-1) else 0) if composed_fifo else depth_input
        for changed in (False,True):
            d=[0x12340000+i for i in range(32)];device=0xa0100000;other=0xa0200000
            d[1]=device;d[3]=(0,24000000,0xffffffff,32768)[cases%4];d[4]=(0,115200,1,0xfffffff,2048,9600)[cases%6]
            d[7]=0 if cases%2 else 7;d[8]=0 if cases%3 else 2;d[9]=mode;d[15]=(6,7,31,32)[cases%4] if composed_irq else 6
            regs={base+off:0xa5a50000+off for base in (device,other) for off in range(0,0x100,4)}
            current=other if changed else device;regs[current+0x9c]=rx;regs[current+0xa0]=tx
            regs[device+0xf4]=(depth_input<<16)|0xa5001234
            from verify_gx8002_uart_fifo_depth import execute as fifo_execute
            results=[]
            for (code,entry,s),(h,fn) in zip(setups,helpers):
                hook=(lambda dev,param: fifo_execute(code,s['fifo'],dev,param)) if composed_fifo else None
                from execute_gx8002_linked_irq_registration import execute as irq_execute
                irq_hook=(lambda number,handler,private:irq_execute(code,0x17550 if code is old else 0x1002553c,number,handler,private,0x174c0 if code is old else 0x100254ac)) if composed_irq else None
                results.append(execute(code,entry,d,regs,h,fn,depth,current if changed else None,fifo_hook=hook,irq_hook=irq_hook))
            if results[0]!=results[1]:
                a,b=results
                mismatch=next(((x,y) for x,y in zip(a[2],b[2]) if x!=y),None)
                raise ValueError(('UART configuration mismatch',cases,mismatch,a[0],b[0]))
            result,memory,trace=results[0];wanted=d.copy();wanted[1]=current;wanted[7]=d[7] or 8;wanted[8]=d[8] or 1
            if d[4]:
                denominator=(d[4]<<4)&0xffffffff;divisor,remainder=divmod(d[3],denominator)
                wanted[5]=divisor;wanted[6]=int(remainder/denominator*16+0.5);arithmetic_cases+=1
            wanted[12]=depth
            if rx in (0,1,2,3):wanted[14]=(1,depth//4,depth//2,(depth-2)&0xffffffff)[rx]
            if tx in (0,1,2,3):wanted[13]=(0,2,depth//4,depth//2)[tx]
            wanted[11]=1;wanted[26]=wanted[31]=0xffffffff
            if result or [memory[0x20026a94+i*4] for i in range(32)]!=wanted:raise ValueError(('UART descriptor oracle',cases))
            fifo_control=127 if mode else 111
            expected_writes=[(device+4,0),(device+16,34 if mode else 3),(device+8,fifo_control)]
            control=regs[device+12]
            if d[4]:expected_writes.extend(((device+8,0),(device+12,control|128),(device,wanted[5]&255),(device+4,(wanted[5]>>8)&255),(device+0xc0,wanted[6]&255),(device+12,control),(device+8,fifo_control)))
            expected_writes.extend(((device+8,0),(device+12,(control&~31)|3),(device+8,fifo_control)))
            irq_writes=[] if d[15]>=32 else [(0x20026ef4+d[15]*8,0x10203278),(0x20026ef8+d[15]*8,0x20026a94),(0xe000e100,1<<d[15])]
            if composed_irq and irq_writes:expected_writes.append(irq_writes[-1])
            observed_writes=[(item[1],item[3]) for item in trace if item[0]=='write' and item[1]>=0xa0000000]
            if observed_writes!=expected_writes:raise ValueError(('UART ordered MMIO oracle',cases))
            irq_index=next(i for i,item in enumerate(trace) if item[0]=='irq')
            if trace[irq_index]!=('irq',d[15],0x10203278,0x20026a94):raise ValueError('UART IRQ arguments')
            if composed_irq and trace[irq_index+1:]!=[('write',address,4,value) for address,value in irq_writes]:raise ValueError('UART IRQ ordered writes')
            cases+=1
    return {'candidate':candidate,'irq_candidate':irq_candidate,'composed_irq':composed_irq,'irq_executions':cases*2 if composed_irq else 0,'fifo_candidate':fifo_candidate,'composed_fifo':composed_fifo,'fifo_executions':cases*2 if composed_fifo else 0,'cases':cases,'arithmetic_cases':arithmetic_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Ordered descriptor/MMIO reads and writes and helper arguments compared. Arithmetic helpers execute decoded bodies in separate frames. IRQ registration and VIC enable execute together in a separate decoded frame when composed_irq is true; otherwise registration is modeled. FIFO helper executes decoded instructions in a separate frame when composed_fifo is true; otherwise its return is modeled. An injected device-pointer change after FIFO return tests descriptor reload ordering. No physical UART, concurrent interrupt execution or zero shifted denominator qualification.']}


if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-configure-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('UART configuration cases:',result['cases'])
