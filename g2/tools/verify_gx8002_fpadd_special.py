# SPDX-License-Identifier: MIT
"""Exceptional-class returned-pointer and complete memory oracle."""
import json,subprocess
from itertools import product
from build_gx8002_fpadd_parts import build,ROOT,Elf32,IMAGE
from execute_gx8002_fpadd_parts import execute
from verify_gx8002_fpadd_parts import finite_oracle
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13364','--stop-address=0x13658',str(path)],text=True));new=decode((ROOT/'build/gx8002-fpadd_parts/candidate.disassembly.txt').read_text())
    elf=Elf32((ROOT/'build/gx8002-fpadd_parts/candidate.elf').read_bytes(),'candidate');constant=next(s for s in elf.sections if s['name']=='.rodata.nan');assert constant['address']==0x1020bd08 and elf.contents(constant)==bytes(20)==IMAGE.read_bytes()[0x15294:0x152a8]
    cases=0
    for ca,cb,sa,sb in product(range(5),range(5),range(2),range(2)):
        a={0:ca,4:sa,8:5,12:0x123400,16:0x10000000};b={0:cb,4:sb,8:3,12:0x345600,16:0x10000000};tmp={k:0xa5a5a5a5 for k in a}
        pointer=0x20040200
        if ca<2:pointer=0x20040000
        elif cb<2:pointer=0x20040100
        elif ca==4:pointer=0x1020bd08 if cb==4 and sa!=sb else 0x20040000
        elif cb==4:pointer=0x20040100
        elif cb==2:
            if ca==2:tmp={**a,4:sa&sb}
            else:pointer=0x20040000
        elif ca==2:pointer=0x20040100
        else:tmp=finite_oracle(a,b)
        expected={base+off:v for base,fields in ((0x20040000,a),(0x20040100,b),(0x20040200,tmp),(0x1020bd08,{k:0 for k in a})) for off,v in fields.items()}
        for code,entry in ((old,0x13364),(new,0x10209dd8)):
            ret,m=execute(code,entry,a,b,full=True)
            assert ret==pointer and m==expected,(ca,cb,sa,sb,ret,pointer,m,expected)
        cases+=1
    return {'candidate':candidate,'cases':cases,'limits':['All canonical exceptional class/sign pairs and full external memory checked; aliasing and nested arithmetic integration remain separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-fpadd-special.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
