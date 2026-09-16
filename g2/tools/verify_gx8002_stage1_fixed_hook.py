# SPDX-License-Identifier: MIT
"""Compare the full fixed-argument stage-one hook against stock."""
import json,subprocess
from itertools import product
from build_gx8002_stage1_initialize import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,helper,arg0,arg1,result,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};r.update(r0=arg0,r1=arg1);initial=dict(r);saved=None;pc=entry;trace=[]
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']=(r['r14']-4)&0xffffffff
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']=(r['r14']+4)&0xffffffff
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='bsr':
            assert int(args,0)==helper;trace.append([r['r0'],r['r1']])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xdead0000^i)&0xffffffff
            r['r0']=result
        else:raise AssertionError((hex(pc),op,args))
        pc+=width
    raise AssertionError('hook bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x39c34','--stop-address=0x39c44',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-stage1-initialize/initialize.disassembly.txt').read_text());cases=0
    for a,b,result,seed in product((0,1,115200,0xffffffff),(0,1,0x87654321,0xffffffff),(0,1,0xffffffff),(0,0x12345678)):
        assert execute(old,0x39c34,0x39bb4,a,b,result,seed)==execute(new,0x100012e0,0x10001260,a,b,result,seed)==[[115200,0]]
        cases+=1
    return {'cases':cases,'cluster_elf_sha256':evidence['elf_sha256'],'limits':['Complete hook instruction execution and fixed arguments verified. Underlying helper behavior is modeled; no hardware serial configuration or firmware integration claim.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stage1-fixed-hook-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'fixed-hook cases passed')
