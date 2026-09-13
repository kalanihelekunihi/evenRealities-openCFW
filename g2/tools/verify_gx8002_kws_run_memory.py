# SPDX-License-Identifier: MIT
"""Execute reconstructed buffer helpers within decoded KWS window preparation."""
import json,subprocess
from verify_gx8002_kws_run import verify as qualify,ROOT,sha,decode,Elf32,expected
from execute_gx8002_kws_run import execute
from verify_gx8002_memmove import execute as move
from verify_gx8002_memcpy_source import execute as copy

def verify():
    evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={};hashes={}
    for kind,artifact,reportname in (('memmove','memmove.elf','gx8002-memmove-source-verification.json'),('memcpy','copy.o','gx8002-memcpy-source-verification.json')):
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact;elf=Elf32(path.read_bytes(),kind);report=json.loads((ROOT/'docs/research'/reportname).read_text())
        for row in report.get('functions',[report]):
            section=next(s for s in elf.sections if s['name']==row.get('section_name','.text.'+row['symbol']))
            assert sha(elf.contents(section))==row['compiled_sha256']
        codes[kind]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));hashes[kind]=sha(path.read_bytes())
    code=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text());cases=0;calls=0
    for stride in range(14):
      for seed in (0,91,255):
        memory={a+i:(i*37+seed+(a>>12))&255 for a in (0x20040000,0x20041000,0x20050000) for i in range(-16,1056)};before=memory.copy()
        old=bytes(memory[0x20040000+i] for i in range(1040));incoming=bytes(memory[0x20041000+i] for i in range(stride*80));window=old[stride*80:]+incoming
        wanted=memory.copy()
        for base in (0x20040000,0x20050000):
            for i,value in enumerate(window):wanted[base+i]=value
        def helper(name,destination,source,count):
            nonlocal calls
            calls+=1
            if name=='memmove':result,_=move(codes[name],0x10206c44,memory,destination,source,count,codes['memcpy'],0)
            else:result,_=copy(codes[name],memory,destination,source,count,start=0)
            return result
        args=(0x20030000,1,stride,0x20058000,0x20059000,520,seed)
        result=execute(code,0x100260e4,evidence['candidate']['bindings'],*args,memory_hook=helper)
        assert result==expected(*args) and memory==wanted
        cases+=1
    assert cases==42 and calls==126
    return {'evidence':evidence,'memory_cases':cases,'decoded_buffer_helper_calls':calls,'helper_hashes':hashes,'source_admitted':False,'limits':['Actual decoded reconstructed memmove/memcpy update shared feature/input RAM; complete memory equals independent sliding-window result including guards. Valid strides 0..13 only; cache/peripheral effects and other helpers modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-memory.json').write_text(json.dumps(r,indent=2)+'\n');print(r['memory_cases'])
