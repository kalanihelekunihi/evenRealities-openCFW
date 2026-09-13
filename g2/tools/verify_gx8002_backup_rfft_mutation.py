# SPDX-License-Identifier: MIT
"""Stock/source dispatcher rereads after scripted transform helper mutations."""
import json,subprocess
from itertools import product
from verify_gx8002_backup_rfft import execute,build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,decode

def verify():
    build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x478a4','--stop-address=0x47912',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-rfft/rfft.disassembly.txt').read_text())
    changes=[((0x1008,7,4),),((0x100c,0x100150dc,4),),((0x1004,0,1),(0x1005,255,1)),
             ((0x1010,0x11112222,4),),((0x1000,0,4),),((0x1000,2,4),),
             ((0x3000,0x8001,2),(0x3002,0x7fff,2))]
    count=0
    for inverse,target,writes,seed in product((0,1,2),(0x1000f1d4,0x1000efd4,0x1000f068),changes,(0,65535)):
        mutation=(target,writes)
        a=execute(old,0x478a4,0x10003000-0x3b940,8,inverse,1,seed,mutation)
        b=execute(new,0x1000ef64,0,8,inverse,1,seed,mutation)
        assert a==b,(inverse,mutation,a,b)
        count+=1
    report={'cases':count,'source_admitted':False,'limits':['Scripted helper writes to descriptor and output are composed with actual dispatcher instructions. Transform arithmetic remains modeled; not full FFT equivalence.']}
    (ROOT/'docs/research/gx8002-backup-rfft-mutation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
