# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_body_schedule_stock import execute
from execute_gx8002_uart_body_schedule_source import execute as source


def verify():
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x1140c','--stop-address=0x11454',str(wrapper)],text=True));cases=0
    new=decode((ROOT/'build/gx8002-uart-body-probe/body.linked.disassembly.txt').read_text())
    for port,alignment,count,remaining,status in product((0,1),range(16),(1,15,16,17,32),(1,31,32,33,47,48,65),(0,0xffffffff)):
        base=0x20060000+alignment;packet=0x20041000;cursor=0x20042000;length=cursor+4;stack=0x20043000;counter=0x2002e358+4*port
        memory={}
        def put(addr,value):
            for i in range(4):memory[addr+i]=(value>>(8*i))&255
        def get(addr):return sum(memory[addr+i]<<(8*i) for i in range(4))
        for addr,value in ((packet+16,base),(cursor,0x20050000),(length,0),(stack,0xa5a5a5a5),(counter,count)):put(addr,value)
        regs=dict(r1=count,r2=count+remaining,r4=0,r7=0x2002e050+port*4,r8=cursor,r9=length,r10=port,r11=packet,r14=stack)
        other=memory.copy()
        sr=dict(r1=count,r18=count+remaining,r4=packet,r5=port,r6=length,r7=cursor,r8=0x2002e358,r14=stack)
        source_stop,source_regs,source_trace=source(new,other,sr,helper_result=status)
        stop,r,trace=execute(code,memory,regs,helper_result=status)
        schedule=remaining>32 and base+count>(base&~15)+16
        calls=[x for x in trace if isinstance(x[0],str)]
        wanted=[('stop',port),('async',port,base+count,remaining&~15,0x10207ee0,0)] if schedule else []
        if calls!=wanted or get(counter)!=count+((remaining&~15) if schedule else 0) or get(cursor)!=(0x2002e520 if schedule else 0x20050000):raise ValueError('Async scheduling mismatch')
        source_calls=[x for x in source_trace if isinstance(x[0],str)]
        if source_calls!=wanted or other!=memory or source_regs['r0']!=0:raise ValueError('Upstream scheduling mismatch')
        cases+=1
    return {'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Stock/upstream scheduling boundaries, helper returns/clobbers modeled. DMA execution and whole-function composition remain pending.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-schedule-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print('Scheduling cases:',r['decoded_cases'])
