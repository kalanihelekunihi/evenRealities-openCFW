# SPDX-License-Identifier: MIT
"""Unsigned conversion normalized parts and 64-bit return ABI oracle."""
import json,subprocess,random,struct
from build_gx8002_floatunsidf import build,ROOT
from execute_gx8002_floatunsidf import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13a5c','--stop-address=0x13ab4',str(p)],text=True));new=decode((ROOT/'build/gx8002-floatunsidf/candidate.disassembly.txt').read_text())
    values=[0,1,0xffffffff];values.extend(v for i in range(32) for v in ((1<<i)-1,1<<i,min((1<<i)+1,0xffffffff)));rng=random.Random(623);values.extend(rng.getrandbits(32) for _ in range(1000))
    for value in values:
        expected=[2,0,0xa5a5a5a5,0xa5a5a5a5,0xa5a5a5a5] if not value else [3,0,value.bit_length()-1,(value<<(61-value.bit_length()))&0xffffffff,(value<<(61-value.bit_length()))>>32]
        result=struct.unpack('<II',struct.pack('<d',float(value)))
        def helper(t,a,m,e):
            assert t==0x1020a574
            fields=[word(m,a[0]+i*4) for i in range(5)];assert fields==expected,(value,fields,expected)
            e.append(('pack',*fields));return result
        for code,entry in ((old,0x13a5c),(new,0x1020a4d0)):
            ret,m,events=execute(code,entry,[value],{},helper)
            assert ret==('return',*result) and not m and events==[('pack',*expected)]
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Normalized parts, untouched zero fields and double return ABI checked; packer arithmetic remains a separate dependency.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-floatunsidf-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
