# SPDX-License-Identifier: MIT
"""Execute successful trim module-selection slices through the next gate call."""
import json,re,struct,subprocess
from itertools import product
from build_gx8002_stage1_clock_trim import build,ROOT,Elf32
from compare_gx8002_stage1_clock_lookup import execute as lookup
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,entry,helper,table,hcode,source,enabled):
    r={f'r{i}':0 for i in range(32)};r.update(r4=(1 if entry>=0x10000000 else 0x20001000),r5=1,r14=0x20001000);mem={0x200014c8+i:v for i,v in enumerate(table)};trace=[];pc=entry;condition=False
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    def store(a,v):
        for i in range(4):mem[a+i]=(v>>(i*8))&255
    def load(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    for a in (0xa001008c,0xa0300088):store(a,source)
    for a in (0xa0010018,0xa0300018):store(a,enabled)
    for _ in range(500):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('subi','addi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)*(1 if op=='addi' else -1))&MASK
        elif op in ('and','andn','or','nor','subu','lsl','lsr'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]
            if op in ('lsl','lsr'):assert b<32
            r[p[0]]=(a&b if op=='and' else a&~b if op=='andn' else a|b if op=='or' else ~(a|b) if op=='nor' else a-b if op=='subu' else a<<b if op=='lsl' else a>>b)&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br','bez','bnez'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=(r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='bsr':
            assert int(args,0)==helper;module=r['r0']
            if module==9:return trace
            assert module in (10,6,13);trace.append(('lookup',module))
            result,_,writes=lookup(hcode,0x10000138,module,0x1000,ids)
            for a,v in writes:store(r['r1']+a-0x1000,v)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op in ('ld.w','ld.bs','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='st.w':assert a>=0xa0000000;store(a,r[reg]);trace.append(('write',a,r[reg]))
            else:
                v=load(a,1 if op=='ld.bs' else 4);r[reg]=(v-256 if op=='ld.bs' and v&128 else v)&MASK
                if a>=0xa0000000:trace.append(('read',a,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify():
    evidence=build();out=ROOT/'build/gx8002-stage1-clock-trim';elf=Elf32((out/'trim.elf').read_bytes(),'trim');table=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    from build_gx8002_stage1_clock_tables import build as tables
    tables();hcode=decode((ROOT/'build/gx8002-stage1-clock-tables/lookup.disassembly.txt').read_text())
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x38f76','--stop-address=0x39104',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((out/'trim.disassembly.txt').read_text());cases=0
    for source,enabled in product((0,MASK,0xaaaaaaaa,0x55555555,*[1<<i for i in range(32)]),(0,MASK,0xaaaaaaaa,0x55555555)):
        a=execute(old,0x38f76,0x38a8c,table,hcode,source,enabled);b=execute(new,0x1000060e,0x10000138,table,hcode,source,enabled)
        assert a==b,(source,enabled,a,b);assert [e for e in b if e[0]=='lookup']==[('lookup',10),('lookup',6),('lookup',13)];cases+=1
    report={'cases':cases,'build':evidence,'limits':['Differential module-switch slices using compiled lookup in separate frames, fixed register samples and source tables. No independent complete switching oracle or full-function ABI proof; full trim execution pending.']}
    (ROOT/'docs/research/gx8002-stage1-trim-modules.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'trim module cases passed')
