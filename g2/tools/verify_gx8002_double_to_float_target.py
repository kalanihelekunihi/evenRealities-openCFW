# SPDX-License-Identifier: MIT
"""Execute complete source conversion against integer nearest-even rounding."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def oracle(value):
    sign=(value>>63)<<31;exp=(value>>52)&2047;frac=value&((1<<52)-1)
    if exp==2047:return sign|0x7f800000|((frac>>29)|0x400000 if frac else 0)
    if exp==0:power=-1074;mant=frac
    else:power=exp-1023-52;mant=(1<<52)|frac
    if not mant:return sign
    high=mant.bit_length()-1+power
    quantum=max(high-23,-149);shift=quantum-power
    if shift>0:
        q,r=divmod(mant,1<<shift);half=1<<(shift-1)
        q+=r>half or (r==half and q&1)
    else:q=mant<<-shift
    if not q:return sign
    high=q.bit_length()-1+quantum
    if high>127:return sign|0x7f800000
    if high< -126:return sign|q
    if q.bit_length()>24:q>>=1
    return sign|((high+127)<<23)|(q&0x7fffff)

def verify(stock_compare=False):
    path=ROOT/'build/gx8002-double-to-float-cluster/convert.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-double-to-float-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    e=Elf32(data,'convert');entry=next(s['value'] for s in e.symbols() if s['name']=='__truncdfsf2')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    old=None
    if stock_compare:
        stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
        wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';original=Elf32(wrapper.read_bytes(),'stock')
        assert original.contents(next(s for s in original.sections if s['name']=='.data'))==stock
        old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x4acd8','--stop-address=0x4b23c',str(wrapper)],text=True))
    values=[(s<<63)|(exp<<52)|f for s in (0,1) for exp in range(2048) for f in (0,1,(1<<29)-1,1<<28,1<<51,(1<<52)-1)]
    rng=random.Random(804);values += [rng.getrandbits(64) for _ in range(4096)]
    for value in values:
        actual=execute(code,entry,bytes(20),arguments=[value&0xffffffff,value>>32],return_float=True)
        if old is not None:
            original=execute(old,0x4acd8,bytes(20),arguments=[value&0xffffffff,value>>32],return_float=True)
            assert actual==original,(hex(value),hex(actual),hex(original))
        expected=oracle(value)
        assert actual==expected,(hex(value),hex(actual),hex(expected))
    result={'stock_compared':stock_compare,'source_elf_sha256':sha(data),'cases':len(values),'source_admitted':False,'limits':['Actual converter, unpack, float constructor and pack execution versus integer rounding, including sampled NaN payloads. Stock equivalence applies only when stock_compared is true. Exhaustive equivalence and hardware qualification remain pending.']}
    (ROOT/'docs/research'/('gx8002-double-to-float-stock.json' if stock_compare else 'gx8002-double-to-float-target.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
