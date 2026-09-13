# SPDX-License-Identifier: MIT
"""Execute source and stock integer multiply against exact modulo arithmetic."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-muldi-source-cluster/muldi.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-muldi-source-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ad64','--stop-address=0x4adb0',str(wrapper)],text=True))
    mask=(1<<64)-1
    values=sorted({0,mask,*(( (1<<k)+d)&mask for k in range(64) for d in (-1,0,1))})
    pairs=[(a,b) for a in values for b in values]
    rng=random.Random(6404);pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(10000)]
    for a,b in pairs:
        args=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
        actual=execute(code,report['entry_address'],bytes(20),arguments=args,return_pair=True)
        original=execute(old,0x4ad64,bytes(20),arguments=args,return_pair=True)
        assert actual==original==(a*b)&mask,(hex(a),hex(b),hex(actual),hex(original))
    result={'source_elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(pairs),'source_admitted':False,'limits':['Actual source and stock instruction execution versus exact product modulo 2^64. Original-entry placement tested. Firmware integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-muldi-stock.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
