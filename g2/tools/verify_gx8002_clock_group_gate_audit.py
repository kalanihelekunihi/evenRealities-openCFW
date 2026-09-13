# SPDX-License-Identifier: MIT
"""Execute stock grouped-gate decision against ID-based child selection."""
import json,re,subprocess
from itertools import product
from load_gx8002_clock_context import load,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode

def execute(code,module,gate,table,fixed_address=None):
    r={f'r{i}':0 for i in range(32)};r.update(r6=module,r14=0x20070000);pc=0x16c72;reads=[]
    if fixed_address is not None:r.update(r13=fixed_address,r18=0xa0000000);pc=0x10024c88
    for _ in range(40):
        if pc in (0x16ce2,0x16cb2,0x10024d3e,0x10024ca8):return pc in (0x16ce2,0x10024d3e),reads
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='addi':r[p[0]]=r[p[1]]+int(p[2],0)
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[1]]+r[p[2]])&0xffffffff
        elif op in ('ld.w','ld.bs'):
            dest,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if op=='ld.w':
                assert a in (0x20070010,0xa0000000);v=0xa0000000 if a==0x20070010 else gate
            else:
                v=table[a];v=v if v<128 else v-256
            reads.append((a,v));r[dest]=v&0xffffffff
        elif op=='lsr':
            count=r[p[2]];assert count<32;r[p[0]]=r[p[1]]>>count
        elif op=='and':r[p[0]]=r[p[1]]&r[p[2]]
        elif op=='nor':r[p[0]]=(~(r[p[0]]|r[p[1]]))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('bnez','bez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Group decision execution bound')
def verify():
    from build_gx8002_clock_module_source_fixed_candidate import build
    candidate=build();fixed=decode((ROOT/'build/gx8002-board/clock-module-source-fixed-candidate.disassembly.txt').read_text())
    table,context=load();byid={m['module']:m for m in context['modules']};p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x16c72','--stop-address=0x16cb2',str(p)],text=True));cases=0;differences=[]
    for module in (16,19,22):
        observed=[context['modules'][module+i] for i in (1,2)];intended=[byid[module+i] for i in (1,2)]
        bits=sorted(set(x['gate_all_offset'] for x in observed+intended))
        for flags in product((0,1),repeat=len(bits)):
            gate=sum(flag<<bit for bit,flag in zip(bits,flags));active,reads=execute(code,module,gate,table)
            assert active==any(not(gate>>x['gate_all_offset']&1) for x in observed)
            expected=any(not(gate>>x['gate_all_offset']&1) for x in intended)
            fixed_active,fixed_reads=execute(fixed,module,gate,table,byid[module]['address'])
            assert fixed_active==expected
            assert [a for a,v in fixed_reads if a in table]==[x['address']+5 for x in intended]
            assert [a for a,v in reads if a in table]==[x['address']+5 for x in observed]
            if active!=expected:differences.append({'module':module,'gate':hex(gate),'stock_active':active,'child_id_active':expected,'observed_child_ids':[x['module'] for x in observed],'intended_child_ids':[x['module'] for x in intended]})
            cases+=1
    assert differences and all(x['module'] in (16,19) for x in differences)
    return {'fixed_candidate':candidate,'cases':cases,'differences':differences,'context':context,'limits':['Executed stock basic block controlling grouped-gate active decision; full module-switch paths and physical glitch/timing consequences remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-group-gate-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],len(r['differences']))
