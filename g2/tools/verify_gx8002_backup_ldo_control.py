# SPDX-License-Identifier: MIT
"""Compare decoded LDO MMIO behavior, including invalid controls."""
import json
import re
import subprocess
from build_gx8002_backup_ldo_control import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,control,value):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=control;initial=dict(r);pc=entry;trace=[];condition=False
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('andi','ori'):r[p[0]]=(r[p[1]]&int(p[2],0)) if op=='andi' else r[p[1]]|int(p[2],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,offset=m.groups();address=r[base]+int(offset,0);assert address==0xa0005058
            if op=='ld.w':r[reg]=value;trace.append(['read',address,value])
            else:trace.append(['write',address,r[reg]])
        elif op in ('br','bt','bf','bez','bnez'):
            take=op=='br' or op=='bt' and condition or op=='bf' and not condition
            if op in ('bez','bnez'):take=(r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('LDO bound')


def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-ldo-control';tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x40a34','--stop-address=0x40a74',str(wrapper)],text=True))
    new=decode((out/'ldo.disassembly.txt').read_text());cases=0
    for control in (0,1,2,3,255,256,0x80000000,0xffffffff):
        for value in [low|high for high in (0,0xffffff00,0x12345600) for low in range(256)]:
            a=execute(old,0x40a34,control,value);b=execute(new,0x100080f4,control,value);assert a==b
            expected=[['read',0xa0005058,value]]
            if control<3:
                byte=value&255
                target=(byte&~4) if control==0 else (byte&~6)|4 if control==1 else byte|6
                expected.append(['write',0xa0005058,target])
            assert b==(0 if control<3 else 0xffffffff,expected)
            cases+=1
    return {'cases':cases,'build':evidence,'limits':['Decoded integer/MMIO comparison with independent bitmask and invalid-input oracle. Hardware voltage/timing effects and incoming-reference closure remain unqualified; not integrated.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-ldo-control-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'LDO cases passed')
