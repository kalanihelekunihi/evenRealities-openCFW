#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted event-tick comparison including application replacement callbacks."""
import json
import re
import struct
import subprocess
from link_gx8002_app_tick import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from compare_gx8002_uart_putc import register_list
from verify_gx8002_memcpy_source import decode


def execute(code,start,targets,queued,active,event_callback,loop_callback,mutation):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x9000
    initial=r.copy();memory={a:0xa5 for a in range(0x8f00,0x9000)}
    for a,n in ((0x20026d38,4),(0x4000,16),(0x4100,16)):
        memory.update({a+i:0 for i in range(n)})
    def write(a,value):
        if any(a+i not in memory for i in range(4)):raise ValueError('outside write memory')
        for i in range(4):memory[a+i]=(value>>(8*i))&255
    def read(a):
        if any(a+i not in memory for i in range(4)):raise ValueError('outside memory')
        return sum(memory[a+i]<<(8*i) for i in range(4))
    write(0x20026d38,0x4000 if active else 0)
    write(0x4008,0x5000 if event_callback else 0);write(0x400c,0x5004 if loop_callback else 0)
    write(0x410c,0x5008)
    pc,saved,trace=start,None,[]
    for _ in range(100):
        op,args,size=code[pc];p=[x.strip() for x in args.split(',')];following=pc+size
        if op=='push':saved={x:r[x] for x in register_list(args)};r['r14']-=len(saved)*4
        elif op=='pop':
            if saved is None or set(saved)!=set(register_list(args)):raise ValueError('save mismatch')
            r.update(saved);r['r14']+=len(saved)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI restore failure')
            return r['r0'],trace
        elif op in ('st.w','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported operand')
            reg,ptr,off=m.groups();a=r[ptr]+int(off,0)
            if op=='st.w':write(a,r[reg])
            else:r[reg]=read(a)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='bez':
            if r[p[0]]==0:following=int(p[1],0)
        elif op in ('bsr','jsr'):
            result=0xffffffff
            if op=='bsr':
                kind=targets.get(int(p[0],0))
                if kind=='queue':
                    if r['r0']!=0x2002ecd8 or read(r['r1']) or read(r['r1']+4):raise ValueError('bad queue/initial event')
                    trace.append(('queue',));result=int(queued)
                    if queued:write(r['r1'],0x12345678);write(r['r1']+4,0x9abcdef0)
                elif kind in ('uart','watchdog'):trace.append((kind,))
                else:raise ValueError('unknown direct call')
            else:
                target=r[p[0]]
                if target==0x5000:
                    trace.append(('event',read(r['r0']),read(r['r0']+4)))
                    if mutation=='clear':write(0x20026d38,0)
                    elif mutation=='replace':write(0x20026d38,0x4100)
                elif target in (0x5004,0x5008):trace.append(('loop',target))
                else:raise ValueError('unknown callback')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    placement=link();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x122d4','--stop-address=0x12324',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.LvpAppEventTick',str(output/'tick.elf')],text=True))
    targets={0x1053c:'queue',0x118c0:'uart',0xfd2c:'watchdog'};linked={a+0x101f6a74:k for a,k in targets.items()};cases=0
    for queued in (False,True):
     for active in (False,True):
      for event in (False,True):
       for loop in (False,True):
        for mutation in ('none','clear','replace'):
            args=(queued,active,event,loop,mutation)
            a=execute(old,0x122d4,targets,*args);b=execute(new,0x10208d48,linked,*args)
            trace=[('queue',)];current=0x4000 if active else 0
            if queued and active and event:
                trace.append(('event',0x12345678,0x9abcdef0))
                if mutation=='clear':current=0
                elif mutation=='replace':current=0x4100
            if current==0x4100:trace.append(('loop',0x5008))
            elif current and loop:trace.append(('loop',0x5004))
            trace.extend([('uart',),('watchdog',)])
            if a!=b or a!=(0,trace):raise ValueError('event tick mismatch')
            cases+=1
    report={'placement':placement,'cases':cases,'source_admitted':False,
            'limits':['Modeled queue, callbacks and services; no concurrent mutation outside calls.',
                      'Hardware timing and firmware integration remain pending.']}
    (ROOT/'docs/research/gx8002-app-tick-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
