# SPDX-License-Identifier: MIT
"""Decode pinned CSI PSR save/restore and compare with authenticated stock."""
import json,subprocess
from itertools import product
from build_gx8002_backup_irq_state import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,psr,argument):
    registers={f'r{i}':0x12340000+i for i in range(32)}
    registers['r0']=argument;initial=registers.copy();trace=[];pc=entry
    for _ in range(4):
        op,args,width=code[pc]
        if op=='mfcr':
            assert args=='r0, cr<0, 0>'
            registers['r0']=psr;trace.append(('read_psr',psr))
        elif op=='psrclr':
            assert args=='ie'
            psr &= ~0x40;trace.append(('write_psr',psr))
        elif op=='mtcr':
            assert args=='r0, cr<0, 0>'
            psr=registers['r0'];trace.append(('write_psr',psr))
        elif op=='rts':
            assert all(registers[k]==initial[k] for k in registers if k!='r0')
            return registers['r0'],psr,trace
        else:raise AssertionError((op,args))
        pc+=width
    raise AssertionError('IRQ primitive instruction bound')


def verify():
    candidate=build();assert all(r['exact_stock_prefix'] for r in candidate['functions'])
    header=(ROOT/'build/upstream-nationalchip-lvp-kws/arch/soc/grus/include/core_ck804.h').read_text()
    assert '#define PSR_IE_Pos                         6U' in header
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d1ac','--stop-address=0x3d1c0',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-irq-state/state.disassembly.txt').read_text())
    states=sorted({0,0xffffffff,0x40,0xffffffbf,0x12345678,*[1<<i for i in range(32)],*[0xffffffff^(1<<i) for i in range(32)]})
    cases=0
    for psr,token in product(states,states):
        for code,save,restore in ((old,0x3d1ac,0x3d1b8),(new,0x1000486c,0x10004878)):
            a=execute(code,save,psr,token)
            assert a==(psr,psr&~0x40,[('read_psr',psr),('write_psr',psr&~0x40)])
            b=execute(code,restore,psr,token)
            assert b==(token,token,[('write_psr',token)])
            assert execute(code,restore,a[1],a[0])[1]==psr
        cases+=1
    result={'candidate':candidate,'status_token_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Exact compiled CSI instructions, decoded PSR accesses and register preservation.','IE mask from authenticated CSI header; physical exception acceptance and privileged execution remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-irq-state-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(verify()['status_token_cases'],'IRQ state cases passed')
