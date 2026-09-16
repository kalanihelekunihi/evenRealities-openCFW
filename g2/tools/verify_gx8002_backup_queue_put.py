# SPDX-License-Identifier: MIT
"""Compare backup queue writer with pinned upstream C and an independent FIFO oracle."""
import json,subprocess
from build_gx8002_backup_queue_put import build,ROOT,Elf32,sha,IMAGE_SHA
from execute_gx8002_backup_queue_put import execute
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-queue-put'
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([prefix,'-D','--start-address=0x4e4a4','--stop-address=0x4e508',str(wrapper)],text=True))
    candidate=decode((out/'queue.disassembly.txt').read_text())
    cases=0
    for member in (1,2,3,4,8,16):
        for slots in (2,3,8,17):
            size=member*slots
            for head in range(0,size,member):
                for tail in range(0,size,member):
                    memory={0x2000+i:(i*73+19)%256 for i in range(size)}
                    memory.update({0x3000+i:(i*37+81)%256 for i in range(member)})
                    for offset,value in enumerate((tail,head,0x2000,size,member)):
                        for i in range(4):memory[0x1000+offset*4+i]=(value>>(i*8))&255
                    before=memory.copy()
                    other=memory.copy()
                    a,at=execute(original,memory,0x4e4a4)
                    b,bt=execute(candidate,other,0x10015b64)
                    if a!=b or memory!=other or at!=bt:raise ValueError(('stock/upstream execution mismatch',member,slots,head,tail,a,b,at,bt))
                    expected=before.copy()
                    full=(tail+member)%size==head
                    if not full:
                        for i in range(member):expected[0x2000+(tail+i)%size]=before[0x3000+i]
                        new_tail=(tail+member)%size
                        for i in range(4):expected[0x1000+i]=(new_tail>>(8*i))&255
                    if a!=int(not full) or memory!=expected:raise ValueError('independent FIFO oracle mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Exact memory access trace, resulting memory, return and saved ABI checked for finite valid queues.', 'No concurrent metadata mutation, buffer/value overlap, zero queue size or signed-overflow C inputs qualified.']}
    (ROOT/'docs/research/gx8002-backup-queue-put-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
