# SPDX-License-Identifier: MIT
"""Backup page-program wrapper's bounds and helper-return qualification."""
import json,subprocess
from itertools import product
from build_gx8002_backup_page_program import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute

def verify():
    candidate=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3fe00','--stop-address=0x3fe2c',str(path)],text=True))
    # Execute stock at its backup runtime address, avoiding the common decoder's primary-image delta.
    relocated={}
    for pc,(op,args,width) in old.items():
        if op in ('bsr','br','bt','bf','bez','bnez'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+0x10000000-0x38940);args=','.join(parts)
        relocated[pc+0x10000000-0x38940]=(op,args,width)
    old=relocated
    new=decode((ROOT/'build/gx8002-backup-page-program/page-program-linked.disassembly.txt').read_text());cases=0
    for address,length,size,result in product((0,1,255,256,0xffffffff),(0,1,255,256,257,0x80000000,0xffffffff),
                                              (0,256,512,0xffffffff),(0,1,0xffffffea,0xffffffff)):
        memory={};word(memory,0x20016d64,size);args=[address,0x20040000,length]
        valid=bool(length) and ((address+length)&0xffffffff)<=size
        want=result if valid else (0 if not length else 0xffffffea)
        for code,entry,target in ((old,0x100074c0,0x1000742c),(new,0x100074c0,0x1000742c)):
            calls=[]
            def callback(destination,parameters,state,events):
                assert destination==target and parameters[:3]==args
                calls.append(True);return result
            outcome,after,events=execute(code,entry,args,memory,callback)
            assert outcome[:2]==('return',want) and after==memory and not events and len(calls)==int(valid)
        cases+=1
    report={'candidate':candidate,'cases':cases,'source_admitted':False,
            'limits':['Wrapper only: unsigned wrapped bounds, zero length and helper-return forwarding checked. Page helper remains modeled; no physical programming.']}
    (ROOT/'docs/research/gx8002-backup-page-program-wrapper.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
