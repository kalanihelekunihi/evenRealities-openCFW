#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute full flash initialization with continuous register and stack state."""
import contextlib
import io
import json
import re
import subprocess
from compare_gx8002_flash_selection import verify as verify_selection, ROOT, decode


def execute(code,pc,delta,seed,configuration_value,discovery,first,second,readonly_configuration=None):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)}
    r['r14']=0x2002f7fc;top=r['r14'];stack={};trace=[];saved=False;initial=r.copy();frame_top=top;loads=0;carry=None;low=top
    for _ in range(160):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args not in ('r4, r15','r4-r5, r15') or saved:raise ValueError('unexpected setup frame')
            names=['r4','r15'] if args=='r4, r15' else ['r4','r5','r15']
            r['r14']-=4*len(names);frame_top=r['r14']
            stack.update({r['r14']+i*4:r[n] for i,n in enumerate(names)});saved=True
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','lsli','rotli'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)))&0xffffffff
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown setup store')
            value,base,off=m.groups();address=r[base]+int(off,0)
            if r['r14']<=address<top:
                if address>=frame_top:raise ValueError('overwrites saved register')
                stack[address]=r[value]
            elif address in (0xa0300090,0xa2000008,0xa200002c,0xa20000f0,0xa2000014,0xa200001c,0x200264fc,0x20026500):
                trace.append(['write',address,r[value]])
            else:raise ValueError('unexpected setup address')
        elif op=='bsr':
            if not saved or top-r['r14']!=32:raise ValueError('call frame')
            target=int(args,0)+delta
            if target==0x10025d74:
                pointer=r['r1']
                if readonly_configuration is None:
                    if pointer!=r['r14']+20 or stack.get(pointer)!=0:raise ValueError('configuration input mismatch')
                    input_value=stack[pointer]
                else:
                    if pointer not in readonly_configuration or readonly_configuration[pointer]!=0:raise ValueError('constant configuration input mismatch')
                    input_value=readonly_configuration[pointer]
                if r['r0']!=9:raise ValueError('configuration operation mismatch')
                trace.append(['call',target,9,'initialized-input',0])
                if configuration_value!=0:raise ValueError('initializer configuration must remain zero')
                trace.extend([['write',0xa000003c,input_value&1],['write',0x20027314,input_value&1]])
            elif target==0x10025080:
                trace.append(['call',target,r['r0'],r['r1']])
            elif target in (0x1002364c,0x1002375c,0x10024190,0x100242b4,0x10024330,0x100242ec):trace.append(['call',target])
            elif target==0x1002436c:
                try:arguments=[r[f'r{i}'] for i in range(4)]+[stack[r['r14']+i*4] for i in range(5)]
                except KeyError:raise ValueError('uninitialized XIP argument')
                trace.append(['xip',arguments])
            else:raise ValueError('unknown setup call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xdeadbeef^(i*0x11111111))&0xffffffff
            if target==0x10024190:r['r0']=discovery&0xffffffff
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown state load')
            dst,reg,offset=m.groups();address=r[reg]+int(offset,0)
            if address==0x200264f0:
                loads+=1
                if loads>2:raise ValueError('excess state reads')
                value=0x20028000 if loads==1 else 0x20029000
            elif address==0x20028004 and loads==1:value=first
            elif address==0x20029004 and loads==2:value=second
            else:raise ValueError('unknown state address')
            r[dst]=value;trace.append(['read',address,value])
        elif op in ('cmpne','cmplt','cmphs','cmphsi'):
            a=r[p[0]];b=int(p[1],0) if op=='cmphsi' else r[p[1]]
            if op=='cmplt':a=a-(1<<32) if a&0x80000000 else a;b=b-(1<<32) if b&0x80000000 else b
            carry=a!=b if op=='cmpne' else a<b if op=='cmplt' else a>=b
        elif op in ('br','bt','bf','bnez'):
            if op in ('bt','bf') and carry is None:raise ValueError('undefined branch')
            if op=='br' or op=='bnez' and r[p[0]]!=0 or op in ('bt','bf') and carry==(op=='bt'):following=int(p[-1],0)
        elif op=='pop':
            expected='r4-r5, r15' if len(names)==3 else 'r4, r15'
            if args!=expected or r['r14']!=frame_top:raise ValueError('unbalanced return frame')
            for i,name in enumerate(names):r[name]=stack[frame_top+i*4]
            r['r14']+=len(names)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('ABI mismatch')
            return {'result':r['r0'],'trace':trace,'frame_bytes':top-low}
        else:raise ValueError('unsupported full instruction '+op)
        low=min(low,r['r14']);pc=following
    raise ValueError('setup execution bound exceeded')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):selection=verify_selection()
    out=ROOT/'build/gx8002-board'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x16604','--stop-address=0x166ba',str(out/'selection-stock.elf')],text=True))
    new=decode((out/'flash.disassembly.txt').read_text());cases=0
    prefix=[['call',0x10025d74,9,'initialized-input',0],['write',0xa000003c,0],['write',0x20027314,0],['call',0x10025080,13,1],['call',0x1002364c]]
    prefix += [['write',a,v] for a,v in [(0xa0300090,1),(0xa2000008,0),(0xa200002c,78),(0xa20000f0,1),(0xa2000014,2),(0xa200001c,31),(0xa2000008,1)]]
    prefix += [['call',0x1002375c],['call',0x10024190]]
    ids=[0,0xffffffff,0x80000000,0x1c3811,0x1c3812,0x1c3813,0x1c3814,0x854012,0x856013,0x856014,0x204016]
    for failure in (0,1,0xffffffff):
        for first in ids:
            for second in (0,0x204016,0xffffffff):
                expected=prefix.copy()
                if not failure:
                    expected += [['read',0x200264f0,0x20028000],['read',0x20028004,first]]
                    if first in (0x854012,0x856013):expected.append(['call',0x10024330])
                    elif first not in (0x1c3812,0x1c3813):expected.append(['call',0x100242b4])
                    expected += [['read',0x200264f0,0x20029000],['read',0x20029004,second]]
                    if second==0x204016:expected.append(['call',0x100242ec])
                    expected += [['write',0x200264fc,0x10023788],['write',0x20026500,0x10023cac],['xip',[235,8,1,24,4,0,1,4,4]]]
                for seed in (0,0xffffffff):
                    for output in (0,):
                        for code,entry,delta,frame in ((old,0x16604,0x1000dfec,32),(new,0x100245f0,0,32)):
                            result=execute(code,entry,delta,seed,output,failure,first,second,readonly_configuration=None if delta else {selection['build']['configuration_constant']['runtime_address']:0})
                            if result!={'result':0 if failure else 0x20026504,'trace':expected,'frame_bytes':frame}:raise ValueError('full flash mismatch')
                        cases+=1
    report={'selection':selection,'cases':cases,'source_admitted':False,'stock_frame_bytes':32,'candidate_frame_bytes':32,'limits':['Full decoded function with modeled returning services; end-to-end composition, state/interface ownership and physical behavior remain unresolved.','Source-defined read-only configuration removes the extra stack word; physical stack capacity and interrupt interaction remain unqualified.']}
    (ROOT/'docs/research/gx8002-flash-full-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
