# SPDX-License-Identifier: MIT
"""Decoded unsigned conversion and source packer together, without helper mocks."""
import json,subprocess,random,struct
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from execute_gx8002_floatunsidf import execute
from execute_gx8002_pack_double import execute as pack
from verify_gx8002_memcpy_source import decode

def verify():
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13a5c','--stop-address=0x13c90',str(path)],text=True))
    source={};evidence={}
    for name in ('floatunsidf','pack_double'):
        p=ROOT/('build/gx8002-'+name+'/candidate.elf');e=Elf32(p.read_bytes(),name)
        report=json.loads((ROOT/('docs/research/gx8002-'+name+'-candidate.json')).read_text())
        section=next(s for s in e.sections if s['name']=='.text');assert sha(e.contents(section))==report['compiled_sha256']
        source[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));evidence[name]={'elf_sha256':sha(p.read_bytes()),'source_sha256':report['source_sha256']}
    values=[0,1,0xffffffff];values.extend(v for i in range(32) for v in ((1<<i)-1,1<<i,min((1<<i)+1,0xffffffff)));rng=random.Random(623);values.extend(rng.getrandbits(32) for _ in range(10000))
    for value in values:
        expected=struct.unpack('<II',struct.pack('<d',float(value)))
        for stock in (True,False):
            calls=[]
            def helper(t,a,m,e):
                assert t==0x1020a574;calls.append(t)
                ret,after,events=pack(old if stock else source['pack_double'],0x13b00 if stock else t,a[:1],m,lambda *x:None)
                assert ret[0]=='return' and after==m and not events
                return ret[1:]
            ret,m,events=execute(old if stock else source['floatunsidf'],0x13a5c if stock else 0x1020a4d0,[value],{},helper)
            assert ret==('return',*expected) and not m and not events and calls==[0x1020a574],(value,ret,expected)
    return {'cases':len(values),'evidence':evidence,'limits':['Nested decoded conversion and packing checks exact binary64 output, no writes outside stack and integer/return ABI; hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-floatunsidf-nested.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
