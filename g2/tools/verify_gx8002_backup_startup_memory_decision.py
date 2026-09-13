# SPDX-License-Identifier: MIT
"""Compose decoded preservation predicate with its startup clear-branch decision."""
import json,subprocess
from itertools import product
from build_gx8002_backup_preserve_memory import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_backup_preserve_memory import execute,verify as predicate
from verify_gx8002_memcpy_source import decode

def verify():
    proof=predicate();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3bad8','--stop-address=0x3bae4',str(p)],text=True))
    assert code[0x3bad8]==('bsr','0x3c93c',4)
    assert code[0x3badc]==('bez','r0, 0x3bb1e',4)
    call=decode(subprocess.check_output([pre,'-D','--start-address=0x3bb1e','--stop-address=0x3bb24',str(p)],text=True))
    assert call[0x3bb1e]==('bsr','0x3ba68',4) and call[0x3bb22]==('br','0x3bae0',2)
    source=decode((ROOT/'build/gx8002-backup-preserve-memory/predicate.disassembly.txt').read_text());cases=0;clear=0
    for flags,fallback,preserve in product(range(16),(0,1,0xffffffff),(0,1,2,0xffffffff)):
        values={0xa0000034:flags,0xa001002c:fallback,0xa0010058:preserve,0xa001005c:0x98765432}
        result,reads=execute(source,0x10003ffc,values)
        target=int(code[0x3badc][1].split(',')[-1],0) if result==0 else 0x3bae0
        should_clear=flags==0 or not preserve&1
        assert (target==0x3bb1e)==should_clear
        if should_clear:
            assert int(call[target][1],0)==0x3ba68
            clear+=1
        cases+=1
    return {'predicate':proof,'cases':cases,'clear_cases':clear,'preserve_cases':cases-clear,'source_admitted':False,'limits':['Checks predicate-to-branch composition and clear call target. Full system initialization and physical memory retention remain separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-startup-memory-decision.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'startup decision cases passed')
