# SPDX-License-Identifier: MIT
"""Decode initialization stores and modeled memset calls, preserving order."""
import json,re,subprocess
from build_gx8002_buffer_initialize import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,seed,memory=None,clear_code=None,clear_entry=None,header_address=0x20027b60,helper_address=0x102099cc,stock_delta=None):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;pc=entry;events=[]
    for _ in range(130):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if args not in ('r4-r5, r15','r4, r15','r15'):raise ValueError('Frame')
            saved=(r['r4'],r['r5'],r['r15']);r['r14']-=12 if 'r5' in args else (8 if 'r4' in args else 4)
        elif op=='pop':
            if args not in ('r4-r5, r15','r4, r15','r15') or saved is None:raise ValueError('Restore')
            
            if 'r4' in args:r['r4']=saved[0]
            if 'r5' in args:r['r5']=saved[1]
            r['r15']=saved[2];r['r14']+=12 if 'r5' in args else (8 if 'r4' in args else 4)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],events
        elif op in ('movi','mov','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='movih':r[p[0]]=int(p[1],0)<<16
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff if len(p)==3 else (r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='st.w':
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(offset,0)
            if not header_address<=a<header_address+120 or a%4:raise ValueError('Header bounds')
            events.append(('write',a-header_address,r[reg]))
            if memory is not None:
                for i,b in enumerate(r[reg].to_bytes(4,'little')):memory[a+i]=b
        elif op=='bsr':
            target=(int(args,0)+(stock_delta if stock_delta is not None else (0x101f6a74 if entry==0x1034c else 0)))&0xffffffff
            if target!=helper_address:raise ValueError('Helper')
            events.append(('clear',r['r0'],r['r1'],r['r2']));destination=r['r0']
            if memory is not None:
                from compare_gx8002_memset import execute as clear
                result=clear(clear_code,clear_entry,destination,r['r1'],r['r2'],seed)
                if result['result']!=destination:raise ValueError('Nested clear return')
                touched=set()
                for address,size,value in result['trace']:
                    for i,b in enumerate(value.to_bytes(size,'little')):
                        a=address+i
                        if a not in memory or not destination<=a<destination+r['r2']:raise ValueError('Nested clear bounds')
                        memory[a]=b;touched.add(a)
                if touched!=set(range(destination,destination+r['r2'])):raise ValueError('Nested clear coverage')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xab000000+i
            r['r0']=destination
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x1034c','--stop-address=0x103e4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-buffer-initialize/buffer.disassembly.txt').read_text())
    writes=[(112,0x20032210),(116,3840),(48,48),(28,10),(32,16000),(36,4),(40,12),(108,40),(0,0x20191222),(8,2),(96,256),(80,0x20030410),(68,8480),(84,7680),(64,8512),(12,0),(88,0),(92,0),(16,0),(100,0),(104,0),(44,0),(20,1),(24,0),(72,0),(76,0),(52,0),(56,0x20027be0),(60,3),(4,1)]
    wanted=[('clear',0x20027b60,0,120),('clear',0x20027be0,0,25536),('clear',0x20030000,0,1040)]+[('write',o,v) for o,v in writes]
    for seed in (0,1,0xffffffff,0xa5a5a5a5,0x80000000):
        for code,entry in ((old,0x1034c),(new,0x10206dc0)):
            if execute(code,entry,seed)!=(0,wanted):raise ValueError('Initialization effects')
    from build_gx8002_memset_candidate import build as build_clear
    clear_candidate=build_clear()
    old_clear=decode(subprocess.check_output([pre,'-D','--start-address=0x12f58','--stop-address=0x12ff8',str(wrapper)],text=True))
    new_clear=decode((ROOT/'build/gx8002-board/memset-candidate.disassembly.txt').read_text())
    nested=0
    # Include every gap and neighboring byte, not just the intended writes.
    for seed in (0,1,0xffffffff,0xa5a5a5a5,0x80000000):
        initial={a:((a*37+seed)%255)+1 for a in range(0x20027b50,0x20030420)}
        expected=initial.copy()
        for destination,count in ((0x20027b60,120),(0x20027be0,25536),(0x20030000,1040)):
            for a in range(destination,destination+count):expected[a]=0
        for offset,value in writes:
            for i,b in enumerate(value.to_bytes(4,'little')):expected[0x20027b60+offset+i]=b
        for code,entry in ((old,0x1034c),(new,0x10206dc0)):
            for helper,helper_entry in ((old_clear,0x12f58),(new_clear,0x102099cc)):
                memory=initial.copy()
                if execute(code,entry,seed,memory,helper,helper_entry)!=(0,wanted) or memory!=expected:raise ValueError('Nested memory effects')
                nested+=1
    return {'candidate':candidate,'decoded_cases':5,'nested_clear_cases':nested,'clear_candidate':clear_candidate,'source_admitted':False,'limits':['Decoded ordered stores and nested stock/source memset traces, including surrounding memory; no physical startup or asynchronous access qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-buffer-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
