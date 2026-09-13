# SPDX-License-Identifier: MIT
"""Execute original and upstream source double to signed-int conversion."""
import json,struct,random,subprocess,math
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-double-bidirectional-conversion-cluster/wrappers.elf';report=json.loads((ROOT/'docs/research/gx8002-double-bidirectional-conversion-cluster.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    e=Elf32(path.read_bytes(),'source');entry=next(s['value'] for s in e.symbols() if s['name']=='__fixdfsi')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ac38','--stop-address=0x4b0b8',str(wrapper)],text=True));new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=[float(i)/8 for i in range(-2048,2049)]+[math.inf,-math.inf,math.nan,0.0,-0.0]
    for value in (-(1<<31),(1<<31)-1,1<<31):
        values += [float(value),math.nextafter(float(value),-math.inf),math.nextafter(float(value),math.inf)]
    rng=random.Random(804);values += [struct.unpack('<d',rng.getrandbits(64).to_bytes(8,'little'))[0] for _ in range(10000)]
    for value in values:
        expected=0 if math.isnan(value) else -(1<<31) if value<=-(1<<31) else (1<<31)-1 if value>=(1<<31) else math.trunc(value)
        raw=struct.unpack('<Q',struct.pack('<d',value))[0];args=[raw&0xffffffff,raw>>32]
        assert execute(old,0x4ac38,bytes(20),arguments=args)==execute(new,entry,bytes(20),arguments=args)==expected&0xffffffff,value
    result={'stock_sha256':IMAGE_SHA,'source_elf_sha256':sha(path.read_bytes()),'cases':len(values),'source_admitted':False,'limits':['Decoded conversion and actual nested unpack execution; truncation, NaN-to-zero and signed saturation oracle. Finite sampling, not hardware qualification.']}
    (ROOT/'docs/research/gx8002-fixdfsi-stock.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
