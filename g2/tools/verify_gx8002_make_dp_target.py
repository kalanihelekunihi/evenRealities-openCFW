# SPDX-License-Identifier: MIT
"""Execute source and stock constructors with split register/stack fraction ABI."""
import json,struct,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_unpack import oracle as unpack

def verify():
    p=ROOT/'build/gx8002-make-dp-cluster/make.elf';data=p.read_bytes();report=json.loads((ROOT/'docs/research/gx8002-make-dp-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    elf=Elf32(data,'source');entry=next(s['value'] for s in elf.symbols() if s['name']=='__make_dp')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oldelf=Elf32(wrapper.read_bytes(),'stock');assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(p)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x4aca8','--stop-address=0x4afd4',str(wrapper)],text=True))
    values=[(s<<63)|(e<<52)|f for s in (0,1) for e in range(2048) for f in (0,1,(1<<52)-1)]
    rng=random.Random(804);values += [rng.getrandbits(64) for _ in range(2048)]
    for value in values:
        fields=unpack(value);cls,sign,exp,lo,hi=struct.unpack('<IIIII',fields)
        stack={0x8000+i:b for i,b in enumerate(hi.to_bytes(4,'little'))}
        args=[cls,sign,exp,lo]
        a=execute(code,entry,bytes(20),arguments=args,return_pair=True,readonly=stack)
        b=execute(old,0x4aca8,bytes(20),arguments=args,return_pair=True,readonly=stack)
        expected=value|1<<51 if (value>>52)&2047==2047 and value&((1<<52)-1) else value
        assert a==b==expected,(hex(value),hex(a),hex(b),hex(expected))
    result={'source_elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(values),'source_admitted':False,'limits':['Register arguments class/sign/exponent/fraction-low and stack fraction-high exercised through actual source/stock constructors and packers. Canonical parts only; references/integration/hardware pending.']}
    (ROOT/'docs/research/gx8002-make-dp-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
