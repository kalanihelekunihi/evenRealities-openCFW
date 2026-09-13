# SPDX-License-Identifier: MIT
"""Decoded OTP configuration policy and callback forwarding; finite effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_flash_otp_configuration import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
MASK=0xffffffff

def execute(code,entry,hz,device,status,content,seed,mutation=None,probe_target=0x10007d78,read_hook=None,probe_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=0x20040000,r14=0x20050000);initial=r.copy();saved=None;pc=entry;memory={};events=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            regs=('r4','r5','r15') if entry==0x4e014 else ('r4','r15')
            assert args==('r4-r5, r15' if entry==0x4e014 else 'r4, r15') and saved is None
            saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            assert saved is not None and r['r14']==initial['r14']-4*len(saved)
            r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return r['r0'],word(memory,0x20040000),events
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsri','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a>>b if op=='lsri' else a<<b)&MASK
        elif op in ('st.w','st.b','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();a=(r[base]+int(off,0))&MASK
            if op=='ld.w':assert a==0x20016d80;r[reg]=probe_target
            else:
                assert a==0x20040000 or r['r14']<=a<r['r14']+5
                if op=='st.w':word(memory,a,r[reg])
                else:memory[a]=r[reg]&255
                if a==0x20040000:events.append(('configuration',r[reg]))
        elif op in ('bez','bnez','bhsz','blz','br'):
            if op=='br' or (op=='bez' and r[p[0]]==0) or (op=='bnez' and r[p[0]]!=0) or (op=='blz' and r[p[0]]>=0x80000000) or (op=='bhsz' and r[p[0]]<0x80000000):nxt=int(p[-1],0)
        elif op in ('bsr','jsr'):
            target=r[args] if op=='jsr' else int(args,0)+((0x10003000-0x3b940) if entry==0x4e014 else 0)
            a,b,c,d=[r[f'r{i}'] for i in range(4)];value=0
            if target==0x10003cf0:assert a==13;events.append(('frequency',13));value=hz
            elif target==probe_target:assert (a,b,c,d)==(0,0,hz>>1,2048);events.append(('probe',a,b,c,d));value=device if probe_hook is None else probe_hook(target,(a,b,c,d))
            elif target==0x1000802c:
                assert (a,b,d)==(device,0,5) and c==r['r14'] and bytes(memory[c+i] for i in range(5))==bytes(5)
                assert len(content)<=5
                if read_hook is None:
                    for i,v in enumerate(content):memory[c+i]=v
                    value=status
                else:value=read_hook((a,b,c,d),memory)
                events.append(('read',device,0,5))
            elif target==0x10009934:assert a==0x10012a8c;events.append(('error',))
            elif target==0x100099bc:assert a==0x10012aa4;value=5;events.append(('strlen',))
            elif target==0x10009998:
                assert (a,b,c)==(r['r14'],0x10012aa4,5)
                value=0 if bytes(memory[a+i] for i in range(5))==b'8003A' else 1
                events.append(('compare',))
            else:raise ValueError(('helper',hex(target)))
            if mutation and events[-1][0]==mutation[0]:
                word(memory,0x20040000,mutation[1]);events.append(('helper_configuration',mutation[0],mutation[1]))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbaad0000+i)&MASK
            r['r0']=value
        else:raise ValueError(('instruction',op,args))
        pc=nxt
    raise ValueError('bound')

def verify():
    candidate=build();assert candidate['compiled_bytes']==120;path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e014','--stop-address=0x4e08c',str(path)],text=True));new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-backup-flash-otp-configuration/configuration.elf')],text=True));cases=0
    for hz,device,status,content,mutation,probe_target in product(
        (0,1,24576000,MASK),(0,0x20016d80),(0,5,0x80000000,MASK),
        (b'8003A',b'8003B',b'\0'*5,b'800\0A',b'\xff'*5,b'',b'8',b'80',b'800',b'8003'),
        (None,('frequency',0x12345678),('probe',MASK),('read',0),('compare',0x87654321),('strlen',0x13579bdf),('error',0x42)),
        (0x10007d78,0x10040000)):
        events=[('configuration',0x8002)];result=MASK;configuration=0x8002
        def event(*parts):
            nonlocal configuration
            events.append(parts)
            if mutation and parts[0]==mutation[0]:
                configuration=mutation[1];events.append(('helper_configuration',*mutation))
        event('frequency',13);event('probe',0,0,hz>>1,2048)
        if device:
            event('read',device,0,5)
            if status&0x80000000:event('error')
            else:
                result=0;event('strlen');event('compare')
                if content.ljust(5,b'\0')==b'8003A':configuration=0x8003a;events.append(('configuration',configuration))
        wanted=(result,configuration,events)
        assert execute(old,0x4e014,hz,device,status,content,hz,mutation,probe_target)==execute(new,0x100156d4,hz,device,status,content,hz,mutation,probe_target)==wanted
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded policy, stack initialization, argument forwarding and ABI checked; flash/clock/string helpers modeled. Explicit strlen call preserved and modeled with the authenticated five-byte signature. Partial writes and scripted configuration mutations at helper boundaries checked; actual nested helpers and hardware remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-flash-otp-configuration-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
