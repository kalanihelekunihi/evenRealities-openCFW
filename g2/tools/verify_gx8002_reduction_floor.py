# SPDX-License-Identifier: MIT
"""Execute linked binary64 floor against exact integer flooring of finite inputs."""
import json,math,random,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import bits,floating


def verify():
    path=ROOT/'build/gx8002-reduction-source-closure/reduction.elf';report=json.loads((ROOT/'docs/research/gx8002-reduction-source-closure.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256'];elf=Elf32(path.read_bytes(),'reduction')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    entry=next(s['value'] for s in elf.symbols() if s['name']=='floor')
    values=[(sign<<63)|(exponent<<52)|fraction for sign in (0,1) for exponent in (0,1,1022,1023,1042,1043,1074,1075,2046) for fraction in (0,1,1<<51,(1<<52)-1)]
    rng=random.Random(804);values += [rng.getrandbits(64) for _ in range(1000)]
    count=0
    for value in values:
        if (value>>52)&2047==2047:continue
        expected=value if value&((1<<63)-1)==0 else bits(float(math.floor(floating(value))))
        actual=execute(code,entry,bytes(20),arguments=[value&0xffffffff,value>>32],return_pair=True,readonly=memory,max_steps=10000)
        assert actual==expected,(hex(value),hex(actual),hex(expected));count+=1
    result={'source_elf_sha256':report['elf_sha256'],'finite_cases':count,'source_admitted':False,'limits':['Decoded finite floor and source arithmetic with ABI checks. Signed zero preserved. Nonfinite behavior, complete reducer execution, placement and hardware pending.']}
    (ROOT/'docs/research/gx8002-reduction-floor.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
