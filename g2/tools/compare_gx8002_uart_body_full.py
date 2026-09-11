# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_body_full import execute
from verify_gx8002_channel_lookup import execute as lookup_execute
from verify_gx8002_channel_lookup_source import verify as lookup_verify
from build_gx8002_uart_body_upstream_probe import build


def verify(original_entry=False,queue_hook=None,control_hook=None):
    probe=build();lookup_dependency=lookup_verify();lookup_code=decode((ROOT/'build/gx8002-board/channel-lookup-candidate.disassembly.txt').read_text())
    def lookup(value):return lookup_execute(lookup_code,0x10207ac0,value)
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x11278','--stop-address=0x1146c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-body-probe'/('body-candidate.disassembly.txt' if original_entry else 'body.linked.disassembly.txt')).read_text());cases=0;coverage={'async':0,'restart':0,'queue':0,'failure':0}
    for port,flags,body_size,count,available,status,alignment,registration in product((0,1),(0,1),(20,80,128),(0,5,20),(0,8,32),(0,0xffffffff,{0x1020368c:0xffffffff},{0x102036c0:0xffffffff},{0x10203780:0xffffffff},{0x100261b8:0xffffffff}),(0,1,15),('valid','missing','small','null')):
        if count>body_size:continue
        ctx=0x2002e050+port*380;packet=ctx+28;ptr=0x20041000;src=0x20050000;dest=0x20060000+alignment;stack=0x20070000
        memory={ctx+i:0 for i in range(380)}
        for base,size in ((0x2002e360,448),(src,64),(dest,256),(stack-64,64)):memory.update({base+i:0 for i in range(size)})
        def put(addr,value,n=4):
            for i in range(n):memory[addr+i]=(value>>(8*i))&255
        put(ctx+8,port);put(ctx+368,2);put(packet+4,0x101,2);put(packet+7,flags,1);put(packet+8,body_size+(4 if flags else 0),2);put(packet+16,dest)
        put(0x2002e358+port*4,count);put(ptr,src);put(ptr+4,available)
        for off,val in ((4,0x999 if registration=='missing' else 0x101),(8,0 if registration=='null' else dest),(12,4 if registration=='small' else 256),(16,0)):put(0x2002e360+off,val)
        for i in range(64):memory[src+i]=(i*13+9)&255
        other=memory.copy();regs=dict(r0=port,r1=packet,r2=ptr,r3=ptr+4,r14=stack)
        a,at=execute(old,memory,regs,entry=0x11278,helper_result=status,lookup_hook=lookup,queue_hook=queue_hook,control_hook=control_hook)
        b,bt=execute(new,other,regs,entry=0x10207cec if original_entry else 0x10301000,helper_result=status,lookup_hook=lookup,queue_hook=queue_hook,control_hook=control_hook)
        relevant=lambda m:{k:v for k,v in m.items() if not stack-64<=k<stack}
        calls=lambda t:[x for x in t if isinstance(x[0],str)]
        if a!=b or relevant(memory)!=relevant(other) or calls(at)!=calls(bt):raise ValueError((port,flags,body_size,count,available,status,alignment,registration,a,b))
        for name in ('async','restart','queue'):
            coverage[name]+=int(any(x[0]==name for x in calls(at)))
        coverage['failure']+=int(a==0xffffffff)
        cases+=1
    return {'lookup_dependency':lookup_dependency,'probe':probe,'original_entry':original_entry,'decoded_cases':cases,'coverage':coverage,'source_admitted':False,'hardware_qualified':False,'limits':['Continuous stock/upstream body entry-to-return with abstract saved frames and modeled helpers. Finite valid port/buffer states; physical helpers and concurrency unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-body-full-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print('Full body cases:',r['decoded_cases'])
