#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded range erase with ordered helper arguments; no hardware writes."""
import contextlib,io,json,re,struct,subprocess
from build_gx8002_flash_erase import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,delta,address,length,size,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};r['r0']=address;r['r1']=length;r['r14']=0x2002f7fc
    initial=r.copy();saved=None;trace=[];frame=0
    def finish():
        if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,18))):raise ValueError('erase ABI')
        return r['r0'],trace,frame
    for _ in range(4000000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            names={'r4-r8, r15':[4,5,6,7,8,15],'r4-r5, r15':[4,5,15]}.get(args)
            if names is None or saved is not None:raise ValueError('erase frame')
            saved={i:r[f'r{i}'] for i in names};frame=len(names)*4;r['r14']-=frame
        elif op=='pop':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('erase pop')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=frame;return finish()
        elif op=='rts':return finish()
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&0xffffffff
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op in ('addu','subu','addi','subi','and','andni','lsli','min.u32','max.u32'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subu','subi') else a&b if op=='and' else a&~b if op=='andni' else a<<b if op=='lsli' else min(a,b) if op=='min.u32' else max(a,b) if op=='max.u32' else a+b)&0xffffffff
        elif op in ('cmphs','cmphsi'):carry=r[p[0]]>=(r[p[1]] if op=='cmphs' else int(p[1],0))
        elif op in ('br','bt','bf','bnez'):
            if op=='br' or op=='bnez' and r[p[0]] or op=='bt' and carry or op=='bf' and not carry:n=int(p[-1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups()
            if r[base]+int(off,0)!=0x200264e8:raise ValueError('erase read')
            r[reg]=size;trace.append(['size',size])
        elif op=='bsr':
            target=int(args,0)+delta
            if target in (0x1002375c,0x1002374c):trace.append(['call',target])
            elif target==0x10023b8c:trace.append(['encode',r['r0'],r['r1'],r['r2']])
            elif target==0x100236dc:trace.append(['command',r['r0'],r['r1'],r['r2']])
            else:raise ValueError('erase helper')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xa5a50000^i)&0xffffffff
        else:raise ValueError('erase opcode '+op)
        pc=n
    raise ValueError('erase execution bound')

def oracle(address,length,size):
    trace=[['size',size]]
    if address>=size:return 0xffffffea,trace
    end=min(size,(address+length)&0xffffffff);address&=0xfffff000;remaining=(end-address)&0xffffffff
    for _ in range(70000):
        if not remaining:return 0,trace
        rounded=max(remaining,4096);step=65536 if address%65536==0 and rounded>=65536 else 4096
        trace += [['call',0x1002375c],['call',0x1002374c],['encode',0x200264ec,address,0x200264f4],['command',0xd8 if step==65536 else 0x20,0x200264f5,3],['call',0x1002375c]]
        address=(address+step)&0xffffffff;remaining=rounded-step
    raise ValueError('oracle long wrap case')

def execute_chip(code,pc,delta,size,result):
    r={f'r{i}':0x12340000+i for i in range(32)};initial=r.copy();saved=None;calls=0;reads=0
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('chip frame')
            saved=r['r15'];r['r14']-=4
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);dst,base,off=m.groups()
            if r[base]+int(off,0)!=0x200264e8 or reads:raise ValueError('chip size read')
            reads+=1;r[dst]=size
        elif op=='bsr':
            if int(args,0)+delta!=0x10023d58 or calls or reads!=1 or (r['r0'],r['r1'])!=(0,size):raise ValueError('chip arguments')
            calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xa5a50000+i
            r['r0']=result
        elif op=='pop':
            if args!='r15' or saved is None or r['r14']!=initial['r14']-4 or calls!=1:raise ValueError('chip return')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('chip ABI')
            return r['r0']
        else:raise ValueError('chip opcode')
        pc+=width
    raise ValueError('chip bound')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'erase-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15d6c','--stop-address=0x15e14',str(wrapper)],text=True));new=decode((out/'erase-linked.disassembly.txt').read_text());cases=0
    for size in (0,1,4095,4096,65536,0x3f000,0x7f000,0xff000):
        for address in (0,1,4095,4096,65535,65536,max(0,size-1),size,0xffffffff):
            for length in (0,1,4095,4096,65535,65536,65537,0x100000):
                expected=oracle(address,length,size)
                for seed in (0,0xffffffff):
                    for code,entry,delta,wanted in ((old,0x15d6c,0x1000dfec,24),(new,0x10023d58,0,0 if address>=size else 12)):
                        result,trace,frame=execute(code,entry,delta,address,length,size,seed)
                        if (result,trace)!=expected or frame!=wanted:raise ValueError('erase mismatch')
                    cases+=1
    chip_old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15e14','--stop-address=0x15e28',str(wrapper)],text=True))
    chip_cases=0
    for size in (0,1,4096,0x3f000,0x7f000,0xff000,0x80000000,0xffffffff):
        for result in (0,1,0xffffffea,0xffffffff):
            if execute_chip(chip_old,0x15e14,0x1000dfec,size,result)!=result or execute_chip(new,0x10023e00,0,size,result)!=result:raise ValueError('chip mismatch')
            chip_cases+=1
    wrap_cases=0
    for address,length,size in [(4096,0xffffffff,0xff000),
                                (0xfffff000,0x2000,0xffffffff),
                                (0x80000001,0x80000000,0xffffffff)]:
        expected=oracle(address,length,size)
        for code,entry,delta,wanted in ((old,0x15d6c,0x1000dfec,24),(new,0x10023d58,0,12)):
            result,trace,frame=execute(code,entry,delta,address,length,size,0)
            if (result,trace)!=expected or frame!=wanted:raise ValueError('wrap mismatch')
        wrap_cases+=1
    report={'build':evidence,'cases':cases,'chip_cases':chip_cases,'wrap_cases':wrap_cases,'source_admitted':False,'limits':['Helpers modeled; Three complete wrapping sequences and 32 chip-wrapper cases pass; hardware remains unqualified.', 'Stock frame24, source frame12 on valid-address path and0 on rejection; physical erase not performed.']}
    (ROOT/'docs/research/gx8002-flash-erase-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
