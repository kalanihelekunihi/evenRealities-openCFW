#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded leaf block-boundary logic, including output/state aliasing."""
import json,re,subprocess
from build_gx8002_flash_block_range import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200264e4

def execute(code,pc,address,index,size,start,end):
    r={f'r{i}':0x12340000+i for i in range(32)}
    initial=r.copy();r.update(r0=address,r1=start,r2=end)
    memory={STATE:index&MASK,STATE+4:size,0x30000000:123,0x30000004:456}
    events=[];flag=False
    for _ in range(12000000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];n=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if op=='ld.w':r[reg]=memory[a];events.append(['read',a,r[reg]])
            else:memory[a]=r[reg];events.append(['write',a,r[reg]])
        elif op in ('addi','subi','andni'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&~b)&MASK
        elif op in ('and','nor'):
            a=r[p[0]];b=r[p[1]];r[p[0]]=(a&b if op=='and' else ~(a|b))&MASK
        elif op in ('cmpne','cmphs'):flag=r[p[0]]!=r[p[1]] if op=='cmpne' else r[p[0]]>=r[p[1]]
        elif op=='blz':
            if r[p[0]]&0x80000000:n=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (flag if op=='bt' else not flag):n=int(p[0],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,12)):raise ValueError('saved register')
            return r['r0'],events
        else:raise ValueError('unknown instruction '+op)
        pc=n
    raise ValueError('execution bound')

def expected(address,index,size,start,end):
    """Closed-form block selection; no simulated loop or instruction semantics."""
    memory={STATE:index&MASK,STATE+4:size}
    events=[]
    for output in (end,start):
        memory[output]=0;events.append(['write',output,0])
    selected=memory[STATE];events.append(['read',STATE,selected])
    if selected&0x80000000:return MASK,events
    capacity=memory[STATE+4];events.append(['read',STATE+4,capacity])
    if address//4096 >= capacity//4096:return MASK,events
    base=(address//4096)*4096
    events.extend([['write',start,base],['write',end,base+4096]])
    return 0,events

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    # The authenticated build verifies the stock image hash; wrap it for ISA decoding.
    from build_gx8002_flash_block_range import IMAGE
    import struct
    wrapper=out/'block-range-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x158b8','--stop-address=0x15900',str(wrapper)],text=True))
    new=decode((out/'block-range-linked.disassembly.txt').read_text());cases=0
    for size in (0,1,4095,4096,4097,8192,65535,65536):
      for index in (-1,0,1,0x80000000):
       for address in (0,1,4095,4096,4097,8191,8192,65535,65536,0xffffffff):
        for start,end in ((0x30000000,0x30000004),(0x30000000,0x30000000),(STATE,0x30000004),(0x30000000,STATE+4),(STATE+4,STATE)):
         a=execute(old,0x158b8,address,index,size,start,end)
         b=execute(new,0x100238a4,address,index,size,start,end)
         if a!=b or a!=expected(address,index,size,start,end):raise ValueError(('decoded mismatch',size,index,address,start,end,a,b))
         cases+=1
    large_cases=0
    for size,address in ((0xffffffff,0xffffefff),(0xffffffff,0xfffff000),
                         (0x80000001,0x7fffffff),(0x80000001,0x80000000)):
        args=(address,0,size,0x30000000,0x30000004)
        reference=expected(*args)
        if execute(old,0x158b8,*args)!=reference or execute(new,0x100238a4,*args)!=reference:
            raise ValueError('large-capacity mismatch')
        large_cases+=1
    report={'large_capacity_cases':large_cases,'independent_expected_results':True,'build':evidence,'decoded_leaf_cases':cases,'source_admitted':False,'limits':['Wrapper call/stack qualification remains.','No physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-block-bounds-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print('decoded leaf cases',cases);return report
if __name__=='__main__':verify()
