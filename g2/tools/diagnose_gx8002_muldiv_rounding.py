# SPDX-License-Identifier: MIT
"""Capture actual pre-pack fields for retained exact-rounding failures."""
import json,struct,subprocess
from fractions import Fraction
from verify_gx8002_double_addsub_target import floating
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_pack_rounding import oracle

def diagnose():
    p=ROOT/'build/gx8002-double-muldiv-cluster/muldiv.elf';report=json.loads((ROOT/'docs/research/gx8002-double-muldiv-cluster.json').read_text());assert sha(p.read_bytes())==report['elf_sha256']
    e=Elf32(p.read_bytes(),'source');symbols={s['name']:s['value'] for s in e.symbols()}
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(p)],text=True))
    records=[]
    for name,a,b,expected in [('mul',0xfffffffffffff,0x3fefffffffffffff,0xfffffffffffff),('div',0x18000000000000,0x4000000000000001,0xbffffffffffff)]:
        trace={symbols['__pack_d']:[]}
        actual=execute(code,symbols['__'+name+'df3'],bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,trace=trace)
        states=trace[symbols['__pack_d']];assert len(states)==1
        state=states[0];ptr=state['registers']['r0'];parts=bytes(state['memory'][ptr+i] for i in range(20))
        cls,sign,exponent,fraction=struct.unpack('<IIiQ',parts)
        packed=oracle(sign,exponent,fraction);assert cls==3 and actual==packed and actual!=expected
        x,y=Fraction(floating(a)),Fraction(floating(b));exact=x*y if name=='mul' else x/y
        scaled=exact*(1<<(60-exponent));q,remainder=divmod(scaled.numerator,scaled.denominator)
        assert remainder
        if name=='mul':assert fraction==q and q&255==0
        else:assert q&255==128 and not q&256 and fraction==(q+128)&~255
        records.append({'exact_scaled_floor':hex(q),'nonzero_remainder':True,'operation':name,'a':hex(a),'b':hex(b),'expected':hex(expected),'actual':hex(actual),'pre_pack_parts':parts.hex(),'exponent':exponent,'fraction':hex(fraction),'packer_agrees_with_parts_oracle':True})
    result={'source_elf_sha256':sha(p.read_bytes()),'failures':records,'limits':['Instrumentation observes actual machine state without replacing helpers. Confirms discrepancy exists in parts delivered to pack; arithmetic algorithm versus earlier instruction modeling still needs resolution.']}
    (ROOT/'docs/research/gx8002-muldiv-rounding-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(diagnose())
