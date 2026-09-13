# SPDX-License-Identifier: MIT
"""Execute candidate C permutation against independent bit-index reversal."""
import json,re,struct
from build_gx8002_backup_bit_reverse import build,ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from build_gx8002_backup_math_tables import build as tables

def verify():
    evidence=build();tables()
    e=Elf32((ROOT/'build/gx8002-backup-math-tables/tables.elf').read_bytes(),'reversal table')
    table=e.contents(next(s for s in e.sections if s['name']=='.bit_reverse'))
    code=decode((ROOT/'build/gx8002-backup-bit-reverse/reverse.disassembly.txt').read_text());cases=0
    for seed in (0,1,0x80000000,0xffffffff,0x55555555):
        values=[(seed+i*0x1020304)&0xffffffff for i in range(256)]
        memory={0x1000+i*4:v for i,v in enumerate(values)}
        r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=0x1000,r1=240,r2=0x2000);initial=r.copy();pc=0x1000f824
        for _ in range(3000):
            op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
            if op in ('addi','lsri','addu'):
                a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
                r[p[0]]=(a>>b if op=='lsri' else a+b)&0xffffffff
            elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
            elif op in ('ld.h','ld.w','st.w'):
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
                reg,base,off=m.groups();a=r[base]+int(off,0)
                if op=='ld.h':r[reg]=struct.unpack_from('<H',table,a-0x2000)[0]
                elif op=='ld.w':r[reg]=memory[a]
                else:assert a in memory;memory[a]=r[reg]
            elif op=='bnezad':
                r[p[0]]=(r[p[0]]-1)&0xffffffff
                if r[p[0]]:nxt=int(p[1],0)
            elif op=='rts':
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
                break
            else:raise ValueError((op,args))
            pc=nxt
        else:raise ValueError('bound')
        assert [memory[0x1000+i*4] for i in range(256)]==[values[int(f'{i:08b}'[::-1],2)] for i in range(256)]
        cases+=1
    report={'build':evidence,'full_permutation_cases':cases,'source_admitted':False,
            'limits':['Actual compiled candidate and generated table agree with independent 256-point permutation. Stock bloop execution is not modeled; not stock equivalence or admission.']}
    (ROOT/'docs/research/gx8002-backup-bit-reverse-candidate-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['full_permutation_cases'])
