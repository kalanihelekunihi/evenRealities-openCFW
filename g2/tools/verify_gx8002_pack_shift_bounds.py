# SPDX-License-Identifier: MIT
"""Bind pack's underflow count range to its actual relocated instructions."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    path=ROOT/'build/gx8002-double-core-layout/core.elf';report=json.loads((ROOT/'docs/research/gx8002-double-core-layout.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'core');symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    checks={0x10012576:('ld.w','r2, (r0, 0x8)'),0x10012578:('movi','r8, 1021'),0x1001257c:('nor','r8, r8'),
            0x1001257e:('cmplt','r2, r8'),0x10012580:('bf','0x100125f6'),0x10012582:('subu','r8, r2'),
            0x10012584:('cmplti','r8, 57'),0x10012588:('bf','0x100125ec'),0x1001258a:('mov','r2, r8'),
            0x1001258c:('mov','r0, r4'),0x1001258e:('mov','r1, r5'),0x10012590:('bsr',hex(symbols['__lshrdi3'])),
            0x10012594:('mov','r6, r0'),0x10012596:('mov','r7, r1'),0x10012598:('mov','r2, r8'),
            0x1001259a:('bmaski','r0, 32'),0x1001259e:('bmaski','r1, 32'),0x100125a2:('bsr',hex(symbols['__ashldi3']))}
    for pc,pair in checks.items():assert code[pc][:2]==pair,(hex(pc),code[pc],pair)
    calls=[pc for pc,(op,args,w) in code.items() if op=='bsr'];assert calls==[0x10012590,0x100125a2]
    # No direct transfer can bypass either comparison or enter between guards and calls.
    incoming=[]
    for pc,(op,args,w) in code.items():
        if op in ('br','bt','bf','bez','bnez','bsr'):
            target=int(args.split(',')[-1].strip(),0)
            if 0x10012582<=target<=0x100125a2:incoming.append((pc,target))
    assert not incoming
    # For every int32 exponent below -1022, subtraction is positive and representable.
    assert -1022-(-(1<<31))==2147482626<1<<31
    admitted=[e for e in range(-1200,-1000) if e < -1022 and -1022-e <57]
    assert admitted==list(range(-1078,-1022))
    result={'source_elf_sha256':sha(path.read_bytes()),'checked_instructions':len(checks),'shift_count_interval':[1,56],'exponent_interval':[-1078,-1023],
            'source_admitted':False,'limits':['Signed int32 exponent algebra and authenticated local decoded control flow. The first helper preserves r8 under existing callee-save checks, so both calls receive the same bounded count.',
                      'Does not prove arbitrary computed entry exclusion or pack numerical behavior; assumes normal pack entry and declared parts layout.']}
    (ROOT/'docs/research/gx8002-pack-shift-bounds.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
