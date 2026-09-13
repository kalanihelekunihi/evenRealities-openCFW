# SPDX-License-Identifier: MIT
"""Whole dispatcher calls reconstructed receive body over shared packet memory."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_callback import helper_for
from gx8002_uart_receive_callback_oracle import oracle
from execute_gx8002_uart_receive_callback import execute,word,BASE
from execute_gx8002_uart_body_full import execute as body_execute
from build_gx8002_uart_body_upstream_probe import build as build_body
from build_gx8002_uart_receive_callback import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=build_body();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    def stock(a,b):return decode(subprocess.check_output([pre,'-D','--start-address='+hex(a),'--stop-address='+hex(b),str(wrapper)],text=True))
    old=stock(0x11624,0x11838);body_old=stock(0x11278,0x1146c)
    new=decode((ROOT/'build/gx8002-uart-receive-callback/callback.disassembly.txt').read_text());body_new=decode((ROOT/'build/gx8002-uart-body-probe/body-candidate.disassembly.txt').read_text());cases=0;calls=0
    for port,flags,total,count,length,registration in product((0,1),(0,1),(20,80),(0,5,20),(8,32),('valid','missing','null')):
        ctx=BASE+380*port;packet=ctx+28;dest=0x20060000
        memory={BASE+i:0 for i in range(1440)};memory.update({dest+i:0xa5 for i in range(256)})
        word(memory,0x20026c74,4);word(memory,0x20026c78,4);word(memory,ctx,0x12345678)
        word(memory,ctx+368,2);word(memory,ctx+8,port);word(memory,packet+16,dest);word(memory,0x2002e358+4*port,count)
        memory[packet+4]=1;memory[packet+5]=1;memory[packet+7]=flags;memory[packet+8]=total+4*flags
        for off,value in ((4,0x999 if registration=='missing' else 0x101),(8,0 if registration=='null' else dest),(12,256),(16,0)):word(memory,0x2002e360+off,value)
        data=bytes((i*13+9)&255 for i in range(length))
        def fresh(source):
            base=helper_for(data,0,True,1)
            def helper(target,args,m,events):
                nonlocal calls
                if target!=0x10207cec:return base(target,args,m,events)
                a,b,c,d=args;events.append(('body',a,b,c,word(m,d)))
                stack=0x20090000
                assert not any(stack-64<=k<stack for k in m)
                m.update({stack-64+i:0xa5 for i in range(64)})
                result,trace=body_execute(body_new if source else body_old,m,dict(r0=a,r1=b,r2=c,r3=d,r14=stack),entry=0x10207cec if source else 0x11278)
                for k in range(stack-64,stack):del m[k]
                events.extend(('nested_body',)+e for e in trace if isinstance(e[0],str));calls+=1
                return result
            return helper
        expected=oracle(port,length,memory,fresh(False))
        for code,entry,source in ((old,0x11624,False),(new,0x10208098,True)):
            a=execute(code,entry,port,length,memory,fresh(source))
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError(('Nested body',port,flags,total,count,length,registration,a[0],expected[0]))
        cases+=1
    return {'body_dependency':dependency,'dispatcher_cases':cases,'body_executions':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Nested decoded body shares dispatcher packet/global/buffer memory using separate abstract frame; source body versus stock body and independent dispatcher oracle. UART,queue and lookup inside body modeled; physical hardware/concurrency unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-callback-body.json').write_text(json.dumps(result,indent=2)+'\n');print(result['dispatcher_cases'],result['body_executions'])
