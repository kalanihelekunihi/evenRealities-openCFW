# SPDX-License-Identifier: MIT
"""Check decoded cache-disable barrier/MMIO sequences against stock and oracle."""
import json,re,subprocess
from build_gx8002_backup_dcache_control import build,ROOT,Elf32,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode


def execute(code,pc,value):
    regs={f'r{i}':0x12340000+i for i in range(32)};initial=regs.copy();trace=[]
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='sync':trace.append(('sync',))
        elif op in ('lrw','movi'):regs[p[0]]=int(p[1],0)
        elif op=='andni':regs[p[0]]=regs[p[1]] & (~int(p[2],0)&0xffffffff)
        elif op=='bclri':regs[p[0]] &= ~(1<<int(p[1],0))
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=regs[base]+int(off,0)
            if op=='ld.w':
                assert address==0xe000f000;regs[reg]=value;trace.append(('read',address,value))
            else:trace.append(('write',address,regs[reg]))
        elif op=='rts':
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return trace
        else:raise AssertionError((op,args))
        pc+=width
    raise AssertionError('instruction bound')


def verify():
    build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d6f4','--stop-address=0x3d718',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dcache-control/control.disassembly.txt').read_text())
    values=[0,0xffffffff,*[1<<i for i in range(32)],*[0xffffffff^(1<<i) for i in range(32)]]
    for value in values:
        want=[('sync',),('sync',),('read',0xe000f000,value),('write',0xe000f000,value&0xfffffffe),('write',0xe000f004,1),('sync',),('sync',)]
        assert execute(old,0x3d6f4,value)==execute(new,0x10004db4,value)==want
    report={'cases':len(values),'differences':0,'limits':['Decoded barrier and MMIO access ordering with modeled control value. Physical cache coherency and full firmware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dcache-disable-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify())
