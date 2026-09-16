# SPDX-License-Identifier: MIT
"""Compare backup synchronization status polling with decoded stock."""
import json,subprocess
from itertools import product
from build_gx8002_backup_flash_sync import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_backup_flash_quad import execute
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3fa58','--stop-address=0x3fa78',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-sync/sync-linked.disassembly.txt').read_text());cases=0
    for last,busy,result in product(range(0,256,2),(0,1,3),(0,1,0xffffffff)):
        values=[(5,255)]*busy+[(5,last)];want=(result,[('read',c,v) for c,v in values])
        assert execute(old,0x3fa58,0x10000000-0x38940,values,result)==execute(new,0x10007118,0,values,result)==want
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Every even status byte and delayed readiness checked with scripted byte writes and transport returns. Public SDK sync is void; observed r0 retained internally only. No physical hardware or failed read without output byte qualification.']}
    (ROOT/'docs/research/gx8002-backup-sync-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
