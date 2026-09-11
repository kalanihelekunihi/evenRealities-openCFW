# SPDX-License-Identifier: MIT
import json,subprocess
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_unpack import execute

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x13c90','--stop-address=0x13d80',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));entry=next(s['value'] for s in elf.symbols() if s['name']=='__unpack_d');new=decode((path.parent/'runtime.disassembly.txt').read_text());cases=0
    for sign in range(2):
        for exponent in range(2047):
            for fraction in (0,1,0x8000000000000,0xfffffffffffff):
                bits=(sign<<63)|(exponent<<52)|fraction
                if exponent==0 and fraction==0:wanted={0:2,4:sign}
                else:
                    significand=fraction|(1<<52) if exponent else fraction
                    shift=60-(significand.bit_length()-1);normalized=significand<<shift
                    exp=exponent-1023 if exponent else -1074+fraction.bit_length()-1
                    wanted={0:3,4:sign,8:exp&0xffffffff,12:normalized&0xffffffff,16:normalized>>32}
                if execute(old,0x13c90,bits)!=wanted or execute(new,entry,bits)!=wanted:raise ValueError(('Unpack mismatch',hex(bits)))
                cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Every finite exponent/sign tested with four fraction patterns, including zero and subnormal normalization. No NaN/Infinity claim; finite corpus, not exhaustive fraction coverage.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-double-unpack.json').write_text(json.dumps(result,indent=2)+'\n');print('Unpack cases:',result['cases'])
