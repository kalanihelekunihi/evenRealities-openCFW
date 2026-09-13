# SPDX-License-Identifier: MIT
"""Runner uses actual source model-buffer offsets and feature dimension."""
import json,subprocess
from verify_gx8002_kws_run import verify as qualify,expected,ROOT,sha,decode,Elf32
from execute_gx8002_kws_run import execute

def leaf(code,value):
    pc=0
    for _ in range(5):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='rts':return value
        if op=='movi':assert p[0]=='r0';value=int(p[1],0)
        elif op in ('addi','lsli'):
            assert p[:2]==['r0','r0'];n=int(p[2],0);value=(value+n if op=='addi' else value<<n)&0xffffffff
        else:raise ValueError(op)
        pc+=width
    raise ValueError('leaf bound')

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/model/runtime_gx8002_model_interface.o';elf=Elf32(path.read_bytes(),'model');report=json.loads((ROOT/'docs/research/gx8002-model-interface-verification.json').read_text());pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={}
    for name in ('LvpCTCModelGetSnpuFeatsBuffer','LvpCTCModelGetSnpuStateBuffer','LvpCTCModelGetSnpuFeatsDim'):
        row=next(r for r in report['functions'] if r['symbol']==name);section=next(s for s in elf.sections if s['name']=='.text.'+name)
        assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
        codes[name]=decode(subprocess.check_output([pre,'-d','-j',section['name'],str(path)],text=True))
    code=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text());cases=0;calls=0
    for stride in (0,1,12,13):
      for index in (0,1,0xffffffff):
       for seed in (0,91):
        def helper(name,value):
            nonlocal calls
            result=leaf(codes[name],value);calls+=1;return result
        args=(0x20030000,index,stride,0x20052000,0x20054410,520,seed)
        actual=execute(code,0x100260e4,evidence['candidate']['bindings'],*args,model_hook=helper)
        assert actual==expected(*args);cases+=1
    assert cases==24 and calls==72
    return {'evidence':evidence,'model_buffer_cases':cases,'decoded_model_calls':calls,'model_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual authenticated model getters drive feature pointer, RNN state +1040 and 520 dimensions. Context/task initialization and SNPU submission still modeled; no model graph/weights or physical execution qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-model-buffers.json').write_text(json.dumps(r,indent=2)+'\n');print(r['model_buffer_cases'])
