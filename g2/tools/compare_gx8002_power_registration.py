#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted registration execution; memcpy is modeled with exact record copy."""
import json
import re
import struct
import subprocess
from link_gx8002_suspend_registration import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode
from compare_gx8002_uart_putc import register_list


def execute(code,start,copy_target,state,record):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=0x1000;initial=r.copy()
    memory={0x2002dfbc+i:v for i,v in enumerate(state)};memory.update({0x1000+i:v for i,v in enumerate(record)})
    def read(a):
        if any(a+i not in memory for i in range(4)):raise ValueError('outside memory')
        return sum(memory[a+i]<<(8*i) for i in range(4))
    pc,condition,saved,writes=start,False,None,[]
    for _ in range(300):
        op,args,size=code[pc];p=[x.strip() for x in args.split(',')];following=pc+size
        if op=='push':saved={x:r[x] for x in register_list(args)}
        elif op=='pop':
            if saved is None or set(saved)!=set(register_list(args)):raise ValueError('save mismatch')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15)):raise ValueError('ABI restore failure')
            return r['r0'],bytes(memory[0x2002dfbc+i] for i in range(len(state))),writes
        elif op in ('ld.w','st.w','ldr.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 3)\)',args)
            if not m:raise ValueError('unsupported operand')
            reg,ptr,off=m.groups();a=r[ptr]+(r[off.split()[0]]<<3 if '<<' in off else int(off,0))
            if op!='st.w':r[reg]=read(a)
            else:
                read(a);writes.append(('word',a,r[reg]))
                for i in range(4):memory[a+i]=(r[reg]>>(8*i))&255
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','lsli','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a<<b if op=='lsli' else a+b)&0xffffffff
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('br','bt','bf','bez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            take={'br':True,'bt':condition,'bf':not condition}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        elif op=='bsr':
            if int(p[0],0)!=copy_target or r['r1']!=0x1000 or r['r2']!=8:raise ValueError('bad copy call')
            destination=r['r0'];read(destination);read(destination+4)
            writes.append(('copy',destination,record.hex()))
            for i,v in enumerate(record):memory[destination+i]=v
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=destination
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    placement=link();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=output/'registration-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data);cases=0
    for mode,name in enumerate(('suspend','resume')):
        offset=0x10c4c+mode*88;array=16+mode*64;counter=8+mode*4
        old=decode(subprocess.check_output([str(prefix)+'objdump','-D',f'--start-address={offset}',f'--stop-address={offset+88}',str(wrapper)],text=True))
        new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_register_'+name,str(output/'suspend-registration.elf')],text=True))
        for count in range(10):
         for match in range(-1,8):
          for callback in (0,0x5000):
           for private in (0,0xffffffff):
            state=bytearray([0xa5]*144);struct.pack_into('<I',state,counter,count)
            for i in range(8):struct.pack_into('<II',state,array+i*8,0x6000+i*4,i)
            if match>=0:
                for i in range(match,8):struct.pack_into('<I',state,array+i*8,callback)
            record=struct.pack('<II',callback,private);expected=state.copy();writes=[];result=0xffffffff
            index=match if match>=0 else count if count<8 and callback else None
            if index is not None:
                destination=array+index*8;expected[destination:destination+8]=record;writes.append(('copy',0x2002dfbc+destination,record.hex()));result=0
                if match<0:struct.pack_into('<I',expected,counter,count+1);writes.append(('word',0x2002dfbc+counter,count+1))
            oracle=(result,bytes(expected),writes)
            if execute(old,offset,0xffe2ecc4,state,record)!=oracle or execute(new,offset+0x101f6a74,0x10025738,state,record)!=oracle:raise ValueError('registration mismatch')
            cases+=1
    report={'placement':placement,'cases':cases,'source_admitted':False,'limits':['Memcpy call modeled; no concurrent state mutation or overlapping input.','Existing state storage and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-power-registration-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
