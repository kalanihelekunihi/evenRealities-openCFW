# SPDX-License-Identifier: MIT
"""Decoded backup status priority and conditional MMIO read checks."""
import json,subprocess
from itertools import product
from build_gx8002_backup_status import build,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_backup_preserve_memory import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3c8f8','--stop-address=0x3c93a',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-backup-status/status.disassembly.txt').read_text());cases=0
    for low,high,fallback in product(range(256),(0,0xffffff00),(0,1,2,0xffffffff)):
        flags=low|high;values={0xa0000034:flags,0xa001002c:fallback}
        result=next((value for mask,value in ((1,2),(4,3),(8,5),(2,4)) if flags&mask),fallback&1)
        trace=[(0xa0000034,flags)]
        if not flags&15:trace.append((0xa001002c,fallback))
        assert execute(old,0x3c8f8,values)==execute(new,0x10003fb8,values)==(result,trace)
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Priority and read sequence verified with modeled registers. Physical reset-status meaning and placement remain separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-status-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],'cases passed')
