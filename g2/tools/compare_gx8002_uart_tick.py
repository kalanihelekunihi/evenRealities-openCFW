#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted UART dispatcher execution with modeled dependencies."""
import json
import re
import struct
import subprocess
from link_gx8002_uart_tick import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from compare_gx8002_uart_putc import register_list
from verify_gx8002_memcpy_source import decode


def execute(code,start,targets,packet,entries,crc,callback_result):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x9000
    initial=r.copy();memory={a:0xa5 for a in range(0x8e00,0x9000)}
    memory.update({0x2002e360+i:v for i,v in enumerate(entries)})
    def read(a,n):
        if any(a+i not in memory for i in range(n)):raise ValueError('outside memory')
        return sum(memory[a+i]<<(8*i) for i in range(n))
    pc,condition,saved,trace=start,False,None,[]
    for _ in range(1000):
        op,args,size=code[pc];p=[x.strip() for x in args.split(',')];following=pc+size
        if op=='push':saved={x:r[x] for x in register_list(args)};r['r14']-=len(saved)*4
        elif op=='pop':
            if saved is None or set(saved)!=set(register_list(args)):raise ValueError('save mismatch')
            r.update(saved);r['r14']+=len(saved)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI restore failure')
            return r['r0'],trace
        elif op in ('ld.b','ld.h','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported operand')
            reg,ptr,off=m.groups();r[reg]=read(r[ptr]+int(off,0),{'ld.b':1,'ld.h':2,'ld.w':4}[op])
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','lsli'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&0xffffffff
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('br','bt','bf','bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            take={'br':True,'bt':condition,'bf':not condition}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        elif op in ('bsr','jsr'):
            if op=='jsr':
                target=r[p[0]];data=bytes(read(r['r0']+i,1) for i in range(32))
                trace.append(('callback',target,r['r1'],data.hex()));result=callback_result
            else:
                kind=targets.get(int(p[0],0))
                if kind=='queue':
                    if r['r0']!=0x2002ecc4:raise ValueError('wrong queue')
                    trace.append(('queue',));result=int(packet is not None)
                    if packet is not None:
                        for i,v in enumerate(packet):
                            if r['r1']+i not in memory:raise ValueError('packet outside stack')
                            memory[r['r1']+i]=v
                elif kind=='crc':trace.append(('crc',r['r0'],r['r1'],r['r2']));result=crc
                elif kind=='printf':trace.append(('printf',r['r0'],r['r1']));result=13
                else:raise ValueError('unknown direct call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    placement=link();output=ROOT/'build/gx8002-uart-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x118c0','--stop-address=0x11948',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_uart_async_tick',str(output/'tick.elf')],text=True))
    targets={0x1053c:'queue',0x12e34:'crc',0x101b0:'printf'};linked={a+0x101f6a74:k for a,k in targets.items()};cases=0
    for present in (False,True):
     for flags in (0,1,2,255):
      for valid in (False,True):
       for index in (-1,0,1,7,15):
        for result in (0,1,0xffffffff):
            packet=bytearray(32);struct.pack_into('<H',packet,4,0x1234);packet[7]=flags
            struct.pack_into('<I',packet,16,0x4000);packet[20]=2
            struct.pack_into('<II',packet,24,17,0x12345678 if valid else 0)
            entries=bytearray(16*28)
            for i in range(16):
                entries[i*28]=1 if i%2==0 else 2
                struct.pack_into('<I',entries,i*28+4,0x1234 if i%2==0 else 0x1235)
            if index>=0:
                for i in range(index,16):
                    entries[i*28]=2
                    struct.pack_into('<I',entries,i*28+4,0x1234)
                    struct.pack_into('<II',entries,i*28+20,0x5000+i*4,0x6000+i*4)
            value=bytes(packet) if present else None
            a=execute(old,0x118c0,targets,value,entries,0x12345678,result)
            b=execute(new,0x10208334,linked,value,entries,0x12345678,result)
            trace=[('queue',)];expected=0xffffffff
            if present:
                if flags==1:trace.append(('crc',0,0x4000,17))
                if flags==1 and not valid:trace.append(('printf',0x1020b17d,17))
                elif index>=0:
                    trace.append(('callback',0x5000+index*4,0x6000+index*4,packet.hex()));expected=result
            if a!=b or a!=(expected,trace):raise ValueError('dispatcher mismatch')
            cases+=1
    report={'placement':placement,'cases':cases,'source_admitted':False,
            'limits':['Queue, CRC, logging and callback calls modeled; no hardware timing claim.',
                      'Finite packet/registration states; firmware integration pending.']}
    (ROOT/'docs/research/gx8002-uart-tick-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
