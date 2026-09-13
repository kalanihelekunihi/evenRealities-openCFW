# SPDX-License-Identifier: MIT
"""Execute upstream positive finite square root against integer midpoint rounding."""
import json,math,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_scalbnf_finite import parts

def oracle(bits):
    if bits&0x7fffffff==0:return bits
    sign,mant,power=parts(bits);assert sign==0
    high=mant.bit_length()-1+power;quantum=high//2-23
    shift=power-2*quantum;assert shift>=0
    radicand=mant<<shift;q=math.isqrt(radicand)
    midpoint=(2*q+1)**2;scaled=4*radicand
    q+=scaled>midpoint or (scaled==midpoint and q&1)
    high=q.bit_length()-1+quantum
    if q.bit_length()>24:q>>=1
    return ((high+127)<<23)|(q&0x7fffff)

def verify(placed=False):
    path=ROOT/('build/gx8002-sqrtf-placed/sqrt.elf' if placed else 'build/gx8002-powf-source-closure/power.elf');data=path.read_bytes()
    report=json.loads((ROOT/('docs/research/gx8002-sqrtf-placed.json' if placed else 'docs/research/gx8002-powf-source-closure.json')).read_text());assert sha(data)==report['elf_sha256']
    e=Elf32(data,'sqrt');entry=next(s['value'] for s in e.symbols() if s['name']=='__ieee754_sqrtf')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';stock_elf=Elf32(wrapper.read_bytes(),'stock')
    assert stock_elf.contents(next(s for s in stock_elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4950c','--stop-address=0x495e4',str(wrapper)],text=True))
    values=[(exp<<23)|f for exp in range(255) for f in (0,1,2,0x3fffff,0x400000,0x7ffffe,0x7fffff)]+[0x80000000]
    rng=random.Random(6436);values += [rng.randrange(0x7f800000) for _ in range(10000)]
    for bits in values:
        actual=execute(code,entry,bytes(20),float_arguments=[bits],return_float=True)
        original=execute(old,0x4950c,bytes(20),float_arguments=[bits],return_float=True)
        expected=oracle(bits);assert actual==original==expected,(hex(bits),hex(actual),hex(original),hex(expected))
    result={'placed':placed,'elf_sha256':sha(data),'entry':entry,'stock_sha256':IMAGE_SHA,'stock_entry':0x4950c,'stock_region_end':0x495e4,'cases':len(values),'source_admitted':False,'limits':['Actual compiled source and stock positive-finite and signed-zero execution versus exact integer midpoint rounding. Negative/nonfinite semantics, FP flags/modes, firmware integration and hardware pending.']}
    (ROOT/('docs/research/gx8002-sqrtf-placed-positive.json' if placed else 'docs/research/gx8002-sqrtf-positive-source.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
