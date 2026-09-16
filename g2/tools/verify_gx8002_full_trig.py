# SPDX-License-Identifier: MIT
"""Execute complete public trig source against high precision reduced Taylor oracle."""
import json,subprocess,math,random
from decimal import Decimal,localcontext
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_reducer_accuracy import oracle
from verify_gx8002_double_pack_target import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_addsub_target import bits


def verify(expanded=False,placed_wrappers=False):
    stem='gx8002-public-trig-placed' if placed_wrappers else 'gx8002-full-trig-closure'
    path=ROOT/'build'/stem/'trig.elf';report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'trig');code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    inputs=json.loads((ROOT/'docs/research/gx8002-reducer-execution.json').read_text())['cases'];rows=[]
    if expanded:
        values=[(sign<<63)|(exponent<<52)|fraction for sign in (0,1) for exponent in (0,1,2,995,1022,1023,1042,1043,1100,1500,2000,2046) for fraction in (0,1,(1<<52)-1)]
        for multiple in (1,2,3,4,10,32,100,1024,2**19):
            boundary=multiple*(math.pi/2)
            for x in (math.nextafter(boundary,0.0),boundary,math.nextafter(boundary,math.inf)):
                values.extend((bits(x),bits(-x)))
        rng=random.Random(8042026)
        values += [rng.getrandbits(64) for _ in range(100)]
        values=sorted(set(values))
        inputs=[{'input':hex(v),'high':'0x0','low':'0x0'} for v in values if (v>>52)&2047!=2047]
    for row in inputs:
        value=int(row['input'],16);q,r,_=oracle(row,440)
        with localcontext() as context:
            context.prec=110
            sine=r;cosine=Decimal(1);st=r;ct=Decimal(1)
            for k in range(1,75):
                st *= -r*r/((2*k)*(2*k+1));sine+=st
                ct *= -r*r/((2*k-1)*(2*k));cosine+=ct
            expected_sin=[sine,cosine,-sine,-cosine][q%4]
            expected_cos=[cosine,-sine,-cosine,sine][q%4]
        for name,entry,reference in [('sin',0x484f0+0x10003000-0x3b940 if placed_wrappers else 0x1001a000,expected_sin),('cos',0x48454+0x10003000-0x3b940 if placed_wrappers else 0x1001a100,expected_cos)]:
            actual=execute(code,entry,bytes(20),arguments=[value&0xffffffff,value>>32],readonly=memory,return_pair=True,max_steps=100000,stack_bytes=2048)
            expected=bits(float(reference))
            if name=='sin' and value&((1<<63)-1)==0:expected=value
            ordered=lambda v: (~v&((1<<64)-1)) if v>>63 else v|(1<<63)
            error=abs(ordered(actual)-ordered(expected))
            rows.append({'function':name,'input':row['input'],'actual':hex(actual),'reference':hex(expected),'ulp_error':error})
    result={'placed_wrappers':placed_wrappers,'expanded':expanded,'source_elf_sha256':report['elf_sha256'],'cases':len(rows),'maximum_ulp_error':max(r['ulp_error'] for r in rows),'errors_over_one_ulp':[r for r in rows if r['ulp_error']>1],'results':rows,'source_admitted':False,'limits':['Full decoded public functions, reducer and kernel source with optional exponent-boundary, near-multiple-of-pi/2 and deterministic random inputs. Independent 440-digit reduction and 110-digit Taylor reference. Sampling is not full-domain correctness; expanded coverage, firmware placement and hardware pending.']}
    (ROOT/'docs/research'/(('gx8002-public-trig-placed' if placed_wrappers else 'gx8002-full-trig')+('-expanded' if expanded else '-execution')+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],r['maximum_ulp_error'],r['errors_over_one_ulp'])
