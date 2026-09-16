# SPDX-License-Identifier: MIT
"""Backup SPI cleanup and interrupt decoded access/ABI qualification."""
import json,subprocess
from itertools import product
from build_gx8002_backup_dw_spi_cleanup import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,build
from build_gx8002_backup_dw_spi_irq import build as build_irq
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_protection_query import execute

def verify():
    evidence=[build(),build_irq()];assert all(r['fits'] for r in evidence)
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x40bbc','--stop-address=0x40be8',str(path)],text=True));old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('br','bt','bf','bez','bnez'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    counts={}
    for name,entry in [('cleanup',0x1000827c),('irq',0x10008288)]:
        new=decode((ROOT/f'build/gx8002-backup-dw-spi-{name}/dw-spi-{name}-candidate.disassembly.txt').read_text());count=0
        for status,regs,value in product((*range(256),*(0x80000000+i for i in range(256))),(0xa3000000,0xa2001000),(0,0xffffffff)):
            memory={};device=0x20040000;master=0x20041000;context=0x20042000
            for address,v in ((device,master),(master+24,context),(context+4,regs),(regs+8,value),(regs+48,status),(0x38,value),(0x3c,value^0xffffffff)):word(memory,address,v)
            if name=='cleanup':
                args=[device];expected=[('read','ld.w',device,master),('read','ld.w',master+24,context),('read','ld.w',context+4,regs)]
                expected += [('write_byte',regs+8+i,0) for i in range(4)]
                after_want=memory.copy();word(after_want,regs+8,0)
            else:
                args=[value,context];expected=[('read','ld.w',context+4,regs),('read','ld.w',regs+48,status)]
                if status&2:expected.append(('read','ld.w',0x38,value))
                if status&8:expected.append(('read','ld.w',0x3c,value^0xffffffff))
                after_want=memory
            for code in (old,new):
                def helper(*args):raise AssertionError('unexpected call')
                outcome,after,events=execute(code,entry,args,memory,helper)
                assert outcome[0]=='return' and (name=='cleanup' or outcome[1]==0)
                assert after==after_want and events==expected
            count+=1
        counts[name]=count
    report={'build':evidence,'cases':counts,'source_admitted':False,'limits':['Exact ordered reads include absolute addresses 0x38/0x3c; their hardware meaning remains unqualified.','Cleanup has void ABI; arbitrary return register is not constrained. No hardware execution.']}
    (ROOT/'docs/research/gx8002-backup-dw-spi-leaves-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
