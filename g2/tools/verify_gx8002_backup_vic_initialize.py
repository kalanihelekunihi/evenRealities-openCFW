# SPDX-License-Identifier: MIT
"""Compare complete VIC source effects with the stock inline startup sequence."""
import json
import random
import re
import subprocess
from build_gx8002_backup_vic_initialize import build, ROOT, sha, Elf32
from build_gx8002_backup_cfft import IMAGE, IMAGE_SHA
from verify_gx8002_memcpy_source import decode


def execute(code,start,stop,seed):
    rng=random.Random(seed)
    regs={f'r{i}':rng.getrandbits(32) for i in range(32)}
    original=regs.copy();trace=[];pc=start
    for _ in range(40):
        if pc==stop:
            assert all(regs[f'r{i}']==original[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return trace
        op,args,width=code[pc];parts=[x.strip() for x in args.split(',')]
        if op in ('lrw','movi'):regs[parts[0]]=int(parts[1],0)
        elif op=='mov':regs[parts[0]]=regs[parts[1]]
        elif op=='subi':regs[parts[0]]=(regs[parts[0]]-int(parts[1],0))&0xffffffff
        elif op=='mtcr':
            assert parts[1:]==['cr<1','0>']
            trace.append(('vector_base',regs[parts[0]]))
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            value,base,offset=m.groups();trace.append(('write',regs[base]+int(offset,0),regs[value]))
        elif op=='psrset':
            assert args=='ee, ie';trace.append(('enable','ee','ie'))
        else:raise ValueError((hex(pc),op,args))
        pc+=width
    raise ValueError('VIC sequence execution bound')


def verify():
    candidate=build();path=ROOT/'build/gx8002-backup-vic-initialize/vic.elf'
    assert sha(path.read_bytes())==candidate['elf_sha256']
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3bae4','--stop-address=0x3bb1e',str(wrapper)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    # Stock stop is the containing function's pop; source stop is its rts.
    # Only initialization effects are compared, not different wrapper frames.
    assert old[0x3bb1c][0]=='pop' and new[0x10018036][0]=='rts'
    expected=[('vector_base',0x10003000),('write',0xe000ec10,255)]
    for i in range(4):expected.extend([('write',0xe000e300+i*4,0),('write',0xe000e280+i*4,0xffffffff)])
    expected.append(('enable','ee','ie'))
    for seed in range(256):
        assert execute(old,0x3bae4,0x3bb1c,seed)==expected
        assert execute(new,0x10018000,0x10018036,seed)==expected
    return {'candidate':candidate,'stock_sha256':IMAGE_SHA,'cases':256,'ordered_effects':expected,'source_admitted':False,'limits':['Exact ordered control-register/MMIO effects and preserved registers checked from arbitrary seeded registers. Comparison ends before distinct wrapper returns. No hardware pending-interrupt acceptance, complete startup helpers, or image handoff execution modeled. Standalone source remains outside firmware placement.']}


if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-vic-initialize-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(result['cases'],'ordered VIC initialization cases')
