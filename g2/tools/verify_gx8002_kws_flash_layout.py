# SPDX-License-Identifier: MIT
"""Decode loader prefix through flash probe; does not qualify full loader."""
import json,re,subprocess,itertools
from build_gx8002_kws_flash_load import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
GETTERS=(0x10208bf4,0x10208bfc,0x10208c04,0x10208c08,0x10208c10)

def execute(code,entry,sizes,full=False,flash=0x20040000,statuses=(0,0)):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;stack={};pc=entry;calls=[];initial=r.copy();saved=None;reads=0;times=0;events=[]
    for _ in range(100):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+w
        if op=='push':
            if args not in ('r4-r9, r15','r4-r8, r15'):raise ValueError('Frame')
            saved={i:r[f'r{i}'] for i in (*range(4,10),14,15)}
            r['r14']-=28 if 'r9' in args else 24
        elif op in ('movi','mov','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='pop':
            if args not in ('r4-r9, r15','r4-r8, r15'):raise ValueError('Restore')
            for i in (*range(4,10 if 'r9' in args else 9),15):r[f'r{i}']=saved[i]
            r['r14']+=28 if 'r9' in args else 24
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Preserved ABI')
            return events
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('bez','bnez','br'):
            if op=='br' or bool(r[p[0]])==(op=='bnez'):nxt=int(p[-1],0)
        elif op in ('addi','subi','addu','subu'):
            left=r[p[0]] if len(p)==2 else r[p[1]];right=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(left-right if op in ('subi','subu') else left+right)&MASK
        elif op in ('lsli','rotli'):
            v=r[p[1]];n=int(p[2],0);r[p[0]]=((v<<n)|(v>>(32-n) if op=='rotli' else 0))&MASK
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)&MASK
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))&MASK
        elif op=='bhsz':
            if r[p[0]]<0x80000000:nxt=int(p[1],0)
        elif op in ('st.w','ld.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            if base!='r14':raise ValueError('Nonstack prefix write')
            offset=int(offset,0)
            expected_sp=initial['r14']-(60 if entry==0x1023c else 56)
            if r['r14']!=expected_sp or offset not in range(0,32,4):raise ValueError('Task stack bounds')
            if op=='st.w':stack[offset]=r[reg]
            else:r[reg]=stack[offset]
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0x1023c else 0))&MASK
            if target==0x1002475c:
                if tuple(r[f'r{i}'] for i in range(4))!=(0,0,6144000,2048):raise ValueError('Probe args')
                if not full:return stack,calls
                events.append(('probe',flash));value=flash
            elif target in GETTERS:value=sizes[GETTERS.index(target)]
            elif target==0x10025930:
                value=0xfffffff0 if times==0 else 0x20;times+=1
            elif target==0x100247b8:
                events.append(('read',*(r[f'r{i}'] for i in range(4))));value=statuses[reads];reads+=1
            elif target==0x10206c24:
                events.append(('print',r['r0'],r['r1'] if r['r0']==0x1020adde else None));value=123
            elif target==0x10208c14:
                if r['r0']!=r['r14']:raise ValueError('Task pointer')
                events.append(('publish',tuple(stack.get(i,'unset') for i in range(0,32,4))));value=0
            else:raise ValueError('Unexpected prefix call')
            calls.append(target)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xab000000+i
            r['r0']=value
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def rounded_signed(value):
    value=(value+3)&MASK
    if value&0x80000000:value-=1<<32
    return ((abs(value)//4)*(-1 if value<0 else 1)*4)&MASK

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x1023c','--stop-address=0x1030a',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-kws-flash-load/loader.disassembly.txt').read_text());cases=0
    values=(0,1,3,4,9164,0x7ffffffc,0x7fffffff,0x80000000,0xfffffffc,0xffffffff)
    for sizes in itertools.product(values,repeat=3):
        parameters=(9164,120800,*sizes)
        data=(0x20000000+rounded_signed(sizes[0]))&MASK
        temporary=(data+rounded_signed(sizes[1]))&MASK
        command=(temporary+rounded_signed(sizes[2]))&MASK
        wanted=({4:0x20000000,8:data,24:temporary,20:command,28:(command+9164)&MASK},list(GETTERS)+[0x10025930])
        for code,entry in ((old,0x1023c),(new,0x10206cb0)):
            if execute(code,entry,parameters)!=wanted:raise ValueError(('Layout',sizes,entry))
        cases+=1
    full_cases=0
    for commands,weights,flash,first,second in itertools.product((0,1,3,4,9164,0xfffffffe),(0,1,120800,0xffffffff),(0,0x20040000),(0,1,0xffffffff),(0,2,0x80000000)):
        params=(commands,weights,0,13056,4)
        aligned=(commands+3)&0xfffffffc;weight_size=(weights+3)&0xfffffffc
        command=0x20000000+13056+4;weight=(command+aligned)&MASK
        events=[('probe',flash)]
        if not flash:events.append(('print',0x1020adc1,None))
        else:
            events += [('read',flash,0xf804,command,aligned),('read',flash,(0xf804+aligned)&MASK,weight,weight_size),('print',0x1020adde,48)]
            if first|second:events.append(('print',0x1020adf7,None))
        for code,entry in ((old,0x1023c),(new,0x10206cb0)):
            expected=list(events)
            if flash and not(first|second):
                unset='unset' if entry==0x1023c else 0
                expected.append(('publish',(unset,0x20000000,0x20000000,unset,unset,command,0x20003300,weight)))
            actual=execute(code,entry,params,True,flash,(first,second))
            if actual!=expected:raise ValueError(('Full loader',params,flash,first,second,entry,actual,expected))
        full_cases+=1
    return {'full_cases':full_cases,'candidate':candidate,'prefix_cases':cases,'source_admitted':False,'limits':['Full loader helper effects modeled with caller clobbers. Unset stock task words become explicit zeros; physical flash/model semantics unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-flash-layout-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['prefix_cases'])
