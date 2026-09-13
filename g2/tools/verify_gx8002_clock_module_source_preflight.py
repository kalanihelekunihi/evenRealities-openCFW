# SPDX-License-Identifier: MIT
"""Module/source validation and module-info failure path; no MMIO success claim."""
import json,re,subprocess
from build_gx8002_clock_module_source_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
MASK=0xffffffff

def execute(code,entry,module,source):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r1=source,r14=0x20070000);initial=r.copy();saved=None;pc=entry;condition=False;calls=[]
    def signed(v):return v if v<0x80000000 else v-(1<<32)
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            end=int(re.fullmatch(r'r4-r(\d+), r15',args)[1]);regs=[f'r{i}' for i in range(4,end+1)]+['r15'];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved);assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],calls
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmphs','cmphsi','cmpnei','cmplti'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=a>=b if op.startswith('cmphs') else a!=b if op=='cmpnei' else signed(a)<b
        elif op in ('lsl','lsr','asri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);assert b<32
            r[p[0]]=((a<<b) if op=='lsl' else (a>>b) if op=='lsr' else (signed(a)>>b))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='st.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0);assert 0x2006ff80<=a<0x20070000
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0);assert target==0x10024a44
            assert r['r0']==module and 0x2006ff80<=r['r1']<0x20070000;calls.append(module)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=MASK
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x16bf4','--stop-address=0x16d84',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-module-source-candidate.disassembly.txt').read_text());cases=0
    for module in [*range(27),0x80000000,0xffffffff]:
        for source in [*range(10),0x7fffffff,0x80000000,0xffffffff]:
            signed=source if source<0x80000000 else source-(1<<32)
            accepted=module<26 and ((module in (0,1,2,6,9)) if source==2 else (module in (7,8)) if signed>2 else True)
            expected=(MASK,[module] if accepted else [])
            assert execute(old,0x16bf4,module,source)==expected,(module,source,'stock')
            assert execute(new,0x10024be0,module,source)==expected,(module,source,'source')
            cases+=1
    return {'candidate':candidate,'cases':cases,'limits':['Preflight validation and injected module-info failure only. Successful gate/source transitions, table ownership and hardware timing remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-source-preflight.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
