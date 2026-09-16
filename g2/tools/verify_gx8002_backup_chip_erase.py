# SPDX-License-Identifier: MIT
"""Backup chip-erase wrappers: exact code and decoded argument forwarding."""
import json,subprocess
from itertools import product
from build_gx8002_backup_chip_erase import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute

def verify():
    evidence=build();assert all(r['byte_exact'] for r in evidence['functions'])
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x408a4','--stop-address=0x408c0',str(path)],text=True));relocated={}
    for pc,(op,args,width) in old.items():
        if op=='bsr':args=hex(int(args,0)+0x10000000-0x38940)
        relocated[pc+0x10000000-0x38940]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-chip-erase/erase-linked.disassembly.txt').read_text());cases=0
    for size,result in product((0,1,4095,4096,0x3f000,0xff000,0x80000000,0xffffffff),(0,1,0xffffffea,0xffffffff)):
        for entry,target in ((0x10007f64,0x1000764c),(0x10007f78,0x10007f64)):
            memory={};word(memory,0x20016d64,size)
            for code in (relocated,new):
                calls=[]
                def callback(destination,args,state,events):
                    assert destination==target
                    if entry==0x10007f64:assert args[:2]==[0,size]
                    calls.append(True);return result
                outcome,after,events=execute(code,entry,[],memory,callback)
                assert outcome[:2]==('return',result) and after==memory and not events and len(calls)==1
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Both wrappers byte-exact; argument and result forwarding checked with helpers modeled. Range erase and physical operations require separate qualification.']}
    (ROOT/'docs/research/gx8002-backup-chip-erase-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
