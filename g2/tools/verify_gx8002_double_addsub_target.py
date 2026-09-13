# SPDX-License-Identifier: MIT
"""Execute source add/subtract and dependencies against exact rational rounding."""
import json,random,struct,subprocess,math
from fractions import Fraction
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def floating(bits):return struct.unpack('<d',struct.pack('<Q',bits))[0]
def bits(value):return struct.unpack('<Q',struct.pack('<d',value))[0]
def oracle(a,b,subtract):
    x,y=floating(a),floating(b)
    exact=Fraction(x)+(-Fraction(y) if subtract else Fraction(y))
    if not exact:
        # Round-to-nearest exact cancellation is positive zero, except two negative zeros.
        return (1<<63) if a==(1<<63) and (b^((1<<63) if subtract else 0))==(1<<63) else 0
    try:return bits(float(exact))
    except OverflowError:return bits(-math.inf if exact<0 else math.inf)

def verify(placed=False,stock_compare=False,exp_cluster=False):
    stem='gx8002-exp-placed-cluster' if exp_cluster else 'gx8002-double-addsub-placed' if placed else 'gx8002-double-addsub-cluster'
    path=ROOT/'build'/stem/('exp.elf' if exp_cluster else 'addsub.elf')
    report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'source');symbols={s['name']:s['value'] for s in elf.symbols()}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=None
    if stock_compare:
        stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
        wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';original=Elf32(wrapper.read_bytes(),'stock')
        assert original.contents(next(s for s in original.sections if s['name']=='.data'))==stock
        old=decode(subprocess.check_output([pre,'-D','--start-address=0x4a460','--stop-address=0x4b0b8',str(wrapper)],text=True))
    edge=[(s<<63)|(e<<52)|f for s in (0,1) for e in (0,1,2,1022,1023,1024,2045,2046) for f in (0,1,(1<<51),(1<<52)-1)]
    pairs=[(a,b) for a in edge for b in edge]
    rng=random.Random(804)
    pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(10000)]
    pairs=[(a,b) for a,b in pairs if (a>>52)&2047!=2047 and (b>>52)&2047!=2047]
    pairs += [(a,a^(1<<63)) for a in edge]
    for subtract in (False,True):
        entry=symbols['__subdf3' if subtract else '__adddf3']
        for a,b in pairs:
            actual=execute(code,entry,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True)
            expected=oracle(a,b,subtract)
            assert actual==expected,(subtract,hex(a),hex(b),hex(actual),hex(expected))
            if old is not None:
                original=execute(old,0x4a754 if subtract else 0x4a724,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True)
                assert original==actual,(subtract,hex(a),hex(b),hex(original),hex(actual))
    result={'stock_compared':stock_compare,'stock_sha256':IMAGE_SHA if stock_compare else None,'placed':placed or exp_cluster,'exp_cluster':exp_cluster,'source_elf_sha256':sha(path.read_bytes()),'finite_cases':2*len(pairs),'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded source add/subtract, unpack, pack, shifts, and copy dependencies executed. Exact rational finite arithmetic rounded independently to binary64.', 'This finite verifier does not qualify nonfinite stock behavior, computed references, firmware integration, or hardware behavior.']}
    (ROOT/'docs/research'/('gx8002-double-addsub-target'+('-placed' if placed else '')+('-stock' if stock_compare else '')+('-exp-cluster' if exp_cluster else '')+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
