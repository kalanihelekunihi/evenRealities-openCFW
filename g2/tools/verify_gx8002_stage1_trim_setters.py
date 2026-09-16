# SPDX-License-Identifier: MIT
"""Build and compare trim setters with independently changing read values."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32,IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode


def execute(code,entry,value,reads):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=value;saved=r.copy();pc=entry;trace=[];pending=iter(reads)
    for _ in range(40):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='or':r[p[0]]=r[p[0]]|r[p[1]] if len(p)==2 else r[p[1]]|r[p[2]]
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0);assert address==0xa0010030
            if op=='ld.w':r[reg]=next(pending);trace.append(('read',r[reg]))
            else:trace.append(('write',r[reg]))
        elif op=='rts':
            assert all(r[f'r{i}']==saved[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert next(pending,None) is None
            return trace
        else:raise AssertionError((hex(pc),op,args))
        pc+=width
    raise AssertionError('execution bound')


def verify():
    out=ROOT/'build/gx8002-stage1-trim-setters';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_trim_setters.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(out/'setters.o')],check=True)
    specs=[(0x397f4,0),(0x3980c,1)]
    (out/'setters.ld').write_text('SECTIONS {\n'+''.join(f'.setter{bit} {off-0x38954+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_stage1_{off:x}) }}\n' for off,bit in specs)+'}\n')
    path=out/'setters.elf';subprocess.run([pre+'ld','-T',str(out/'setters.ld'),str(out/'setters.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trim');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    wrapped=Elf32(wrapper.read_bytes(),'stock');assert wrapped.contents(next(s for s in wrapped.sections if s['name']=='.data'))==stock
    dis=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'setters.disassembly.txt').write_text(dis);new=decode(dis);cases=0;rows=[]
    for off,bit in specs:
        sec=next(s for s in elf.sections if s['name']==f'.setter{bit}');assert sec['size']<=24
        old=decode(subprocess.check_output([pre+'objdump','-D',f'--start-address={off:#x}',f'--stop-address={off+24:#x}',str(wrapper)],text=True))
        for value,first,second in product((0,1,2,3,0x80000000,0xffffffff),range(256),(0,1,2,3,0x12345678,0xffffffff)):
            expected=[('read',first),('write',first&~(1<<bit)),('read',second),('write',second|((value&1)<<bit))]
            assert execute(old,off,value,(first,second))==expected
            assert execute(new,sec['address'],value,(first,second))==expected
            cases+=1
        rows.append({'offset':off,'bytes':sec['size'],'address':sec['address'],'envelope_bytes':24,'fits':sec['size']<=24})
    report={'cases':cases,'sections':rows,'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Finite decoded execution with independent ordered-write oracle and ABI checks. MMIO values supplied. Both setters fit; second uses one source-authored BCLRI instruction. Hardware and startup integration pending.']}
    (ROOT/'docs/research/gx8002-stage1-trim-setters.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'trim setter cases passed')
