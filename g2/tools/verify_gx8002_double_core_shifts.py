# SPDX-License-Identifier: MIT
"""Execute relocated GCC shift helpers for defined 64-bit shift counts."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,value,count):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=value&0xffffffff,r1=value>>32,r2=count);initial=r.copy();pc=entry
    def v(x):return r[x] if x.startswith('r') else int(x,0)
    for _ in range(30):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];n=pc+w
        if op in ('mov','movi'):r[p[0]]=v(p[1])
        elif op in ('subu','subi','lsl','lsr','or'):
            a=v(p[0] if len(p)==2 else p[1]);b=v(p[-1])
            if op in ('lsl','lsr'):assert 0<=b<32
            r[p[0]]=(a-b if op in ('subu','subi') else a<<b if op=='lsl' else a>>b if op=='lsr' else a|b)&0xffffffff
        elif op in ('bez','bhz','br'):
            x=v(p[0]) if op!='br' else 0
            if op=='br' or (x==0 if op=='bez' else 0<x<0x80000000):n=int(p[-1],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            return r['r0']|(r['r1']<<32)
        else:raise ValueError((op,args))
        pc=n
    raise ValueError('bound')

def verify():
    path=ROOT/'build/gx8002-double-core-layout/core.elf';report=json.loads((ROOT/'docs/research/gx8002-double-core-layout.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'core');symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=[0,(1<<64)-1,0xaaaaaaaaaaaaaaaa,0x5555555555555555]
    values += [1<<i for i in range(64)]+[((1<<64)-1)^(1<<i) for i in range(64)]
    rng=random.Random(804);values += [rng.getrandbits(64) for _ in range(1024)];cases=0
    for name,left in [('__ashldi3',True),('__lshrdi3',False)]:
        for value in values:
            for count in range(64):
                expected=((value<<count)&((1<<64)-1)) if left else value>>count
                assert execute(code,symbols[name],value,count)==expected,(name,hex(value),count)
                cases+=1
    result={'source_elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Relocated decoded helper bodies for counts0..63, with integer oracle and callee-save checks. Counts outside C shift contract, caller count bounds and pack execution remain unqualified.']}
    (ROOT/'docs/research/gx8002-double-core-shifts.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
