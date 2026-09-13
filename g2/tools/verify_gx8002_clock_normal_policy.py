# SPDX-License-Identifier: MIT
"""Compare normal module-source policy call sequence, not fragment admission."""
import json,subprocess
from build_gx8002_clock_normal_policy_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
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
        elif op=='bsr':
            assert int(args,0)+(0x1000dfec if start<0x100000 else 0)==0x10024be0;out.append((r['r0'],r['r1']));r={}
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Bound')


def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17b52','--stop-address=0x17bea',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-normal-policy-candidate.disassembly.txt').read_text())
    a=calls(old,0x17b52,0x17bea);b=calls(new,0x10025b40);assert len(a)==len(b)==19
    differences=[{'index':i,'stock':x,'upstream':y} for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert differences==[{'index':8,'stock':(7,3),'upstream':(7,4)}]
    return {'candidate':candidate,'ordered_module_source_calls':a,'upstream_calls':b,'differences':differences,'source_admitted':False,'limits':['18 of 19 calls match slight_1v; ADC differs (stock SYS, upstream 32K). Inlined fragment has no independent function boundary; full clk_init reconstruction required for admission.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-normal-policy.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['ordered_module_source_calls']))
