#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise explicit IRQ software frames; hardware IRQ instructions are boundaries."""
import json
import re
import subprocess
from build_gx8002_irq_entry_candidate import build
from verify_gx8002_memcpy_source import decode
from link_gx8002_uart_console import ROOT


def execute(code,start,seed,depth=0,stack=None,stack_top=0x8000,architecture=False,interrupt_pc=None,initial_registers=None,body_target=0x10025598):
    regs={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)}
    regs.update({f'fr{i}':(seed^((i+1)*0x1234567))&0xffffffff for i in range(8)})
    if initial_registers is not None:regs.update(initial_registers)
    regs['r14']=stack_top;original=regs.copy();stack={} if stack is None else stack
    outer=stack.copy();pc=start;low=regs['r14'];peak=stack_top;phase=0;calls=0
    epc=(seed^0x12345678)&0xffffffff;epsr=(seed^0x87654321)&0xffffffff
    initial_control=(epc,epsr)
    volatile=['r0','r1','r2','r3','r12','r13']
    def push(value):
        regs['r14']-=4
        if regs['r14'] in stack:raise ValueError('hardware frame overlaps saved state')
        stack[regs['r14']]=value
    def pop():
        if regs['r14'] not in stack:raise ValueError('uninitialized hardware restore')
        value=stack.pop(regs['r14']);regs['r14']+=4
        return value
    injected=False
    for _ in range(40):
        if depth and interrupt_pc==pc and not injected:
            if not architecture:raise ValueError('boundary injection requires architecture model')
            injected=True
            nested=execute(code,start,seed^0xdeadbeef,depth-1,stack,regs['r14'],True,
                           interrupt_pc=interrupt_pc,initial_registers=regs.copy(),body_target=body_target)
            peak=min(peak,regs['r14']-nested['modeled_peak_bytes'])
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='nie':
            if phase!=0:raise ValueError('entry order')
            if architecture:push(epc);push(epsr)
            phase=1
        elif op=='ipush':
            if phase!=1:raise ValueError('hardware save order')
            if architecture:
                for name in reversed(volatile):push(regs[name])
            phase=2
        elif op in ('subi','addi'):
            if p[:2]!=['r14','r14']:raise ValueError('unexpected stack adjustment')
            amount=int(p[2],0);regs['r14']+=amount if op=='addi' else -amount;low=min(low,regs['r14'])
        elif op in ('stm','ldm','fstms','fldms'):
            match=re.fullmatch(r'(r|fr)(\d+)-(?:r|fr)(\d+), \(r14\)',args)
            if not match:raise ValueError('unsupported save range')
            kind,first,last=match.groups();names=[kind+str(i) for i in range(int(first),int(last)+1)]
            for i,name in enumerate(names):
                address=regs['r14']+i*4
                if not regs['r14']<=address<stack_top:raise ValueError('save outside frame')
                if op in ('stm','fstms'):
                    if address in stack:raise ValueError('overlapping saves')
                    stack[address]=regs[name]
                else:
                    if address not in stack:raise ValueError('uninitialized restore')
                    regs[name]=stack.pop(address)
        elif op=='bsr':
            if int(p[0],0)!=body_target:raise ValueError('unexpected body target')
            calls+=1
            if architecture:
                for name in volatile:regs[name]^=0xffffffff
                epc^=0xffffffff;epsr^=0xffffffff
            # Model arbitrary body clobbers of state explicitly protected by
            # this software wrapper, independently of IPUSH's hardware state.
            for name in regs:
                if name.startswith('fr') or name.startswith('r') and int(name[1:])>=15:regs[name]^=0xffffffff
            # Model the C body's observed PUSH LR at the callback point.
            call_sp=regs['r14']-4
            if call_sp in stack:raise ValueError('callback frame overlaps saved state')
            sentinel=(seed^0xface1234)&0xffffffff
            stack[call_sp]=sentinel;peak=min(peak,call_sp)
            if depth and interrupt_pc is None:
                nested=execute(code,start,seed^0xdeadbeef,depth-1,stack,call_sp,architecture,body_target=body_target)
                if nested['calls']!=1:raise ValueError('nested model failure')
                peak=min(peak,call_sp-nested['modeled_peak_bytes'])
            if stack.pop(call_sp)!=sentinel:raise ValueError('callback return address corrupted')
        elif op=='ipop':
            if phase!=2:raise ValueError('hardware restore order')
            expected_sp=original['r14']-(32 if architecture else 0)
            if regs['r14']!=expected_sp:raise ValueError('unbalanced software frame')
            if architecture:
                for name in volatile:regs[name]=pop()
                if any(regs[name]!=original[name] for name in volatile):raise ValueError('volatile register restoration failure')
            elif stack!=outer:raise ValueError('unbalanced software frame')
            if any(regs[name]!=original[name] for name in regs if name.startswith('fr') or name.startswith('r') and int(name[1:])>=15):raise ValueError('register restoration failure')
            phase=3
        elif op=='nir':
            if phase!=3 or calls!=1:raise ValueError('return order')
            if architecture:
                epsr=pop();epc=pop()
                if (epc,epsr)!=initial_control:raise ValueError('control register restoration failure')
                if stack!=outer or regs['r14']!=original['r14']:raise ValueError('unbalanced hardware frame')
            if depth and interrupt_pc is not None and not injected:raise ValueError('injection point not reached')
            if architecture and regs!=original:raise ValueError('complete register restoration failure')
            return {'calls':calls,'software_frame_bytes':original['r14']-low-(32 if architecture else 0),'modeled_peak_bytes':stack_top-min(low,peak)}
        else:raise ValueError('unexpected wrapper instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=build();prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    code=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(ROOT/'build/gx8002-irq/entry.elf')],text=True));cases=0
    for seed in (0,1,0xffffffff,0x55555555,0xaaaaaaaa,0x80000000):
        for depth in range(4):
            result=execute(code,0x10025574,seed,depth)
            if result!={'calls':1,'software_frame_bytes':100,'modeled_peak_bytes':104*(depth+1)}:raise ValueError('frame result mismatch')
            cases+=1
    report={'build':evidence,'cases':cases,'software_bytes_per_returning_callback_level':104,'modeled_depths':[1,2,3,4],'modeled_peak_bytes':[104,208,312,416],'source_admitted':False,'limits':['Checks only explicit software saves; NIE/IPUSH/IPOP/NIR hardware state not simulated.', 'Recursive checks share software stack memory; hardware IRQ frames are excluded, so this is not actual nested IRQ execution.', 'C dispatch, callback ABI, stack capacity and hardware timing remain separate qualification.']}
    (ROOT/'docs/research/gx8002-irq-software-frame-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
