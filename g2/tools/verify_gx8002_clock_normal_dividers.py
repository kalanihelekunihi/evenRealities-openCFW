# SPDX-License-Identifier: MIT
"""Compare normal module-source policy call sequence, not fragment admission."""
import json,subprocess
from build_gx8002_clock_normal_dividers_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32


def calls(code,start,end=None):
    r={};pc=start;out=[]
    for _ in range(100):
        if pc==end:return out
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op in ('push','pop'):
            if op=='pop':return out
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=r[p[1]]<<int(p[2],0)
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if start<0x100000 else 0);assert target in (0x10024df8,0x10024f44)
            out.append(('div' if target==0x10024df8 else 'dto',*[r[f'r{i}'] for i in range(2 if target==0x10024df8 else 3)]));r={}
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Bound')


def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17bea','--stop-address=0x17c78',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-normal-dividers-candidate.disassembly.txt').read_text())
    a=calls(old,0x17bea,0x17c78);b=calls(new,0x10025bd8);assert a==b and len(a)==16
    return {'candidate':candidate,'ordered_divider_dto_calls':a,'upstream_calls':b,'source_admitted':False,'limits':['All 16 divider/DTO calls match pinned upstream with explicitly recovered build configuration. Inlined fragment has no independent function boundary; full clk_init reconstruction required for admission.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-normal-dividers.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['ordered_divider_dto_calls']))
