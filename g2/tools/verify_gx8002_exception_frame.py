# SPDX-License-Identifier: MIT
"""Execute decoded exception save frame up to the deployed terminal loop."""
import json,re,subprocess
from itertools import product
from build_gx8002_exception_candidate import build,ROOT,IMAGE,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,handler,values,sp,epsr,epc,post_enable_psr):
    r={f'r{i}':v for i,v in enumerate(values)};r['r14']=sp;initial=r.copy();memory={};events=[];pc=entry;top=0x20027310;frame=top-72
    def write(address,value):
        assert address==sp-4 or frame<=address<=top
        assert address%4==0;memory[address]=value;events.append(['write',address,value])
    for _ in range(45):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='psrset':assert args=='ee';events.append(['enable_exceptions'])
        elif op in ('subi','addi','lsri'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=int(p[-1],0);r[p[0]]=(a-b if op=='subi' else a+b if op=='addi' else a>>b)&0xffffffff
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op in ('st.w','ld.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='st.w':write(address,r[reg])
            else:r[reg]=memory[address];events.append(['read',address,r[reg]])
        elif op=='stm':
            assert args=='r0-r12, (r14)'
            for i in range(13):write(r['r14']+4*i,r[f'r{i}'])
        elif op=='mfcr':
            reg,cr=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args).groups();r[reg]={0:post_enable_psr,2:epsr,4:epc}[int(cr)]
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='sextb':
            v=r[p[-1]]&255;r[p[0]]=(v if v<128 else v-256)&0xffffffff
        elif op=='bsr':
            assert int(args,0)==handler and r['r0']==frame;r['r15']=nxt;nxt=handler;events.append(['handler',frame])
        elif op=='br':
            target=int(args,0)
            if target==pc:
                assert pc==handler+8
                expected=[initial[f'r{i}'] for i in range(16)]+[epsr,epc]
                assert [memory[frame+4*i] for i in range(18)]==expected
                assert memory[top]==sp and memory[sp-4]==initial['r13']
                assert r['r3']==(((post_enable_psr>>16)&255)^128)-128 & 0xffffffff
                return {'frame':expected,'events':events,'halted_at_stock_loop':True}
            nxt=target
        else:raise ValueError((op,args))
        pc=nxt
    raise ValueError('Exception execution bound')

def verify():
    candidate=build();assert all(s['byte_exact'] for s in candidate['sections']);p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x15604','--stop-address=0x15658',str(p)],text=True));new=decode((ROOT/'build/gx8002-exception/exception.disassembly.txt').read_text());cases=0
    for sp,seed,psr in product((0x2002f7fc,0x20070000),(0,91,0xffffffff),(0,0x7f0000,0x800000,0xffffffff)):
        values=[(seed+i*0x1020304)&0xffffffff for i in range(32)];epsr=(seed^0x12345678)&0xffffffff;epc=0x102047ac
        a=execute(old,0x15610,0x15604,values,sp,epsr,epc,psr);b=execute(new,0x100235fc,0x100235f0,values,sp,epsr,epc,psr);assert a==b;cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded stock/source frame writes, saved registers, control-register values and existing terminal loop compared to independent 18-word frame oracle.','PSR after psrset supplied as stimulus, not an architectural PSR bit-effect model. Single entry with writable nonoverlapping original stack; nesting/physical exceptions unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-exception-frame.json').write_text(json.dumps(r,indent=2)+'\n');print('Exception frame cases:',r['cases'])
