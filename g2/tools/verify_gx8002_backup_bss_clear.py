# SPDX-License-Identifier: MIT
"""Execute the source-built backup startup BSS clearer over its real range."""
import json,re
from build_gx8002_backup_reset import build,ROOT
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();code=decode((ROOT/'build/gx8002-backup-reset/reset.disassembly.txt').read_text());cases=0
    for seed in (0,0x12345678,0xffffffff):
        r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r['r14']=0x2002fffc;initial=r.copy();pc=0x10003128;writes=[];condition=False;saved=None
        for _ in range(200000):
            op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
            if op=='push':saved={k:r[k] for k in ('r4','r5','r6')};r['r14']-=12
            elif op=='pop':r.update(saved);r['r14']+=12
            elif op=='lrw':r[p[0]]=int(p[1],0)
            elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
            elif op=='xor':r[p[0]]^=r[p[1]]
            elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&0xffffffff
            elif op in ('bt','bf'):
                if condition==(op=='bt'):nxt=int(p[0],0)
            elif op=='st.w':
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
                reg,base,offset=m.groups();writes.append((r[base]+int(offset,0),r[reg]))
            elif op=='rts':break
            else:raise AssertionError((hex(pc),op,args))
            pc=nxt
        else:raise AssertionError('bound')
        assert r==initial
        assert writes==[(a,0) for a in range(0x20017090,0x2002d79c,4)]
        cases+=1
    report={'cases':cases,'words_per_case':len(writes),'build':evidence,'limits':['Actual compiled BSS-clear instructions check every ordered zero store and register/stack restoration for the recovered fixed range. Control registers, caller behavior, physical memory and startup lifetime not modeled.']}
    (ROOT/'docs/research/gx8002-backup-bss-clear-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['words_per_case'],'BSS words checked per case')
