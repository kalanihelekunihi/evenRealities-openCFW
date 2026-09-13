# SPDX-License-Identifier: MIT
"""Decoded allocation equivalence and explicit rejection repair verification."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_alloc_playback import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
HANDLE=0x20026b94
SETTINGS=0x20040000
BASE=0xa0b00000

def execute(code,entry,route,initial,settings,seed,stop_bad=False):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=route,r14=0x20070000);saved=r.copy();stack={};trace=[];state=bytearray(initial);memory={BASE+i:seed for i in (0,4,12)};pc=entry;condition=False
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r6, r15':raise ValueError('Allocation frame')
            r['r14']-=16
            for i,name in enumerate(('r4','r5','r6','r15')):stack[r['r14']+4*i]=r[name]
        elif op=='pop':
            if args!='r4-r6, r15':raise ValueError('Allocation restore')
            for i,name in enumerate(('r4','r5','r6','r15')):r[name]=stack[r['r14']+4*i]
            r['r14']+=16
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Allocation ABI')
            return r['r0'],trace,bytes(state),memory
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='addi':r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+int(p[-1],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('bseti','bclri'):
            value=r[p[1]] if len(p)==3 else r[p[0]];mask=1<<int(p[-1],0);r[p[0]]=value|mask if op=='bseti' else value&~mask
        elif op in ('andi','andni'):r[p[0]]=r[p[1]]&(int(p[2],0) if op=='andi' else ~int(p[2],0))
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('ld.w','st.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();a=r[base]+int(off,0);size=4 if op.endswith('w') else 1
            if a in memory:
                if size!=4:raise ValueError('Allocation MMIO width')
                if op.startswith('ld'):r[reg]=memory[a];trace.append(('read',a,r[reg]))
                else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
            elif HANDLE<=a<=HANDLE+64-size:
                offset=a-HANDLE
                if op.startswith('ld'):r[reg]=int.from_bytes(state[offset:offset+size],'little');trace.append(('state_read',offset,size,r[reg]))
                else:
                    value=r[reg]&((1<<(size*8))-1);state[offset:offset+size]=value.to_bytes(size,'little');trace.append(('state_write',offset,size,value))
            elif a in (SETTINGS,SETTINGS+4) and op=='ld.w':r[reg]=settings[(a-SETTINGS)//4];trace.append(('settings_read',a,r[reg]))
            elif stop_bad and op=='st.w' and a==20:return ('stock_low_write',a,r[reg],trace)
            else:raise ValueError(('Allocation address',hex(a),op))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe7e0 else 0))&0xffffffff;result=None
            if target==0x102099cc:
                if (r['r0'],r['r1'],r['r2'])!=(HANDLE+16,0,36):raise ValueError('Allocation memset arguments')
                trace.append(('memset',HANDLE+16,0,36));state[16:52]=bytes(36);result=HANDLE+16
            elif target==0x10205374:
                if r['r0']!=0:raise ValueError('Allocation selector argument')
                trace.append(('select',0));result=SETTINGS
            elif target==0x1002553c:
                if (r['r0'],r['r1'],r['r2'])!=(13,0x102050cc,HANDLE):raise ValueError('Allocation IRQ arguments')
                trace.append(('request_irq',13,0x102050cc,HANDLE))
            else:raise ValueError('Allocation call target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            if result is not None:r['r0']=result
        else:raise ValueError('Allocation opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Allocation bound')

def oracle(route,initial,settings,seed):
    state=bytearray(initial);memory={BASE+i:seed for i in (0,4,12)};trace=[('state_read',4,1,state[4])]
    rejected=bool(state[4])
    if not rejected:
        reserved=int.from_bytes(state[8:12],'little');trace.append(('state_read',8,4,reserved));rejected=bool(reserved)
    if not rejected:trace.append(('state_read',12,1,state[12]));rejected=state[12]!=route
    if rejected:return 0,trace,bytes(state),memory
    trace.extend((('memset',HANDLE+16,0,36),('state_write',4,1,1),('state_write',20,4,0),('state_write',24,1,route),('select',0),('state_write',48,4,SETTINGS)))
    state[16:52]=bytes(36);state[4]=1;state[24]=route;state[48:52]=SETTINGS.to_bytes(4,'little')
    for address,mask,value,index in ((BASE+12,1<<21,1<<21,None),(BASE,1<<31,0,None),(BASE,2,(settings[0]&1)<<1,0),(BASE,1,settings[1]&1,1),(BASE+4,256,0,None)):
        trace.append(('read',address,memory[address]))
        if index is not None:trace.append(('settings_read',SETTINGS+4*index,settings[index]))
        memory[address]=(memory[address]&~mask)|value;trace.append(('write',address,memory[address]))
    trace.append(('request_irq',13,0x102050cc,HANDLE));return HANDLE,trace,bytes(state),memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe7e0','--stop-address=0xe86c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-alloc-playback/bits.disassembly.txt').read_text());cases=0;repairs=0
    for route,first,second,seed in product(range(256),(0,1,2,255,0xffffffff),(0,1,2,255,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        initial=bytearray([0xa5]*64);initial[4]=0;initial[8:12]=bytes(4);initial[12]=route;settings=(first,second);wanted=oracle(route,initial,settings,seed)
        for code,entry in ((old,0xe7e0),(new,0x10205254)):
            if execute(code,entry,route,initial,settings,seed)!=wanted:raise ValueError(('Allocation effects',entry,route,settings,seed))
        cases+=1
    for route,active,reserved,configured in product((0,1,255,256,0xffffffff),(0,1,255),(0,1,0xffffffff),(0,1,255)):
        initial=bytearray([0xa5]*64);initial[4]=active;initial[8:12]=reserved.to_bytes(4,'little');initial[12]=configured
        if not active and not reserved and route==configured:continue
        wanted=oracle(route,initial,(0,0),0)
        if execute(new,0x10205254,route,initial,(0,0),0)!=wanted:raise ValueError('Allocation repair effects')
        stock=execute(old,0xe7e0,route,initial,(0,0),0,True)
        if stock!=('stock_low_write',20,0,wanted[1]):raise ValueError('Stock rejection bug not reproduced')
        repairs+=1
    return {'candidate':candidate,'decoded_success_cases':cases,'intentional_repair_cases':repairs,'source_admitted':False,'hardware_qualified':False,'limits':['Memset, settings selector and IRQ registration modeled with caller clobbers. Valid fixed handle/settings RAM; asynchronous mutation and physical hardware unqualified. Stock invalid paths checked only through first low-memory write; source rejects without writes/calls.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-alloc-playback-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_success_cases'],r['intentional_repair_cases'])
