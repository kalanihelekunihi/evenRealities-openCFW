# SPDX-License-Identifier: MIT
"""Decoded output callback comparison for every unsigned character."""
import json,subprocess
from build_gx8002_backup_printf_output import build,ROOT
from verify_gx8002_memcpy_source import decode

def execute(code,entry,delta,value):
    pc=entry;calls=[];saved=False
    for _ in range(10):
        op,args,width=code[pc];nxt=pc+width
        if op=='push':assert args=='r15' and not saved;saved=True
        elif op=='pop':assert args=='r15' and saved;return calls
        elif op in ('bez','bnez'):
            reg,target=args.split(',');assert reg=='r0'
            if (value==0)==(op=='bez'):nxt=int(target,0)
        elif op=='bsr':assert int(args,0)+delta==0x10009990;calls.append(value)
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-printf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x42264','--stop-address=0x42274',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((out/'output.disassembly.txt').read_text())
    for value in range(256):
        assert execute(old,0x42264,0x10000000-0x38940,value)==execute(new,0x10009924,0,value)==([value] if value else [])
    report={'build':evidence,'cases':256,'limits':['Valid unsigned character inputs; _putchar modeled, full formatter and UART pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-printf-output-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
