# SPDX-License-Identifier: MIT
"""Execute linked exponential with actual source arithmetic against Decimal."""
import json,subprocess,math,random
from decimal import Decimal,localcontext
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import bits

def verify(signed_constants=False,helpers=False,placed=False):
    stem='gx8002-exp-placed-cluster' if placed else 'gx8002-exp-helper-cluster' if helpers else 'gx8002-exp-signed-cluster' if signed_constants else 'gx8002-exp-corrected-cluster'
    path=ROOT/'build'/stem/'exp.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text());assert sha(data)==report['elf_sha256']
    elf=Elf32(data,'exp');symbols={s['name']:s['value'] for s in elf.symbols()}
    readonly={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] for i,b in enumerate(elf.contents(s))}
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    values=[-745.,-744.,-710.,-709.,-100.,-10.,-1.,-0.5,-2**-28,-0.,0.,2**-28,0.5,1.,10.,100.,709.,710.]+[i/8 for i in range(-64,65)]
    for boundary in (-745.1332191019411,709.782712893384,-708.3964185322641,-2**-28,2**-28):
        values += [math.nextafter(boundary,-math.inf),boundary,math.nextafter(boundary,math.inf)]
    for k in range(-1000,1001,25):
        boundary=(k+0.5)*math.log(2)
        values += [math.nextafter(boundary,-math.inf),boundary,math.nextafter(boundary,math.inf)]
    rng=random.Random(804);values += [rng.uniform(-746,710) for _ in range(500)]
    maximum=0
    for value in values:
        a=bits(value)
        actual=execute(code,symbols['open_cfw_gx8002_backup_exp'],bytes(20),arguments=[a&0xffffffff,a>>32],return_pair=True,readonly=readonly,max_steps=30000)
        with localcontext() as ctx:
            ctx.prec=110;expected=bits(float(Decimal.from_float(value).exp()))
        assert (actual==0x7ff0000000000000)==(expected==0x7ff0000000000000),(value,hex(actual),hex(expected))
        distance=abs(actual-expected);assert distance<=1,(value,hex(actual),hex(expected),distance)
        maximum=max(maximum,distance)
    payloads=[1,(1<<52)-1]+[1<<n for n in range(52)]+[rng.getrandbits(52)|1 for _ in range(256)]
    special=[(sign<<63)|0x7ff0000000000000|p for sign in (0,1) for p in payloads]+[0x7ff0000000000000,0xfff0000000000000]
    for a in special:
        actual=execute(code,symbols['open_cfw_gx8002_backup_exp'],bytes(20),arguments=[a&0xffffffff,a>>32],return_pair=True,readonly=readonly,max_steps=30000)
        expected=a|(1<<51) if a&((1<<52)-1) else (0 if a>>63 else a)
        assert actual==expected,(hex(a),hex(actual),hex(expected))
    result={'special_cases':len(special),'overflow_classification_exact':True,'source_elf_sha256':sha(data),'finite_cases':len(values),'max_ulp':maximum,'source_admitted':False,'limits':['Full decoded source exponential and arithmetic dependencies; Decimal 110-digit oracle. Sample includes overflow/underflow neighbors, range-reduction boundaries and seeded inputs. NaNs quiet with payload/sign preserved; signed infinities checked exactly. Exhaustive rounding, stock comparison, placement and hardware remain pending.']}
    (ROOT/'docs/research'/('gx8002-exp-placed-target.json' if placed else 'gx8002-exp-helper-target.json' if helpers else 'gx8002-exp-signed-target.json' if signed_constants else 'gx8002-exp-corrected-target.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
