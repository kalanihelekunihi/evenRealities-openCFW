#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode compact IRQ context and dispatch together with ABI-compliant callbacks."""
import contextlib,io,json,re
from build_gx8002_irq_compact_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,status,handler,private,seed=0,depth=0,interrupt_pc=None,stack=None,stack_top=0x8000,initial_registers=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    r.update({f'fr{i}':(seed^i*0x1234567)&MASK for i in range(8)})
    if initial_registers is not None:r.update(initial_registers)
    r['r14']=stack_top;original=r.copy();stack={} if stack is None else stack
    outer=stack.copy();low=r['r14'];peak=low;pc=0x10025574;injected=False
    epc=seed^0x12345678;epsr=seed^0x87654321;control=(epc,epsr);trace=[];phase=0
    volatile=['r0','r1','r2','r3','r12','r13'];irq=((status&511)-32)&MASK
    def push(v):
        r['r14']-=4
        if r['r14'] in stack:raise ValueError('overlapping save')
        stack[r['r14']]=v
    def pop():
        if r['r14'] not in stack:raise ValueError('uninitialized restore')
        v=stack.pop(r['r14']);r['r14']+=4;return v
    for _ in range(64):
        if depth and pc==interrupt_pc and not injected:
            if phase==0:raise ValueError('interrupted control not yet saved')
            injected=True
            nested=execute(code,status,handler,private,seed^MASK,depth-1,interrupt_pc,
                           stack,r['r14'],r.copy())
            peak=min(peak,r['r14']-nested['peak_bytes'])
            # A nested exception overwrites EPC/EPSR. The outer return must
            # recover its original values from the NIE frame, not these regs.
            epc=pc;epsr=seed^0xabcdef01
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='nie':
            if phase:raise ValueError('entry order')
            push(epc);push(epsr);phase=1
        elif op=='ipush':
            if phase!=1:raise ValueError('save order')
            for n in reversed(volatile):push(r[n])
            phase=2
        elif op=='push':
            if args!='r15':raise ValueError('link save')
            push(r['r15'])
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op in ('subi','addi','andi','lsli','addu'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a&b if op=='andi' else a<<b if op=='lsli' else a+b)&MASK
        elif op in ('stm','ldm','fstms','fldms'):
            m=re.fullmatch(r'(r|fr)(\d+)-(?:r|fr)(\d+), \(r14\)',args)
            if not m:raise ValueError('save range')
            kind,first,last=m.groups()
            for i,n in enumerate(range(int(first),int(last)+1)):
                a=r['r14']+i*4;name=kind+str(n)
                if op in ('stm','fstms'):
                    if a in stack:raise ValueError('overlapping save')
                    stack[a]=r[name]
                else:
                    if a not in stack:raise ValueError('uninitialized restore')
                    r[name]=stack.pop(a)
        elif op=='ldr.w':
            if args!='r2, (r3, r0 << 3)':raise ValueError('slot addressing')
            a=(r['r3']+(r['r0']<<3))&MASK
            if a!=(0x20026ef4+irq*8)&MASK:raise ValueError('slot address')
            trace.append(['read',a,handler]);r['r2']=handler
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);dst,base,off=m.groups();a=(r[base]+int(off,0))&MASK
            if a in stack:r[dst]=stack.pop(a)
            elif a==0xe000ec00:r[dst]=status;trace.append(['read',a,status])
            elif a==(0x20026ef8+irq*8)&MASK:r[dst]=private;trace.append(['read',a,private])
            else:raise ValueError('unknown load')
        elif op=='bez':
            if not r[p[0]]:next_pc=int(p[1],0)
        elif op=='jsr':
            if r['r14']!=original['r14']-124 or r[p[0]]!=handler or [r['r0'],r['r1']]!=[irq,private]:raise ValueError('callback contract')
            trace.append(['call',handler,irq,private])
            for n in volatile+['r15']+[f'r{i}' for i in range(18,32)]+[f'fr{i}' for i in range(8)]:r[n]^=MASK
            epc^=MASK;epsr^=MASK
        elif op=='ipop':
            if phase!=2 or r['r14']!=original['r14']-32:raise ValueError('software frame')
            for n in volatile:r[n]=pop()
            phase=3
        elif op=='nir':
            if phase!=3:raise ValueError('return order')
            epsr=pop();epc=pop()
            if stack!=outer or r!=original or (epc,epsr)!=control:raise ValueError('context restoration')
            if depth and not injected:raise ValueError('injection point not reached')
            return {'trace':trace,'peak_bytes':original['r14']-min(low,peak)}
        else:raise ValueError('unknown compact instruction '+op)
        low=min(low,r['r14']);pc=next_pc
    raise ValueError('compact bound')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    if not evidence['byte_exact']:raise ValueError('compact bytes differ')
    code=decode((ROOT/'build/gx8002-irq/compact.disassembly.txt').read_text());cases=0
    for irq in range(32):
     for high in (0,0x200,0x80000000,0xfffffe00):
      status=high|(irq+32)
      for handler in (0,0x10026000):
       for seed in (0,0xffffffff,0x12345678):
        private=seed^0x20028000;expected=[['read',0xe000ec00,status],['read',0x20026ef4+irq*8,handler]]
        if handler:expected += [['read',0x20026ef8+irq*8,private],['call',handler,irq,private]]
        if execute(code,status,handler,private,seed)!={'trace':expected,'peak_bytes':124}:raise ValueError('compact effects')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Full context and dispatch for valid vectors32..63 with modeled ABI-compliant callbacks. Nested control timing, invalid vector domains and callback stack usage remain separate.']}
    (ROOT/'docs/research/gx8002-irq-compact-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
