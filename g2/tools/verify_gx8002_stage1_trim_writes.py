# SPDX-License-Identifier: MIT
"""Compare successful trim/source write slices with changing MMIO reads."""
import json,re,struct,subprocess
from itertools import product
from build_gx8002_stage1_clock_trim import build,ROOT,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,start,stop,base_reg,trim,table,reads):
    r={f'r{i}':0 for i in range(32)};r[base_reg]=0x20001000;memory={};trace=[];pending=iter(reads)
    for base,data in ((0x20001008,struct.pack('<3I',*trim)),(0x20001668,table)):
        memory.update({base+i:v for i,v in enumerate(data)})
    pc=start
    for _ in range(100):
        if pc==stop:
            assert next(pending,None) is None
            return trace
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bseti':r[p[0]]=r[p[0] if len(p)==2 else p[1]]|(1<<int(p[-1],0))
        elif op=='addi':r[p[0]]=r[p[1]]+int(p[2],0)
        elif op in ('lsl','and','andn','or','nor'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]
            if op=='lsl':assert b<32
            r[p[0]]=(a<<b if op=='lsl' else a&b if op=='and' else a&~b if op=='andn' else a|b if op=='or' else ~(a|b))&MASK
        elif op in ('ld.w','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='st.w':assert address in (0xa0004024,0xa0004028,0xa000402c,0xa001008c);trace.append(('write',address,r[reg]))
            elif address==0xa001008c:r[reg]=next(pending);trace.append(('read',address,r[reg]))
            else:r[reg]=sum(memory[address+i]<<(8*i) for i in range(4 if op=='ld.w' else 1))
        else:raise AssertionError((pc,op,args))
        pc+=width
    raise AssertionError('bound')


def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x38ef2','--stop-address=0x38f76',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    out=ROOT/'build/gx8002-stage1-clock-trim';new=decode((out/'trim.disassembly.txt').read_text());elf=Elf32((out/'trim.elf').read_bytes(),'trim')
    original=b''.join(elf.contents(next(s for s in elf.sections if s['name']==name)) for name in ('.data.low','.data.high'))
    cases=0
    for trim,reads,selections in product(((0,0,0),(1,2,3),(MASK,0x12345678,0x80000000)),((0,0,0,0),(MASK,)*4,(0xaaaaaaaa,0x55555555,0x12345678,0x87654321)),range(16)):
        table=bytearray(original)
        for i in range(4):table[i*8+4]=(selections>>i)&1
        expected=[('write',0xa0004024,trim[0]),('write',0xa0004028,trim[1])]
        for i in range(4):
            if i==2:expected.append(('write',0xa000402c,trim[2]))
            bit=struct.unpack_from('<I',table,i*8)[0];value=table[i*8+4]
            expected += [('read',0xa001008c,reads[i]),('write',0xa001008c,(reads[i]&~(1<<bit))|(value<<bit))]
        assert execute(old,0x38ef2,0x38f76,'r5',trim,table,reads)==expected
        assert execute(new,0x1000058e,0x1000060e,'r4',trim,table,reads)==expected
        cases+=1
    report={'cases':cases,'build':evidence,'limits':['Successful oscillator/source-write slices only; supplied trim words, static table mutations and independent MMIO reads. Full trim control flow, module switching and ABI remain pending.']}
    (ROOT/'docs/research/gx8002-stage1-trim-writes.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'trim write cases passed')
