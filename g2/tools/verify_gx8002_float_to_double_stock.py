# SPDX-License-Identifier: MIT
"""Execute full widening source and original chain against binary representation math."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def oracle(bits):
    sign=(bits>>31)<<63;exponent=(bits>>23)&255;fraction=bits&0x7fffff
    if exponent==255:return sign|(2047<<52)|(((fraction<<29)|(1<<51)) if fraction else 0)
    if exponent:return sign|((exponent-127+1023)<<52)|(fraction<<29)
    if not fraction:return sign
    top=fraction.bit_length()-1
    return sign|((top-149+1023)<<52)|((fraction-(1<<top))<<(52-top))

def verify():
    path=ROOT/'build/gx8002-float-to-double-cluster/widen.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-float-to-double-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old={}
    for start,end in [(0x4a434,0x4a460),(0x4aca8,0x4acd8),(0x4adb0,0x4b0b8)]:
        old.update(decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True)))
    values=[(sign<<31)|(exp<<23)|f for sign in (0,1) for exp in range(256) for f in (0,1,2,0x3fffff,0x400000,0x7ffffe,0x7fffff)]
    rng=random.Random(3264);values += [rng.getrandbits(32) for _ in range(10000)]
    for value in values:
        actual=execute(code,0x4a434-0x3b940+0x10003000,bytes(20),float_arguments=[value],return_pair=True)
        original=execute(old,0x4a434,bytes(20),float_arguments=[value],return_pair=True)
        assert actual==original==oracle(value),(hex(value),hex(actual),hex(original),hex(oracle(value)))
    result={'source_elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(values),'source_admitted':False,'limits':['Actual source/stock widening, unpack and double construction/packing. Sampled representation and NaN payload equivalence; integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-float-to-double-stock.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
