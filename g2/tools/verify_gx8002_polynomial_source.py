# SPDX-License-Identifier: MIT
"""Execute Horner source against exact rational arithmetic rounded at each step."""
import json, random, subprocess
from fractions import Fraction
from build_gx8002_backup_cfft import ROOT, sha, Elf32, IMAGE, IMAGE_SHA
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import bits, floating


def verify():
    code, readonly, hashes = {}, {}, {}
    for stem, filename in [('gx8002-exp-placed-cluster','exp.elf'),('gx8002-polynomial-placed','polynomial.elf')]:
        path=ROOT/'build'/stem/filename
        report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text())
        assert sha(path.read_bytes())==report['elf_sha256']
        hashes[stem]=report['elf_sha256']
        elf=Elf32(path.read_bytes(),stem)
        decoded=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
        assert not set(code).intersection(decoded);code.update(decoded)
        for s in elf.sections:
            if s['flags']&2 and s['size'] and s['type']!=8:
                readonly.update({s['address']+i:b for i,b in enumerate(elf.contents(s))})
    stock=IMAGE.read_bytes(); assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    se=Elf32(wrapper.read_bytes(),'stock')
    assert se.contents(next(s for s in se.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x49828','--stop-address=0x4b238',str(wrapper)],text=True))
    stock_memory={base+i:b for base in (0x10003000,0x20003000) for i,b in enumerate(stock[0x3b940:0x4f9cc])}
    rng=random.Random(49828);count=0
    for degree in range(17):
        for _ in range(40):
            coefficients=[rng.randrange(-1024,1025)/64 for _ in range(degree+1)]
            x=rng.randrange(-128,129)/64
            expected=coefficients[-1]
            for coefficient in reversed(coefficients[:-1]):
                product=float(Fraction(x)*Fraction(expected))
                expected=float(Fraction(product)+Fraction(coefficient))
            payload=b''.join(bits(v).to_bytes(8,'little') for v in coefficients)
            memory=dict(readonly);memory.update({0x20040000+i:b for i,b in enumerate(payload)})
            xb=bits(x)
            actual=execute(code,0x49828+0x10003000-0x3b940,bytes(20),arguments=[0x20040000,degree,xb&0xffffffff,xb>>32],readonly=memory,return_pair=True,max_steps=100000)
            sm=dict(stock_memory);sm.update({0x20040000+i:b for i,b in enumerate(payload)})
            original=execute(old,0x49828,bytes(20),arguments=[0x20040000,degree,xb&0xffffffff,xb>>32],readonly=sm,return_pair=True,max_steps=100000)
            assert original==actual==bits(expected),(degree,x,hex(actual),hex(bits(expected)))
            count+=1
    identity_count=0; passthrough_count=0
    values=[(sign<<63)|(exponent<<52)|fraction for sign in (0,1) for exponent in (0,1,2,1022,1023,1024,2045,2046,2047) for fraction in (0,1,1<<51,(1<<52)-1)]
    values += [rng.getrandbits(64) for _ in range(1000)]
    for value in values:
        # Degree zero must preserve every payload, regardless of x classification.
        for degree,coefficient_bits,xb,expected in [(0,[value],0x7ff0000000000001,value)]+([(1,[0,0x3ff0000000000000],value,value if value&((1<<63)-1) else 0)] if (value>>52)&2047!=2047 else []):
            payload=b''.join(v.to_bytes(8,'little') for v in coefficient_bits)
            results=[]
            for instructions,entry,base_memory in [(code,0x49828+0x10003000-0x3b940,readonly),(old,0x49828,stock_memory)]:
                memory=dict(base_memory);memory.update({0x20040000+i:b for i,b in enumerate(payload)})
                results.append(execute(instructions,entry,bytes(20),arguments=[0x20040000,degree,xb&0xffffffff,xb>>32],readonly=memory,return_pair=True,max_steps=100000))
            assert results==[expected,expected],(degree,hex(value),[hex(v) for v in results],hex(expected))
            if degree:identity_count+=1
            else:passthrough_count+=1
    result={'source_elf_hashes':hashes,'identity_cases':identity_count,'degree_zero_payload_cases':passthrough_count,'finite_cases':count,'stock_comparison_cases':count,'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['Exact rational per-operation rounding on bounded finite coefficients and inputs; degree 0..16. Full-exponent identity and arbitrary degree-zero payload checks also compare stock. General nonfinite arithmetic, higher-degree extreme exponents, integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-polynomial-source.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
