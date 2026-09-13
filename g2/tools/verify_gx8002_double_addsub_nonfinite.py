# SPDX-License-Identifier: MIT
"""Execute source add/subtract nonfinite operands with actual source NaN data."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def oracle(a,b,subtract):
    if subtract:b ^= 1<<63
    def nan(x):return (x>>52)&2047==2047 and x&((1<<52)-1)!=0
    if nan(a):return a|(1<<51)
    if nan(b):return b|(1<<51)
    infinity=0x7ff0000000000000;mask=(1<<63)-1
    if a&mask==infinity and b&mask==infinity:return a if a==b else 0x7ff8000000000000
    if a&mask==infinity:return a
    assert b&mask==infinity
    return b

def verify(placed=False,stock_compare=False):
    stem='gx8002-double-addsub-placed' if placed else 'gx8002-double-addsub-cluster'
    path=ROOT/'build'/stem/'addsub.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text());assert sha(data)==report['elf_sha256']
    elf=Elf32(data,'source');symbols={s['name']:s['value'] for s in elf.symbols()}
    section=next(s for s in elf.sections if s['name']=='.nan');constant=elf.contents(section)
    # GCC's typed __thenan_df = { CLASS_SNAN, 0, 0, {0} }.
    assert constant==bytes(20) and symbols['__thenan_df']==section['address']
    readonly={section['address']+i:b for i,b in enumerate(constant)}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=None;old_readonly={}
    if stock_compare:
        stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
        wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';original=Elf32(wrapper.read_bytes(),'stock')
        assert original.contents(next(s for s in original.sections if s['name']=='.data'))==stock
        old=decode(subprocess.check_output([pre,'-D','--start-address=0x4a460','--stop-address=0x4b0b8',str(wrapper)],text=True))
        address=0x100155c0;offset=address-0x10003000+0x3b940
        assert old[0x4a660][:2]==('lrw','r2, 0x100155c0')
        assert int.from_bytes(stock[0x4a78c:0x4a790],'little')==address
        assert stock[offset:offset+20]==constant
        old_readonly={address+i:b for i,b in enumerate(stock[offset:offset+20])}
    payloads=[0,1,(1<<52)-1]+[1<<bit for bit in range(52)]
    rng=random.Random(804);payloads += [rng.getrandbits(52) for _ in range(128)]
    special=[(sign<<63)|0x7ff0000000000000|p for sign in (0,1) for p in payloads]
    other=[0,1,1<<63,0x3ff0000000000000,0xbff0000000000000,0x7fefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000123,0xfff0000000000123]
    pairs=[(a,b) for a in special for b in other]+[(b,a) for a in special for b in other]
    for subtract in (False,True):
        for a,b in pairs:
            actual=execute(code,symbols['__subdf3' if subtract else '__adddf3'],bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=readonly)
            expected=oracle(a,b,subtract)
            assert actual==expected,(subtract,hex(a),hex(b),hex(actual),hex(expected))
            if old is not None:
                original=execute(old,0x4a754 if subtract else 0x4a724,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=old_readonly)
                assert original==actual,(subtract,hex(a),hex(b),hex(original),hex(actual))
    result={'stock_compared':stock_compare,'stock_sha256':IMAGE_SHA if stock_compare else None,'placed':placed,'source_elf_sha256':sha(data),'nan_data_sha256':sha(constant),'cases':len(pairs)*2,'source_admitted':False,'limits':['Decoded execution includes source-generated canonical NaN data, payload propagation and subtraction sign handling.', 'Computed references, firmware integration, hardware and exception behavior remain unqualified.']}
    (ROOT/'docs/research'/('gx8002-double-addsub-nonfinite'+('-placed' if placed else '')+('-stock' if stock_compare else '')+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
