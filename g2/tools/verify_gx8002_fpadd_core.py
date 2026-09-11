# SPDX-License-Identifier: MIT
import json,subprocess,random,struct,math
from execute_gx8002_double_pack_integer import execute as pack
from itertools import product
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_fpadd_core import execute

def finite_oracle(a,b):
    def signed(v):return v if v<0x80000000 else v-0x100000000
    ea,eb=signed(a[8]),signed(b[8]);fa=a[12]|(a[16]<<32);fb=b[12]|(b[16]<<32)
    exponent=max(ea,eb)
    def align(f,gap):
        if gap>=64:return 0
        return (f>>gap)|int(bool(f&((1<<gap)-1)))
    fa=align(fa,exponent-ea);fb=align(fb,exponent-eb)
    total=(-fa if a[4] else fa)+(-fb if b[4] else fb)
    sign=int(total<0);fraction=abs(total)
    if a[4]==b[4]:sign=a[4]
    while fraction and fraction<(1<<60):fraction<<=1;exponent-=1
    if fraction>=(1<<61):fraction=(fraction>>1)|(fraction&1);exponent+=1
    return {0:3,4:sign,8:exponent&0xffffffff,12:fraction&0xffffffff,16:fraction>>32}

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13364','--stop-address=0x13c90',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));entry=next(s['value'] for s in elf.symbols() if s['name']=='_fpadd_parts');new=decode((path.parent/'runtime.disassembly.txt').read_text());cases=0
    for exponent,sign,delta,cancel in product(range(-32,33),(0,1),range(32),(False,True)):
        fraction=(1<<60)+(delta<<32);a={0:3,4:sign,8:exponent&0xffffffff,12:fraction&0xffffffff,16:fraction>>32};b={**a,4:sign^int(cancel)}
        wanted={0:3,4:0 if cancel else sign,8:(exponent if cancel else exponent+1)&0xffffffff,12:0 if cancel else a[12],16:0 if cancel else a[16]}
        for code,start in ((old,0x13364),(new,entry)):
            if execute(code,start,a,b)!=(0x20040200,wanted):raise ValueError(('Add core invariant',exponent,sign,delta,cancel))
        cases+=1
    unequal=0
    for gap,sa,sb,fa,fb in product((-100,-65,-64,-63,-33,-32,-31,-1,0,1,31,32,33,63,64,65,100),(0,1),(0,1),((1<<60),(1<<60)+256,(1<<61)-256),((1<<60),(1<<60)+512,(1<<61)-256)):
        a={0:3,4:sa,8:gap&0xffffffff,12:fa&0xffffffff,16:fa>>32};b={0:3,4:sb,8:0,12:fb&0xffffffff,16:fb>>32}
        wanted=finite_oracle(a,b)
        for code,start in ((old,0x13364),(new,entry)):
            if execute(code,start,a,b)!=(0x20040200,wanted):raise ValueError(('Unequal core',gap,sa,sb,fa,fb,hex(start),execute(code,start,a,b),wanted))
        unequal+=1
    pack_entry=next(s['value'] for s in elf.symbols() if s['name']=='__pack_d')
    packed_cases=0
    rng=random.Random(0x8002);random_cases=0
    for _ in range(2048):
        fields=[]
        for side in range(2):
            fraction=((1<<52)|rng.getrandbits(52))<<8
            fields.append({0:3,4:rng.randrange(2),8:rng.randrange(-100,101)&0xffffffff,12:fraction&0xffffffff,16:fraction>>32})
        wanted=finite_oracle(*fields)
        for code,start in ((old,0x13364),(new,entry)):
            if execute(code,start,*fields)!=(0x20040200,wanted):raise ValueError(('Random finite core',fields))
        def number(f):
            exponent=f[8] if f[8]<0x80000000 else f[8]-0x100000000
            return math.ldexp(float(f[12]|(f[16]<<32)),exponent-60)*(-1 if f[4] else 1)
        expected_bits=struct.unpack('<Q',struct.pack('<d',number(fields[0])+number(fields[1])))[0]
        for program,start,packer in ((old,0x13364,0x13b00),(new,entry,pack_entry)):
            result=execute(program,start,*fields)[1]
            if pack(program,packer,result)!=expected_bits:raise ValueError(('Addition IEEE result',fields,result))
            packed_cases+=1
        random_cases+=1
    return {'packed_executions':packed_cases,'random_cases':random_cases,'unequal_cases':unequal,'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded finite core tested against integer sticky-alignment/sign/normalization oracle, including exponent boundaries and deterministic varied fractions. Random finite core outputs also feed decoded packing and match host IEEE addition. Exceptional classes and exhaustive operand coverage remain unqualified.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-fpadd-core.json').write_text(json.dumps(result,indent=2)+'\n');print('Decoded add core cases:',result['cases'])
