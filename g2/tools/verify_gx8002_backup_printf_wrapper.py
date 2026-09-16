# SPDX-License-Identifier: MIT
"""Check decoded variadic wrapper register/stack ABI against stock."""
import itertools,json,re,subprocess
from build_gx8002_backup_printf_wrapper import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,delta,fmt,values,result,seed):
    r={f'r{i}':(seed+i)&MASK for i in range(32)};sp=0x20070000;r.update(r0=fmt,r1=values[0],r2=values[1],r3=values[2],r14=sp);initial=r.copy();memory={sp+4*i:v for i,v in enumerate(values[3:])};pc=entry;calls=[]
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));assert r['r0']==result
            assert all(memory[sp+4*i]==v for i,v in enumerate(values[3:]));return calls
        elif op=='push':assert args=='r15';r['r14']-=4;memory[r['r14']]=r['r15']
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+(b if op=='addi' else -b))&MASK
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if op=='ld.w':r[reg]=memory[a]
            else:memory[a]=r[reg]
        elif op=='bsr':
            assert int(args,0)+delta==0x10008e20
            cursor=memory[r['r14']];assert r['r1']==r['r14']+4
            actual=tuple(memory[cursor+4*i] for i in range(len(values)))
            calls.append((r['r0'],r['r2'],r['r3'],actual))
            memory[r['r1']]=0xdeadbeef # formatter may use its local output buffer
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x42274','--stop-address=0x422a8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-printf/wrapper.disassembly.txt').read_text());cases=0
    for fmt,seed,result,length in itertools.product((0x100131ac,0x10013270,0x20010000),(0,0xa5a5a5a5,MASK),(0,1,128,MASK),(3,4,8,16)):
        values=tuple((seed+i*0x1020304)&MASK for i in range(length));expected=[(0x10009924,MASK,fmt,values)]
        assert execute(old,0x42274,0x10000000-0x38940,fmt,values,result,seed)==execute(new,0x10009934,0,fmt,values,result,seed)==expected
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Register and stack varargs, formatter arguments, local buffer, returned result, caller stack and preserved registers'],'limits':['Formatter modeled; format parsing, alignment-sensitive vararg types and nested output execution pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-printf-wrapper-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
