# SPDX-License-Identifier: MIT
"""Status write argument checks, polling and ordered transport calls."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_flash_status_write import build,ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,delta,pointer,length,reg,statuses):
    r={f'r{i}':0xab000000+i for i in range(32)};r.update(r0=pointer,r1=length,r2=reg,r14=0x20070000);initial=r.copy();pc=entry;mem={};trace=[];condition=False;si=0
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            m=re.fullmatch(r'r4-r(\d+), r15',args);assert m
            names=[f'r{i}' for i in range(4,int(m[1])+1)]+['r15'];saved={k:r[k] for k in names};r['r14']-=4*len(names);frame=r['r14']
        elif op=='pop':
            assert r['r14']==frame;r.update(saved);r['r14']+=4*len(names)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],trace
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ld.b':
            dst,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();r[dst]=mem[r[base]+int(off,0)]
        elif op in ('cmphsi','cmpnei'):condition=r[p[0]]>=int(p[1],0) if op=='cmphsi' else r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf','bez','bnez'):
            if op=='br' or op in ('bt','bf') and condition==(op=='bt') or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):n=int(p[-1],0)
        elif op=='bsr':
            target=int(args,0)+delta;a=[r[f'r{i}'] for i in range(3)]
            if target==0x10006c30:
                assert a[0]==5 and a[2]==1 and r['r14']<=a[1]<frame
                value=statuses[si];si+=1;mem[a[1]]=value;trace.append(('read_status',value))
            else:
                assert target==0x10006cb0;trace.append(('write',*a))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=0xffffffff # ignored transport returns
        else:raise ValueError((hex(pc),op,args))
        pc=n
    raise AssertionError('execution bound')

def verify():
    candidate=build();assert candidate['fits']
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3f674','--stop-address=0x3f6d0',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-flash-status-write/initialize.disassembly.txt').read_text());cases=0
    for pointer,length,reg,statuses in product((0,0x20040000,0xffffffff),(0,1,2,3,0xffffffff),(0,1,2,3,4,0xffffffff),((0,),(254,),(1,0),(255,3,128))):
        if length>2 or reg not in (1,2,3):want=(0xffffffff,[])
        else:want=(0,[('read_status',s) for s in statuses]+[('write',6,0,0),('write',{1:1,2:49,3:17}[reg],pointer,length)])
        for code,entry,delta in ((old,0x3f674,0x0ffc76c0),(new,0x10006d34,0)):
            assert execute(code,entry,delta,pointer,length,reg,statuses)==want
        cases+=1
    report={'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Transport calls modeled including ignored errors; caller buffer passed through without dereferencing. No physical flash or nested transport execution qualification.']}
    (ROOT/'docs/research/gx8002-backup-flash-status-write-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
