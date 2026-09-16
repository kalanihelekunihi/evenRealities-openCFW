# SPDX-License-Identifier: MIT
"""Decoded backup context selection and ordered word-store verification."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_get_out_buffer import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,index,memory,seed):
    r={f'r{i}':(seed+i)&MASK for i in range(32)};r.update(r0=index);initial=r.copy();trace=[]
    for _ in range(40):
        op,args,width=code[entry];p=[x.strip() for x in args.split(',')]
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('andi','mult','addi','addu','lsli','subu','divu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a*b if op=='mult' else a<<b if op=='lsli' else a-b if op=='subu' else a//b if op=='divu' else a+b)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bez':
            if r[p[0]]==0:entry=int(p[1],0);continue
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='ld.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);r[reg]=memory[address];trace.append(('read',address,r[reg]))
        elif op=='st.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();trace.append(('write',(r[base]+int(off,0))&MASK,r[reg]))
        elif op=='str.w':
            reg,base,index_reg,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();trace.append(((r[base]+(r[index_reg]<<int(shift)))&MASK,r[reg]))
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],trace
        else:raise AssertionError((op,args))
        entry+=width
    raise AssertionError('Instruction bound')

def verify():
    candidate=build();out=ROOT/'build/gx8002-backup-get-out-buffer'
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x42790','--stop-address=0x427cc',str(wrapper)],text=True));new=decode((out/'index.disassembly.txt').read_text());cases=0
    for index,channels,frames,total,base in product((0,1,3,4,255,MASK),(0,1,2,4),(1,3,4),(4,12,24),(0,0x2001a380,0xfffffff0)):
        context_bytes=((channels<<9)*frames)&MASK;channel_bytes=((channels<<9)*total)&MASK
        if channels and (not context_bytes or channel_bytes//context_bytes==0):continue
        memory={0x20017718:channels,0x20017724:frames,0x20017734:total,0x20017748:base}
        a=execute(old,0x42790,index,memory,0);b=execute(new,0x10009e50,index,memory,0)
        wanted=0 if not channels else (base+(index%(channel_bytes//context_bytes))*context_bytes)&MASK
        assert a==b and a[0]==wanted,(index,channels,frames,total,base,a,b)
        assert [x for x in a[1] if x[0]=='write']==[('write',0x20017780,0x20017700),('write',0x20017790,0x200177a0)]
        cases+=1
    result={'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Ordered field reads and context writes plus arithmetic return checked for stable valid configurations. Zero output preserves context initialization.', 'Nonzero derived divisors required; hardware and full input domain unqualified. Fit reported separately; no source admission.']}
    (ROOT/'docs/research/gx8002-backup-get-out-buffer-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['cases'])
