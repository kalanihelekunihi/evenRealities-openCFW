# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_backup_dma_irq import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32

STATE=0x2002d3e8
CALLBACKS=0x200174a8

def execute(code,entry,pending,callbacks,mutation,status,clear_hook=None,deallocate_hook=None,callback_hook=None,private_data=(0x1234,0x5678),state_address=STATE,callback_address=CALLBACKS,helper_addresses=None):
    STATE=state_address;CALLBACKS=callback_address
    memory={STATE:0xa1000000,0xa10002e8:pending}
    memory.update({CALLBACKS+i*4:v for i,v in enumerate((*callbacks,*private_data))})
    r={f'r{i}':0x70000000+i for i in range(32)};r['r14']=0x2002f000
    initial=r.copy();saved=None;trace=[];pc=entry;condition=False
    def helper(kind,arg,target=None):
        trace.append((kind,arg) if target is None else (kind,target,arg))
        if kind=='clear' and clear_hook is not None:clear_hook(arg,memory[STATE])
        if kind=='deallocate' and deallocate_hook is not None:deallocate_hook(arg)
        if kind=='callback' and callback_hook is not None:callback_hook(target,arg)
        if mutation:
            if kind=='clear':memory[STATE]=0xa1001000+arg*0x1000
            elif kind=='deallocate':
                memory[CALLBACKS+arg*4]=0x10208098 if arg==0 else 0
                memory[CALLBACKS+8+arg*4]=0xabcd0000+arg
            elif kind=='callback':
                memory[CALLBACKS+4]=0x102030e4
                memory[CALLBACKS+12]=0x87654321
                memory[0xa10002e8]=0
        for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        r['r0']=status
    for _ in range(150):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            match=re.fullmatch(r'r4-r(\d+), r15',args)
            if not match or saved is not None:raise ValueError('IRQ frame')
            regs=[f'r{i}' for i in range(4,int(match[1])+1)]+['r15']
            saved=[r[x] for x in regs];r['r14']-=4*len(regs)
        elif op=='pop':
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('IRQ ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addi','lsli','lsl','asr','lsr','andi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a<<b if op in ('lsli','lsl') else a>>b if op=='lsr' else (a if a<0x80000000 else a-0x100000000)>>b if op=='asr' else a&b)&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='bnez':
            if r[p[0]]!=0:jump=int(p[1],0)
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op in ('ld.w','st.w','ldr.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if m:reg,base,offset=m.groups();addr=(r[base]+int(offset,0))&0xffffffff
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
                if not m:raise ValueError('IRQ operand '+args)
                reg,base,index,shift=m.groups();addr=(r[base]+(r[index]<<int(shift)))&0xffffffff
            if op=='st.w':memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
            else:r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)+(0x101f6a74 if entry==0xd068 else 0)
            if helper_addresses is not None:
                if target not in helper_addresses:raise ValueError('Relocated IRQ helper')
                target=helper_addresses[target]
            if target not in (0x10203804,0x10203a98):raise ValueError('IRQ helper')
            helper('clear' if target==0x10203804 else 'deallocate',r['r0'])
        elif op=='jsr':helper('callback',r['r0'],r[args])
        else:raise ValueError('IRQ instruction '+op+' '+args)
        pc=jump if jump is not None else pc+width
    raise ValueError('IRQ bound')

def expected(pending,callbacks,mutation):
    trace=[('read',STATE,0xa1000000),('read',0xa10002e8,pending)]
    cb=list(callbacks);private=[0x1234,0x5678]
    for channel in range(2):
        if not pending&(1<<channel):continue
        base=0xa1000000
        trace.append(('read',STATE,base))
        trace.extend(('write',base+o,1<<channel) for o in (0x338,0x340,0x348,0x350,0x358))
        trace.extend([('write',base+0x310,256<<channel),('deallocate',channel)])
        if mutation:cb[channel]=0x10208098 if channel==0 else 0;private[channel]=0xabcd0000+channel
        trace.append(('read',CALLBACKS+channel*4,cb[channel]))
        if cb[channel]:
            trace.extend([('read',CALLBACKS+8+channel*4,private[channel]),('callback',cb[channel],private[channel])])
            if mutation:cb[1]=0x102030e4;private[1]=0x87654321
    return trace

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d544','--stop-address=0x3d5bc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-irq/irq.disassembly.txt').read_text());cases=0
    rt=lambda p:p-0x3b940+0x10003000
    for pending,c0,c1,mutation,status in product((0,1,2,3,4,0x80000000,0xffffffff),(0,0x10004054),(0,0x10004034),(False,True),(0,1,0xffffffff)):
        a=execute(old,0x3d544,pending,(c0,c1),mutation,status,helper_addresses={0x3d500:0x10203a98})
        b=execute(new,rt(0x3d544),pending,(c0,c1),mutation,status,helper_addresses={rt(0x3d500):0x10203a98})
        assert a==b,('IRQ stock/source',pending,c0,c1,mutation,a,b)
        assert a[0]==0 and a[1]==expected(pending,(c0,c1),mutation)
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Deallocator/callback bodies modeled with clobbers and callback mutation; inline MMIO write order checked.','No hardware interrupt delivery, MMIO side effects or combined relocation qualification.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-dma-irq-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'],'cases passed')
