# SPDX-License-Identifier: MIT
"""Compare decoded backup quotient/remainder with exact nonzero-divisor math."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-backup-unsigned-division/division.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-backup-unsigned-division.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x49ddc','--stop-address=0x4a434',str(wrapper)],text=True))
    table=bytes(i.bit_length() for i in range(256));assert stock[0x4df14:0x4e014]==table
    linked=Elf32(data,'source');assert linked.contents(next(s for s in linked.sections if s['name']=='.bit_lengths'))==table
    memory={0x100155d4+i:b for i,b in enumerate(table)}
    mask=(1<<64)-1;values=sorted({0,mask,*(((1<<k)+d)&mask for k in range(64) for d in (-1,0,1))})
    pairs=[(a,b) for a in values for b in values if b]
    rng=random.Random(6408);pairs += [(rng.getrandbits(64),rng.getrandbits(64) or 1) for _ in range(6000)]
    counts={}
    for name,entry,index in [('quotient',0x49ddc,0),('remainder',0x4a110,1)]:
        for a,b in pairs:
            args=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
            actual=execute(code,entry-0x3b940+0x10003000,bytes(20),arguments=args,return_pair=True,readonly=memory)
            original=execute(old,entry,bytes(20),arguments=args,return_pair=True,readonly=memory)
            expected=divmod(a,b)[index]
            assert actual==original==expected,(name,hex(a),hex(b),hex(actual),hex(original),hex(expected))
        counts[name]=len(pairs)
    zero_faults=0
    for entry in (0x49ddc,0x4a110):
        for a in values:
            for instructions,pc in ((code,entry-0x3b940+0x10003000),(old,entry)):
                try:
                    execute(instructions,pc,bytes(20),arguments=[a&0xffffffff,a>>32,0,0],return_pair=True,readonly=memory)
                except AssertionError as error:
                    assert str(error)=='zero divisor requires separate exception qualification'
                    zero_faults+=1
                else:raise AssertionError('zero divisor returned')
    result={'zero_divisor_fault_arrivals':zero_faults,'source_elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':counts,'source_admitted':False,'limits':['Nonzero-divisor source and stock instruction execution against exact unsigned arithmetic. Zero divisors reach DIVU with a zero operand in source and stock; exception dispatch/resumption, integration and hardware remain pending.']}
    (ROOT/'docs/research/gx8002-backup-unsigned-division-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
