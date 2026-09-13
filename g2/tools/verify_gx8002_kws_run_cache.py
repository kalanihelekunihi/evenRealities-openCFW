# SPDX-License-Identifier: MIT
"""Decoded KWS preparation calls authenticated source cache-range routines."""
import json,subprocess
from itertools import product
from verify_gx8002_kws_run_memory import verify as qualify,ROOT,sha,decode,Elf32,expected
from execute_gx8002_kws_run import execute
from verify_gx8002_dcache_invalid_range import execute as invalidate
from verify_gx8002_dcache_clean_range import execute as clean

def verify():
    evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={};hashes={}
    for kind,reportname in (('dcache-invalid-range','gx8002-dcache-invalid-range-source-verification.json'),('dcache-clean-range','gx8002-dcache-clean-range-verification.json')):
        path=ROOT/f'build/gx8002-source-candidate/{kind}/{kind}.elf';elf=Elf32(path.read_bytes(),kind);report=json.loads((ROOT/'docs/research'/reportname).read_text())
        for row in report['functions']:
            section=next(s for s in elf.sections if s['name']==row.get('section_name','.text.'+row['symbol']));assert sha(elf.contents(section))==row['compiled_sha256']
        codes[kind]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));hashes[kind]=sha(path.read_bytes())
    runner=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text());bindings=json.loads((ROOT/'docs/research/gx8002-kws-run-candidate.json').read_text())['bindings'];cases=0;calls=0
    for stride,pointer,dimension in product((0,1,12,13),(0x20058000,0x2005800f,0xfffffff0),(0,1,520,0x80000000)):
        traces=[]
        def cache(name,address,length):
            nonlocal calls
            invalid=name=='gx_dcache_invalid_range';kind='dcache-invalid-range' if invalid else 'dcache-clean-range'
            trace,complete=(invalidate if invalid else clean)(codes[kind],0x10025608 if invalid else 0x10025664,address,length,91)
            signed=length if length<0x80000000 else length-(1<<32)
            wanted=[(0xe000f004,(((address&0xfffffff0)|(2 if invalid else 8))+i*16)&0xffffffff) for i in range((max(0,signed)+15)//16)]
            assert complete and trace==wanted;traces.append(trace);calls+=1
        args=(0x20030000,1,stride,pointer,0x20059000,dimension,91)
        result=execute(runner,0x100260e4,bindings,*args,cache_hook=cache)
        assert result==expected(*args) and len(traces)==3;cases+=1
    assert cases==48 and calls==144
    return {'evidence':evidence,'cache_cases':cases,'decoded_cache_calls':calls,'helper_hashes':hashes,'source_admitted':False,'limits':['Actual decoded cache routines driven by runner arguments; ordered cache-port writes checked independently. Memory helpers modeled in this check, decoded separately in prerequisite. Hardware coherence/timing and model/context helpers remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-cache.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cache_cases'])
