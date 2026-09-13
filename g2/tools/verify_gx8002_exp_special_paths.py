# SPDX-License-Identifier: MIT
"""Authenticate decoded stock exp special-path call shapes; no helper emulation claim."""
import json,subprocess,struct
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x4818c','--stop-address=0x48454',str(wrapper)],text=True))
    expected={0x4838c:('lrw','r2, 0x8800759c'),0x4838e:('lrw','r3, 0x7e37e43c'),
              0x48390:('mov','r0, r2'),0x48392:('mov','r1, r3'),0x48394:('bsr','0x4a790'),
              0x4839a:('mov','r2, r10'),0x4839c:('mov','r3, r1'),0x4839e:('mov','r0, r10'),0x483a0:('bsr','0x4a724'),
              0x483e2:('movi','r0, 0'),0x483e4:('mov','r1, r0'),0x483e6:('addi','r14, r14, 4'),0x483e8:('pop','r4-r11, r15')}
    for pc,pair in expected.items():assert code[pc][:2]==pair,(hex(pc),code[pc],pair)
    assert struct.unpack_from('<d',stock,0x4844c)[0]==1e300
    result={'stock_sha256':IMAGE_SHA,'checked_instructions':len(expected),'overflow_call':0x4a790,'nan_call':0x4a724,
            'underflow_direct_zero':True,'source_admitted':False,'limits':['Decoded stock path structure and operand bits only. Arithmetic helper semantics and NaN payload/exception behavior remain unverified.']}
    (ROOT/'docs/research/gx8002-exp-special-paths.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
