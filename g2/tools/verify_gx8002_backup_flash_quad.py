# SPDX-License-Identifier: MIT
"""Backup quad configuration and polling against ordered call oracles."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_flash_quad import build,ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,delta,values,result):
    r={f'r{i}':0xab000000+i for i in range(32)};r.update(r14=0x20070000);initial=r.copy();pc=entry;mem={};trace=[];condition=False;si=0
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            assert args=='r15';names=['r15'];saved={k:r[k] for k in names};r['r14']-=4;frame=r['r14']
        elif op=='pop':
            assert r['r14']==frame;r.update(saved);r['r14']+=4*len(names)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],trace
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]])&0xffffffff
        elif op in ('andi','ori'):r[p[0]]=r[p[1]]&int(p[2],0) if op=='andi' else r[p[1]]|int(p[2],0)
        elif op in ('ld.b','st.b'):
            dst,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();
            address=r[base]+int(off,0)
            assert r['r14']<=address<frame
            if op=='ld.b':r[dst]=mem[address]
            else:mem[address]=r[dst]&255
        elif op in ('cmphsi','cmpnei'):condition=r[p[0]]>=int(p[1],0) if op=='cmphsi' else r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf','bez','bnez'):
            if op=='br' or op in ('bt','bf') and condition==(op=='bt') or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):n=int(p[-1],0)
        elif op=='bsr':
            target=int(args,0)+delta;a=[r[f'r{i}'] for i in range(3)]
            if target==0x10006c30:
                assert a[2]==1 and r['r14']<=a[1]<frame
                command,value=values[si];si+=1;assert a[0]==command
                mem[a[1]]=value;trace.append(('read',command,value))
            elif target==0x10006d34:
                data=tuple(mem[a[0]+i] for i in range(a[1]));trace.append(('status_write',data,a[2]))
            else:
                assert target==0x10007350;trace.append(('wait',))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=result
        else:raise ValueError((hex(pc),op,args))
        pc=n
    raise AssertionError('execution bound')

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3fc90','--stop-address=0x3fd6c',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-flash-quad/transport-linked.disassembly.txt').read_text());cases=0
    for offset,command,mask,selector in ((0x3fcb0,53,2,1),(0x3fcf4,53,2,2),(0x3fd30,21,16,3)):
        for value,first,result in product(range(256),(0,1,255),(0,0xffffffff)):
            values=([(5,first)] if selector==1 else [])+[(command,value)]
            trace=[('read',c,v) for c,v in values]
            if not value&mask:trace += [('status_write',((first,value|mask) if selector==1 else (value|mask,)),selector),('wait',)]
            for code,entry,delta in ((old,offset,0x0ffc76c0),(new,offset+0x0ffc76c0,0)):
                assert execute(code,entry,delta,values,result)==(0,trace)
            cases+=1
    for last,busy,result in product(range(0,256,2),(0,1,3),(0,1,0xffffffff)):
        values=[(5,255)]*busy+[(5,last)];want=(result,[('read',c,v) for c,v in values])
        assert execute(old,0x3fc90,0x0ffc76c0,values,result)==execute(new,0x10007350,0,values,result)==want
        cases+=1
    report={'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Transport, status-write and wait calls modeled at configuration boundaries. Wait helper separately checked. Full nested execution and physical flash remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-flash-quad-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
