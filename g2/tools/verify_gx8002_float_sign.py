# SPDX-License-Identifier: MIT
"""Execute bit-preserving sign operations against stock and integer identities."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-float-sign/sign.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-float-sign-build.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x49be4','--stop-address=0x49c14',str(wrapper)],text=True))
    values=[(sign<<31)|(exp<<23)|frac for sign in (0,1) for exp in range(256) for frac in (0,1,0x3fffff,0x400000,0x7fffff)]
    rng=random.Random(643);values += [rng.getrandbits(32) for _ in range(5000)];cases=0
    for value in values:
        for entry,sign in [(0x49be4,0),(0x49be4,0xffffffff),(0x49c04,0)]:
            args=[value,sign];expected=(value&0x7fffffff)|(sign&0x80000000)
            actual=execute(code,entry-0x3b940+0x10003000,bytes(20),float_arguments=args,return_float=True)
            original=execute(old,entry,bytes(20),float_arguments=args,return_float=True)
            assert actual==original==expected;cases+=1
    result={'source_elf_sha256':sha(data),'cases':cases,'source_admitted':False,'limits':['Sampled actual source/stock sign operations including signaling NaN payload preservation; integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-float-sign-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
