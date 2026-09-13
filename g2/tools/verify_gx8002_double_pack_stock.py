# SPDX-License-Identifier: MIT
"""Direct stock/source pack comparison on normal and overflow rounding paths."""
import json,struct,subprocess,random
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_pack_rounding import oracle

def verify(nonfinite=False):
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-double-core-layout/core.elf';report=json.loads((ROOT/'docs/research/gx8002-double-core-layout.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'core');entry=next(s['value'] for s in elf.symbols() if s['name']=='__pack_d')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ae44','--stop-address=0x4afd4',str(wrapper)],text=True));new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    vendor=ROOT/'build/upstream-xuantie-qemu-csky/translate_v2.c'
    assert sha(vendor.read_bytes())=='d56e8f41f25c225e3a6d7446a26062cacee2a4f9fe6a2df8661cf066c9e373a5'
    cases=0
    for exponent in (() if nonfinite else (-1200,*range(-1080,-1019),-1,0,1,1022,1023,1024)):
        for base in ((1<<52),(1<<52)+1,(1<<53)-2,(1<<53)-1):
            for residue in range(256):
                fraction=(base<<8)|residue
                for sign in (0,1):
                    parts=struct.pack('<5I',3,sign,exponent&0xffffffff,fraction&0xffffffff,fraction>>32)
                    expected=oracle(sign,exponent,fraction)
                    assert execute(old,0x4ae44,parts)==execute(new,entry,parts)==expected,(exponent,base,residue,sign)
                    cases+=1
    if nonfinite:
        from verify_gx8002_double_unpack import oracle as unpack
        rng=random.Random(804);payloads=[0,1,(1<<51),(1<<52)-1]+[1<<i for i in range(52)]+[rng.getrandbits(52) for _ in range(4096)]
        for sign in (0,1):
            for payload in payloads:
                value=(sign<<63)|(2047<<52)|payload
                expected=value|(1<<51) if payload else value
                parts=unpack(value)
                assert execute(old,0x4ae44,parts)==execute(new,entry,parts)==expected,hex(value)
                cases+=1
            parts=unpack(sign<<63)
            assert execute(old,0x4ae44,parts)==execute(new,entry,parts)==sign<<63
            cases+=1
    result={'nonfinite':nonfinite,'stock_sha256':IMAGE_SHA,'source_elf_sha256':sha(path.read_bytes()),'cases':cases,'instruction_semantics_sha256':sha(vendor.read_bytes()),'source_admitted':False,'limits':['Direct decoded stock/source/exact-integer comparison of normal, underflow and overflow rounding. Finite rounding and nonfinite modes are reported separately; arbitrary noncanonical structures remain outside scope.']}
    (ROOT/('docs/research/gx8002-double-pack-stock-nonfinite.json' if nonfinite else 'docs/research/gx8002-double-pack-stock.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
