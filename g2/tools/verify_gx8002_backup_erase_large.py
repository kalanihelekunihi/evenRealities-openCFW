# SPDX-License-Identifier: MIT
"""Execute large wrapped erase loops fully, using a streaming effect oracle."""
import json,subprocess
from itertools import product
from compare_gx8002_backup_flash_erase import execute,build,ROOT,IMAGE,MASK,decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def trace(address,length,size,widths,counts):
    yield ['read',0x20016d64,size]
    current=address&0xfffff000;remaining=(min((address+length)&MASK,size)-current)&MASK;epoch=0
    while remaining:
        chunk=65536 if current%65536==0 and remaining>=65536 else 4096
        w=widths[epoch%len(widths)];epoch+=1
        counts['commands']+=1;counts['bytes']+=chunk
        yield ['ready',0x10007350,[]]
        yield ['command',0x10006cb0,[6,0,0]]
        yield ['read',0x20016d68,w]
        for i in range(1,5):
            shift=((w-i)*8)&63
            yield ['write',0x20016d70+i,(current>>shift)&255 if shift<32 else 0]
        yield ['command',0x10006cb0,[0xd8 if chunk==65536 else 0x20,0x20016d71,3]]
        yield ['ready',0x10007350,[]]
        remaining=max(remaining,4096)-chunk;current=(current+chunk)&MASK


def verify():
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3ff8c','--stop-address=0x400d0',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-erase/erase-linked.disassembly.txt').read_text());rows=[]
    for address,size,widths in product((4096,65536),(0,4096,65536,131072),((3,),(0,4,MASK))):
        length=MASK
        if address>=size:continue
        remaining=(min((address+length)&MASK,size)-(address&0xfffff000))&MASK
        if remaining<=131072:continue
        counts=[]
        for code,entry,delta,frame in ((old,0x3ff8c,0x10000000-0x38940,28),(new,0x1000764c,0,40)):
            count={'commands':0,'bytes':0}
            assert execute(code,entry,delta,address,length,0,trace(address,length,size,widths,count),seed=0x1234,frame=frame,instruction_limit=20000000)==0
            counts.append(count)
        assert counts[0]==counts[1]
        rows.append({'address':address,'length':length,'size':size,'widths':widths,**counts[0]})
        print('completed large case',len(rows),rows[-1],flush=True)
    assert len(rows)==6
    report={'build':evidence,'cases':rows,'source_admitted':False,'hardware_qualified':False,
            'limits':['All six previously excluded wrapped-underflow inputs execute full decoded loops; streaming only avoids retaining the oracle in memory. Readiness and command transport remain modeled; no physical erases performed.']}
    (ROOT/'docs/research/gx8002-backup-erase-large.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':verify()
