# SPDX-License-Identifier: MIT
"""Decode output-configuration state at helper and by-value driver boundaries."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_output import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff;BASE=0x101f6a74;BOARD=0x20026d00;STACK=0x20070000


def execute(code,entry,source,channel,buffer,size,frames,initial_memory,seed=0,mutation=None,copy_code=None,copy_entry=0):
    memory=initial_memory.copy();r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=source,r1=channel,r14=STACK);initial=r.copy();saved=None;pc=entry;condition=False;events=[]
    def read(address,n):
        if n>1 and address%4:raise ValueError('Read alignment')
        if any(address+i not in memory for i in range(n)):raise ValueError('Unmapped read '+hex(address))
        return int.from_bytes(bytes(memory[address+i] for i in range(n)),'little')
    def write(address,n,value):
        if address%4:raise ValueError('Write alignment')
        if not (BOARD<=address and address+n<=BOARD+240) and not (r['r14']<=address and address+n<=r['r14']+12):raise ValueError('Write bounds')
        for i,b in enumerate(value.to_bytes(n,'little')):memory[address+i]=b
    def snapshot():return bytes(memory[a] for a in range(BOARD,BOARD+240))
    for _ in range(250):
        op,args,w=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+w
        if op=='push':
            if args not in ('r4-r8, r15','r4-r9, r15') or saved is not None:raise ValueError('Frame')
            last=8 if 'r8' in args else 9;saved={f'r{i}':r[f'r{i}'] for i in (*range(4,last+1),15)};r['r14']-=len(saved)*4
        elif op=='pop':
            if saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=len(saved)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return events,snapshot()
        elif op in ('mov','movi'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addi','subi','lsli','lsri','andi','andni'):
            a,b=(r[p[0]],int(p[1],0)) if len(p)==2 else (r[p[1]],int(p[2],0))
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else a>>b if op=='lsri' else a&b if op=='andi' else a&~b)&MASK
        elif op in ('addu','and'):
            a,b=(r[p[0]],r[p[1]]) if len(p)==2 else (r[p[1]],r[p[2]])
            r[p[0]]=(a+b if op=='addu' else a&b)&MASK
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op in ('bez','bnez','bhsz'):
            take=(r[p[0]]==0) if op=='bez' else (r[p[0]]!=0) if op=='bnez' else (r[p[0]]<0x80000000)
            if take:nxt=int(p[1],0)
        elif op in ('ld.b','ld.w','st.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(offset,0))&MASK
            if op=='st.w':write(address,4,r[reg])
            else:r[reg]=read(address,1 if op=='ld.b' else 4)
        elif op=='bsr':
            target=(int(args,0)+(BASE if entry==0x105fc else 0))&MASK
            result=0
            if target==0x10025738:
                destination,start,n=r['r0'],r['r1'],r['r2']
                if n!=12 or destination!=r['r14'] or start not in (BOARD+136,BOARD+160,BOARD+208):raise ValueError('Struct copy')
                data=[read(start+i,4) for i in range(0,12,4)]
                for i,v in enumerate(data):write(destination+i*4,4,v)
                if copy_code is not None:
                    from verify_gx8002_memcpy_source import execute as copy_execute
                    expected_memory=memory.copy()
                    for i in range(12):memory[destination+i]=0xa5
                    returned,_=copy_execute(copy_code,memory,destination,start,12,start=copy_entry)
                    if returned!=destination or memory!=expected_memory:raise ValueError('Nested struct copy')
                result=destination
            else:
                offset=target-BASE
                if offset in (0x105d8,0x105b0):
                    if r['r0']!=channel:raise ValueError('Selector argument')
                    events.append((offset,(channel,),snapshot()));result=buffer if offset==0x105d8 else size
                elif offset in (0xc590,0x104e8):events.append((offset,(),snapshot()));result=BOARD if offset==0xc590 else frames
                else:
                    counts={0xdab8:(2,0),0xd6b8:(4,2),0xd534:(4,3),0xd60c:(4,1),0xd7b4:(4,3),0xd8cc:(1,0)}
                    if offset not in counts:raise ValueError('Driver target '+hex(target))
                    regs,stack=counts[offset];arguments=tuple(r[f'r{i}'] for i in range(regs))+tuple(read(r['r14']+i*4,4) for i in range(stack))
                    events.append((offset,arguments,snapshot()))
            if mutation and target!=0x10025738:
                state=bytearray(snapshot());mutation(target-BASE,state)
                for i,b in enumerate(state):memory[BOARD+i]=b
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xab000000+i+seed)&MASK
            r['r0']=result
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Execution bound')


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x105fc','--stop-address=0x107c0',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-input-output/index.disassembly.txt').read_text());cases=0
    for source,channel,track,size,frames in product(range(16),(0,1,2,4,8,16,0xffffffff),(0,1),(0,127,128,255,256,7680,0xffffffff),(0,63,64,160,0x80000000,0xffffffff)):
        memory={BOARD+i:(i*37+11)&255 for i in range(240)}
        for offset in (5,33):memory[BOARD+offset]=(memory[BOARD+offset]&~8)|(track<<3)
        expected=execute(old,0x105fc,source,channel,0x20030417,size,frames,memory,source)
        actual=execute(new,0x10207070,source,channel,0x20030417,size,frames,memory,source)
        from gx8002_audio_input_output_oracle import expected as oracle
        wanted=oracle(source,channel,0x20030417,size,frames,memory)
        if actual!=expected or expected!=wanted:raise ValueError(('Driver-boundary mismatch',source,channel,track,size,frames))
        cases+=1
    mutation_cases=0
    for source,channel,changed in product(range(16),(1,2,4,8),(0xc590,0x104e8,0xdab8,0xd6b8,0xd534)):
        def mutation(target,state):
            if target==changed:
                for i in range(len(state)):state[i]^=(i*17+source+1)&255
        memory={BOARD+i:(i*37+11)&255 for i in range(240)}
        wanted=oracle(source,channel,0x20030417,7680,160,memory,mutation)
        for code,entry in ((old,0x105fc),(new,0x10207070)):
            if execute(code,entry,source,channel,0x20030417,7680,160,memory,source,mutation)!=wanted:raise ValueError(('Helper mutation',source,channel,changed))
        mutation_cases+=1
    from verify_gx8002_memcpy_source import verify as copy_verify
    copy_evidence=copy_verify()
    copy_old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x1774c','--stop-address=0x177ca',str(ROOT/'build/gx8002-memcpy-source/stock-analysis.elf')],text=True))
    copy_new=decode(subprocess.check_output([pre+'objdump','-d',str(ROOT/'build/gx8002-memcpy-source/copy.o')],text=True))
    nested_cases=0
    for source,channel,track in product(range(16),(1,2,4,8),(0,1)):
        memory={BOARD+i:(i*37+11)&255 for i in range(240)}
        for offset in (5,33):memory[BOARD+offset]=(memory[BOARD+offset]&~8)|(track<<3)
        wanted=oracle(source,channel,0x20030417,7680,160,memory)
        for code,entry in ((old,0x105fc),(new,0x10207070)):
            for helper,helper_entry in ((copy_old,0x1774c),(copy_new,0)):
                if execute(code,entry,source,channel,0x20030417,7680,160,memory,source,copy_code=helper,copy_entry=helper_entry)!=wanted:raise ValueError('Nested output configuration')
                nested_cases+=1
    return {'candidate':candidate,'nested_copy_cases':nested_cases,'copy_evidence':copy_evidence,'helper_mutation_cases':mutation_cases,'decoded_cases':cases,'source_admitted':False,'limits':['Stock/source driver-call arguments, board snapshots and final state compared; helpers and memcpy modeled. Independent SDK-field oracle also checked. Helper boundary mutation checked. Decoded nested stock/source memcpy checked; source admission pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-output-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
