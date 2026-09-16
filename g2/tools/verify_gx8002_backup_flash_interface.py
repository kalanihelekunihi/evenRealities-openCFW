# SPDX-License-Identifier: MIT
"""Decoded backup initializer versus source and independent ordered IO oracle."""
import json, re, subprocess
from itertools import product
from build_gx8002_backup_flash_interface import build, ROOT, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

PAIR={0xb4014,0xb4016,0xb4017,0x854012,0x856013,0x856014,0xb36014,0xba6015,0xc84015,0xc84215,0xc86015,0xc86016,0xcd7015,0xef4015}
SKIP={0x1c3812,0x1c3813,0x1c7017}
WRITES=[(0xa2000008,0),(0xa0300090,1),(0xa200002c,78),(0xa20000f0,1),(0xa2000014,4),(0xa200001c,31),(0xa2000008,1)]

def execute(code,entry,delta,device,failure,status,busy,seed):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)};r['r14']=0x20070000;initial=r.copy();mem={};trace=[];pc=entry;condition=False;frames=None;reads=0;status_reads=0
    ready=[1]*busy+[0];status_values=ready+([status]+(ready if not status&64 else []) if not failure and device==0xc22017 else [])
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            assert frames is None
            m=re.fullmatch(r'r4-r(\d+), r15',args);assert m
            names=[f'r{i}' for i in range(4,int(m[1])+1)]+['r15'];frames={k:r[k] for k in names};r['r14']-=4*len(names);frame=r['r14']
        elif op=='pop':
            assert r['r14']==frame;r.update(frames);r['r14']+=4*len(names)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert status_reads==len(status_values)
            return r['r0'],trace
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli','rotli'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='andni':r[p[0]]=r[p[1]]&(~int(p[2],0)&0xffffffff)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('andi','ori'):r[p[0]]=r[p[1]]&int(p[2],0) if op=='andi' else r[p[1]]|int(p[2],0)
        elif op in ('ld.w','ld.b','st.w','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op.startswith('st'):
                value=r[reg] if op=='st.w' else r[reg]&255
                if r['r14']<=address<frame:mem[address]=value
                else:
                    assert address in {a for a,_ in WRITES}|{0x20016d78,0x20016d7c};trace.append(('write',address,value))
            else:
                if r['r14']<=address<frame:value=mem[address]
                elif address==0xa2000028:value=int(reads<busy);reads+=1;trace.append(('busy',value))
                elif address==0x20016d6c:value=0x20040000;trace.append(('read',address,value))
                elif address==0x20040004:value=device;trace.append(('read',address,value))
                else:raise AssertionError(hex(address))
                r[reg]=value
        elif op=='bsr':
            target=int(args,0)+delta;a=[r[f'r{i}'] for i in range(4)];value=0
            if target==0x1001574c:
                assert a[0]==9 and mem[a[1]]==0;trace.append(('config',9,0))
            elif target==0x10003be8:trace.append(('gate',a[0],a[1]))
            elif target==0x10004844:trace.append(('irq',*a[:3]))
            elif target==0x10006c30:
                assert a[0]==5 and a[2]==1 and r['r14']<=a[1]<frame
                v=status_values[status_reads];status_reads+=1;mem[a[1]]=v;trace.append(('status',v))
            elif target==0x10006d34:trace.append(('status_write',mem[a[0]],a[1],a[2]))
            else:
                assert target in (0x10007c90,0x10007f80,0x100073b4,0x10007370,0x100073f0)
                trace.append(('call',target));value=failure if target==0x10007c90 else 0
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcd000000^i)&0xffffffff
            r['r0']=value
        elif op in ('cmpne','cmplt','cmphsi','cmphs'):
            a=r[p[0]];b=int(p[1],0) if op=='cmphsi' else r[p[1]]
            if op=='cmplt':a=a if a<0x80000000 else a-0x100000000;b=b if b<0x80000000 else b-0x100000000
            condition=a!=b if op=='cmpne' else a<b if op=='cmplt' else a>=b
        elif op in ('br','bt','bf','bez','bnez'):
            if op=='br' or op in ('bt','bf') and condition==(op=='bt') or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):n=int(p[-1],0)
        else:raise ValueError((hex(pc),op,args))
        pc=n
    raise AssertionError('execution bound')

def oracle(device,failure,status,busy):
    ready=[('status',1)]*busy+[('status',0)]
    trace=[('config',9,0),('gate',13,1)]+[('busy',1)]*busy+[('busy',0)]+[('write',a,v) for a,v in WRITES]+[('irq',15,0x10007138,0)]+ready+[('call',0x10007c90)]
    if failure:return 0,trace
    trace += [('call',0x10007f80),('write',0xa2000008,0),('write',0xa2000014,2),('read',0x20016d6c,0x20040000),('read',0x20040004,device)]
    if device in PAIR:trace.append(('call',0x10007370))
    elif device==0x684015:trace += [('call',0x100073b4),('call',0x10007370)]
    elif device==0xc22017:
        trace.append(('status',status))
        if not status&64:trace += [('status_write',status|64,1,1)]+ready
    elif device not in SKIP:trace.append(('call',0x100073b4))
    if device==0x204016:trace.append(('call',0x100073f0))
    trace += [('write',0x20016d78,0x10006d90),('write',0x20016d7c,0x100074ec)]
    return 0x20016d80,trace

def verify():
    candidate=build();assert candidate['fits']
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x406b8','--stop-address=0x40898',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-flash-interface/initialize.disassembly.txt').read_text())
    ids=PAIR|SKIP|{0,0xffffffff,0x80000000,0x204016,0xc22017,0x684015}
    ids |= {(v+d)&0xffffffff for v in ids for d in (-1,1)}
    cases=0
    for device,failure,status,busy,seed in product(sorted(ids),(0,1,0xffffffff),(0,1,63,64,127,255),(0,2),(0,0xffffffff)):
        expected=oracle(device,failure,status,busy)
        for code,entry,delta in ((old,0x406b8,0x0ffc76c0),(new,0x10007d78,0)):
            actual=execute(code,entry,delta,device,failure,status,busy,seed)
            assert actual==expected,(hex(device),failure,status,busy,actual,expected)
        cases+=1
    report={'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Helpers modeled; polling, ordered MMIO/state writes, selection boundaries and register preservation checked. Physical SPI and complete dependency ownership remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-flash-interface-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
