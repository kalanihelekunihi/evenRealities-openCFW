# SPDX-License-Identifier: MIT
"""Finite-domain conversion and complete helper argument trace oracle."""
import json,struct,subprocess,math,random
from itertools import product
from build_gx8002_fixunsdfsi import build,ROOT
from execute_gx8002_fixunsdfsi import execute
from verify_gx8002_memcpy_source import decode

def words(value):return struct.unpack('<II',struct.pack('<d',value))
def number(a):return struct.unpack('<d',struct.pack('<II',*a[:2]))[0]
def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12ff8','--stop-address=0x13030',str(p)],text=True));new=decode((ROOT/'build/gx8002-fixunsdfsi/candidate.disassembly.txt').read_text())
    values=[0.,-0.,0.5,1.,1.9,2147483647.,2147483647.5,2147483648.,2147483648.5,4294967295.,math.nextafter(4294967296.,0.)]
    rng=random.Random(319);values.extend(rng.random()*4294967296. for _ in range(500))
    for value in values:
        trace=[('compare',*words(value),*words(2147483648.))]
        converted=value
        if value>=2147483648.:trace.append(('subtract',*words(value),*words(2147483648.)));converted=value-2147483648.
        trace.append(('signed',*words(converted)))
        def helper(t,a,m,e):
            if t==0x1020a420:e.append(('compare',*a));return (0 if number(a)>=number(a[2:]) else 0xffffffff)
            if t==0x1020a0cc:e.append(('subtract',*a));return words(number(a)-number(a[2:]))
            if t==0x1020a460:e.append(('signed',*a[:2]));return int(number(a))&0xffffffff
            raise ValueError('Unknown helper')
        for code,entry in ((old,0x12ff8),(new,0x10209a6c)):
            ret,m,events=execute(code,entry,list(words(value)),{},helper)
            assert ret==('return',int(value)) and not m and events==trace,(value,ret,events,trace)
    opaque_cases=0
    for bits,comparison,signed,subtracted in product((0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0x7ff0000000000001,0xbff0000000000000,0x41f0000000000000),(0,1,0x7fffffff,0x80000000,0xffffffff),(0,0x7fffffff,0x80000000,0xffffffff),((0,0),(0x12345678,0xabcdef01))):
        arguments=[bits&0xffffffff,bits>>32]
        takes_subtract=comparison<0x80000000
        expected=[('compare',*arguments,*words(2147483648.))]
        if takes_subtract:expected.append(('subtract',*arguments,*words(2147483648.)))
        expected.append(('signed',*(subtracted if takes_subtract else arguments)))
        def boundary(t,a,m,e):
            if t==0x1020a420:e.append(('compare',*a));return comparison
            if t==0x1020a0cc:e.append(('subtract',*a));return subtracted
            if t==0x1020a460:e.append(('signed',*a[:2]));return signed
            raise ValueError('Unknown helper')
        for code,entry in ((old,0x12ff8),(new,0x10209a6c)):
            ret,m,events=execute(code,entry,arguments,{},boundary)
            assert ret==('return',(signed+(0x80000000 if takes_subtract else 0))&0xffffffff) and not m and events==expected
        opaque_cases+=1
    return {'candidate':candidate,'cases':len(values),'helper_boundary_cases':opaque_cases,'source_admitted':False,'limits':['Finite unsigned-domain mathematical oracle and special-bit-pattern helper boundary equivalence checked. Nested floating helper semantics, exception delivery and hardware timing remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-fixunsdfsi-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
