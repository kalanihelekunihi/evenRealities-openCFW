# SPDX-License-Identifier: MIT
"""Independent initialization oracle and full decoded stock/source comparison."""
import json,subprocess
from itertools import product
from execute_gx8002_uart_message_initialize import execute,word,BASE,MASK
from build_gx8002_uart_message_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def helper_for(init_result):
    def helper(t,args,m,events):
        a,b,c,d=args
        if t==0x10207ac0:events.append(('get',a));return {0:BASE,1:BASE+380}.get(a,0)
        if t in (0x102036e8,0x10203704):events.append(('stop',t,a));return MASK
        if t==0x10203530:events.append(('init',a,b));return init_result
        if t==0x10206f9c:
            events.append(('queue_init',a,b,c,d))
            for i,v in enumerate((0,0,b,c,d)):word(m,a+4*i,v)
            return MASK
        if t==0x1020368c:events.append(('start',a,b,c));return MASK
        if t in (0x102076c0,0x10207718):events.append(('power_register',t,word(m,a),word(m,a+4)));return MASK
        if t==0x10207770:events.append(('lock_create',a));word(m,a,7);return 7
        raise ValueError(('Unknown helper',hex(t)))
    return helper

def oracle(memory,config,helper):
    m=memory.copy();events=[]
    def call(t,*args):return helper(t,list(args)+[0]*(4-len(args)),m,events)
    if not config:return ('return',MASK),m,events
    port=word(m,config);ctx=call(0x10207ac0,port&255)
    if not ctx:return ('return',MASK),m,events
    word(m,ctx+8,port)
    if word(m,ctx+12) and not word(m,config+12):return ('return',MASK),m,events
    word(m,ctx,word(m,config+8) or 0x42555858);word(m,ctx+16,word(m,config+4))
    call(0x102036e8,word(m,ctx+8));call(0x10203704,word(m,ctx+8))
    if call(0x10203530,word(m,ctx+8),word(m,ctx+16)):return ('return',MASK),m,events
    for i in range(2):
        other=call(0x10207ac0,i)
        if other and not word(m,other+12):call(0x10206f9c,0x2002ecc4,0x2002e5e4,256,32);break
    if not word(m,ctx+12):call(0x10206f9c,ctx+348,ctx+92,256,32)
    call(0x1020368c,word(m,ctx+8),0x10208098,0)
    scratch=0x20080000
    for i,v in enumerate((0x10207c74,0x1020b18b,0x10207c9c,0x1020b1a3)):word(m,scratch+4*i,v)
    call(0x102076c0,scratch);call(0x10207718,scratch+8)
    for i in range(16):del m[scratch+i]
    call(0x10207770,ctx+376);word(m,ctx+12,1)
    return ('return',0),m,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x119e4','--stop-address=0x11ad8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-initialize/callback.disassembly.txt').read_text());cases=0
    for port,first,second,reinit,magic,status in product((0,1,2,256,257,MASK),(0,1,MASK),(0,1,MASK),(0,1),(0,0x12345678),(0,1,MASK)):
        config=0x20040000;m={BASE+i:(i*37)&255 for i in range(760)};m.update({0x2002ecc4+i:0xa5 for i in range(20)})
        word(m,BASE+12,first);word(m,BASE+380+12,second)
        for i,v in enumerate((port,115200,magic,reinit)):word(m,config+i*4,v)
        helper=helper_for(status);expected=oracle(m,config,helper)
        for code,entry in ((old,0x119e4),(new,0x10208458)):
            a=execute(code,entry,config,0,m,helper)
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError(('Initialization',port,first,second,reinit,magic,status,hex(entry)))
        cases+=1
    for code,entry in ((old,0x119e4),(new,0x10208458)):
        a=execute(code,entry,0,0,{},helper_for(0))
        if a!=(('return',MASK),{},[]):raise ValueError('Null config')
    return {'candidate':candidate,'decoded_cases':cases+1,'source_admitted':False,'hardware_qualified':False,'limits':['Independent initialization oracle, final global memory, helper ordering and saved ABI; modeled UART/queue/power helpers. Aliases, helper mutations and nested execution pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
