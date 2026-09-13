# SPDX-License-Identifier: MIT
"""Execute original and upstream source signed-int to double conversion."""
import json,struct,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-double-conversion-cluster/wrappers.elf';report=json.loads((ROOT/'docs/research/gx8002-double-conversion-cluster.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    e=Elf32(path.read_bytes(),'source');entry=next(s['value'] for s in e.symbols() if s['name']=='__floatsidf')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4abd0','--stop-address=0x4afd4',str(wrapper)],text=True));new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=list(range(-2048,2049))+[-(1<<31),(1<<31)-1]
    values += [sign*((1<<bit)+delta) for sign in (-1,1) for bit in range(31) for delta in (-1,0,1)]
    rng=random.Random(804);values += [rng.randrange(-(1<<31),1<<31) for _ in range(10000)]
    for value in values:
        expected=struct.unpack('<Q',struct.pack('<d',float(value)))[0];args=[value&0xffffffff]
        assert execute(old,0x4abd0,bytes(20),arguments=args,return_pair=True)==execute(new,entry,bytes(20),arguments=args,return_pair=True)==expected,value
    result={'stock_sha256':IMAGE_SHA,'source_elf_sha256':sha(path.read_bytes()),'cases':len(values),'source_admitted':False,'limits':['Decoded conversion and actual nested pack execution; all int32 values are exactly representable by binary64. Finite sampling, not exhaustive int32 enumeration or hardware qualification.']}
    (ROOT/'docs/research/gx8002-floatsidf-stock.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
