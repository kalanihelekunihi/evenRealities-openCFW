# SPDX-License-Identifier: MIT
"""Registration replacement, exhaustion and input/table alias qualification."""
import json,subprocess
from itertools import product
from build_gx8002_backup_uart_registration import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_uart_registration import execute,word
from verify_gx8002_memcpy_source import decode
TABLE=0x2002cf30

def oracle(memory,ptr):
    m=memory.copy()
    for i in range(16):
        row=TABLE+i*28
        if word(m,ptr+4)==word(m,row+4):
            word(m,row+4,0);m[row]=255
            for off in (8,12,16,24,20):word(m,row+off,0)
    for i in range(16):
        row=TABLE+i*28
        if word(m,row+4)==0:
            word(m,row+4,word(m,ptr+4));m[row]=m[ptr]
            for off in (8,12,16,24,20):word(m,row+off,word(m,ptr+off))
            return ('return',0),m
    return ('return',0xffffffff),m

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x43d70','--stop-address=0x43e08',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-uart-registration/callback.disassembly.txt').read_text());cases=0
    for alias,identifier,empty,duplicates in product(range(-1,16),(0,1,7,0xffffffff),range(-1,16),(False,True)):
        m={TABLE-16+i:(i*37)&255 for i in range(480)};ptr=0x20040000 if alias<0 else TABLE+28*alias
        m.update({0x20040000+i:(i*19)&255 for i in range(28)})
        for i in range(16):word(m,TABLE+28*i+4,0 if i==empty else identifier if duplicates and i%3==0 else i+100)
        word(m,ptr+4,identifier);expected=oracle(m,ptr)
        for code,entry in ((old,0x43d70),(new,0x1000b430)):
            a=execute(code,entry,ptr,0,m,lambda *args: (_ for _ in ()).throw(ValueError('Unexpected helper')))
            if (a[0],a[1])!=expected:raise ValueError(('Registration',alias,identifier,empty,duplicates,hex(entry)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Independent ordered-field oracle, full table/input/guard memory and ABI; all16 table aliases, zero/full identifiers, duplicate removal and empty/exhausted table. Arbitrary partial overlap and physical concurrency unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-uart-registration-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'])
