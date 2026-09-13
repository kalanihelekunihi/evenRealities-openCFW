# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_backup_dma_select import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,allocation,token,channel,gate_hook=None,irq_hook=None,state_address=0x2002d3e8,helper_addresses=None,count=None):
    memory={state_address+4:len(allocation) if count is None else count}
    memory.update({state_address+0x370+i:value for i,value in enumerate(allocation)})
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x2002f000;r['r0']=channel
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r5','r15'];condition=False
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('Receive frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Receive restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bt','bf'):
            if condition == (op=='bt'):jump=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='bnez':
            if r[p[0]]!=0:jump=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='br':jump=int(args,0)
        elif op=='ldbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not m:raise ValueError('Postincrement byte operand')
            reg,base_reg=m.groups();addr=r[base_reg]
            if addr not in memory:raise ValueError('Postincrement byte address')
            r[reg]=memory[addr]&255;trace.append(('read',addr,r[reg]))
            r[base_reg]=(addr+1)&0xffffffff
        elif op in ('ld.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op in ('ld.w','ld.b'):r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            if helper_addresses is not None:
                if target not in helper_addresses:raise ValueError('Relocated deallocation helper')
                target=helper_addresses[target]
            save=target in (0xffe2eaec,0x10025560)
            if save:
                if irq_hook is not None and irq_hook(True,r['r0'])!=token:raise ValueError('Deallocation IRQ save result')
                trace.append(('irq_save',))
            elif target in (0xffe2eaf8,0x1002556c):
                if r['r0']!=token:raise ValueError('Selection IRQ token')
                if irq_hook is not None:irq_hook(False,r['r0'])
                trace.append(('irq_restore',token))
            elif target in (0xffe2e60c,0x10025080):
                trace.append(('resource',r['r0'],r['r1']))
                if gate_hook is not None:gate_hook(r['r0'],r['r1'])
            else:raise ValueError('Selection helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=token if save else 0xffffffff
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),str(path));assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d4ac','--stop-address=0x3d500',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-select/select.disassembly.txt').read_text())
    cases=0;state=0x2002d3e8
    for flags,count,token in product(product((0,1,2,255),repeat=3),(0,1,2,3,0xffffffff),(0,0x98765432)):
        a=execute(old,0x3d4ac,flags,token,0,count=count,helper_addresses={0x3d1ac:0x10025560,0x3d1b8:0x1002556c,0x3c528:0x10025080})
        b=execute(new,0x10004b6c,flags,token,0,count=count,helper_addresses={0x1000486c:0x10025560,0x10004878:0x1002556c,0x10003be8:0x10025080})
        assert a==b
        values=list(flags);selected=0xffffffff
        trace=[('irq_save',),('read',state+4,count)]
        for ch in range(min(count,2)):
            trace.append(('read',state+0x370+ch,values[ch]))
            if values[ch]==0:
                selected=ch;values[ch]=1
                trace += [('write',state+0x370+ch,1),('resource',25,1)]
                break
        trace.append(('irq_restore',token))
        assert a==(selected,trace,{state+4:count,**{state+0x370+i:v for i,v in enumerate(values)}})
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Explicit two-flag oracle, including zero/large counts and nonzero occupied flag variants.',
                      'IRQ/resource helpers modeled with caller clobbers; physical concurrency and placement remain unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-select-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],'selection cases passed')
