# SPDX-License-Identifier: MIT
"""Execute complete source binary64 comparison wrappers with nested helpers."""
import json,random,struct,math,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    stock_compare=True;twins=False
    path=ROOT/'build/gx8002-double-inequality-cluster/wrappers.elf';report=json.loads((ROOT/'docs/research/gx8002-double-inequality-cluster.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'wrappers');symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=None
    if stock_compare:
        stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
        wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
        assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
        old=decode(subprocess.check_output([pre,'-D','--start-address=0x4aaa8','--stop-address=0x4b17a',str(wrapper)],text=True))
    edges=[(s<<63)|(e<<52)|f for s in (0,1) for e in (0,1,1023,2046,2047) for f in (0,1,1<<51,(1<<52)-1)]
    rng=random.Random(804);pairs=[(a,b) for a in edges for b in edges]+[(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(4096)];cases=0
    for name,nan in [('__nedf2',1)]:
        for a,b in pairs:
            x,y=[struct.unpack('<d',v.to_bytes(8,'little'))[0] for v in (a,b)]
            expected=nan if math.isnan(x) or math.isnan(y) else (x>y)-(x<y)
            args=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
            result=execute(code,symbols[name],bytes(20),arguments=args)
            assert result==expected&0xffffffff,(name,hex(a),hex(b),result,expected)
            assert execute(old,0x4aaa8,bytes(20),arguments=args)==result
            cases+=1
    result={'twins':twins,'stock_compared':stock_compare,'stock_sha256':IMAGE_SHA if stock_compare else None,'source_elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,'limits':['Actual decoded wrappers and nested unpack/comparator bodies; numeric ordering oracle including wrapper-specific NaN return conventions. Stock comparison mode runs original wrappers and original nested helpers. Firmware integration and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-double-inequality-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
