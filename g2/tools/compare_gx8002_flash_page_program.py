#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded read wrapper, with changing callback pointers and ABI clobbers."""
import contextlib,io,json,re,struct,subprocess
from build_gx8002_flash_page_program import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,delta,address,destination,length,size,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};r.update(r0=address,r1=destination,r2=length,r14=0x2002f7fc)
    initial=r.copy();saved=None;trace=[];calls=0;reads=0
    for _ in range(500000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r10, r15' or saved is not None:raise ValueError('read frame')
            saved={i:r[f'r{i}'] for i in (4,5,6,7,8,9,10,15)};r['r14']-=32
        elif op=='pop':
            if args!='r4-r10, r15' or saved is None or r['r14']!=initial['r14']-32:raise ValueError('read return')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=32
            if reads!=calls or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('read ABI')
            return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('addu','subu'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addu' else -1)*r[p[-1]])&0xffffffff
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op in ('cmphs','cmphsi'):carry=r[p[0]]>=(r[p[1]] if op=='cmphs' else int(p[1],0))
        elif op in ('br','bnez','bez','bt','bf'):
            if op=='br' or op=='bnez' and r[p[0]] or op=='bez' and not r[p[0]] or op=='bt' and carry or op=='bf' and not carry:n=int(p[-1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups()
            if r[base]+int(offset,0)==0x200264e8:
                r[reg]=size;trace.append(['size',size]);pc=n;continue
            if r[base]+int(offset,0)!=0x200264fc or reads!=calls:raise ValueError('callback read')
            value=0x10023788 if calls%2==0 else 0x10028000
            r[reg]=value;reads+=1;trace.append(['callback',value])
        elif op in ('bsr','jsr'):
            if op=='bsr':
                target=int(args,0)+delta
                if target not in (0x1002375c,0x1002374c):raise ValueError('program helper')
                trace.append(['wait' if target==0x1002375c else 'enable'])
            else:
                target=r[p[0]];wanted=0x10023788 if calls%2==0 else 0x10028000
                if target!=wanted or reads!=calls+1:raise ValueError('callback dispatch')
                trace.append(['read',target,r['r0'],r['r1'],r['r2']]);calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xa5a50000^i)&0xffffffff
        else:raise ValueError('read opcode '+op)
        pc=n
    raise ValueError('read bound')

def oracle(address,destination,length,size):
    if not length:return 0,[]
    trace=[['size',size]]
    if ((address+length)&0xffffffff)>size:return 0xffffffea,trace
    trace += [['wait'],['enable']];offset=address&255
    chunk=length if ((length+offset)&0xffffffff)<=256 else 256-offset
    done=0;i=0
    while True:
        target=0x10023788 if i%2==0 else 0x10028000
        trace += [['callback',target],['read',target,(address+done)&0xffffffff,(destination+done)&0xffffffff,chunk]]
        done+=chunk;i+=1
        if done>=length:break
        chunk=min(length-done,256);trace.append(['enable'])
    return 0,trace

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'page-program-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15c48','--stop-address=0x15cc0',str(wrapper)],text=True));new=decode((out/'page-program-linked.disassembly.txt').read_text());cases=0
    for address in (0,1,255,256,257,65535,0xffffff00,0xffffffff):
        for length in (0,1,2,255,256,257,511,512,513,1024):
            for size in (0,256,65536,0xffffffff):
                for seed in (0,0xffffffff):
                    expected=oracle(address,0xfffffff0,length,size)
                    if execute(old,0x15c48,0x1000dfec,address,0xfffffff0,length,size,seed)!=expected or execute(new,0x10023c34,0,address,0xfffffff0,length,size,seed)!=expected:raise ValueError('page mismatch')
                    cases+=1
    overflow_cases=0
    for address,length,size in [(1,0xffffffff,0),(255,0xffffff01,0),
                                (0xffffffff,0xffffffff,0xffffffff),
                                (0xffffff80,0xffffff80,0xffffffff)]:
        for seed in (0,0xffffffff):
            expected=oracle(address,0xfffffff0,length,size)
            if execute(old,0x15c48,0x1000dfec,address,0xfffffff0,length,size,seed)!=expected or execute(new,0x10023c34,0,address,0xfffffff0,length,size,seed)!=expected:raise ValueError('page overflow')
            overflow_cases+=1
    report={'build':evidence,'cases':cases,'overflow_cases':overflow_cases,'source_admitted':False,'limits':['Callbacks modeled with replacement and clobbers; physical buffer validity unqualified.', 'Eight wrapped length-plus-offset cases qualified; no physical write operation performed.']}
    (ROOT/'docs/research/gx8002-flash-page-program-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
