# SPDX-License-Identifier: MIT
"""Decoded shutdown stop ordering and complete clearing oracle."""
import json,subprocess
from itertools import product
from execute_gx8002_uart_message_done import execute,word,BASE,MASK
from build_gx8002_uart_message_done import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify(fill_hook=None):
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11ad8','--stop-address=0x11b30',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-done/callback.disassembly.txt').read_text());cases=0
    for available,mutation,value,result in product(range(4),(0,0x102036e8,0x10203704),(0,1,0x80000000,MASK),(0,1,MASK)):
        memory={BASE-16+i:(i*37)&255 for i in range(1440)};memory.update({0x2002ecb4+i:(i*19)&255 for i in range(52)})
        def helper(t,args,m,events):
            a,b,c,d=args
            if t==0x10207ac0:events.append(('get',a));return BASE+380*a if available&(1<<a) else 0
            if t in (0x102036e8,0x10203704):
                events.append(('stop',t,a))
                if t==mutation:
                    for port in (0,1):word(m,BASE+380*port+8,value)
                return result
            if t==0x102099cc:
                events.append(('clear',a,b,c))
                if b!=0 or any(a+i not in m for i in range(c)):raise ValueError('Clear bounds')
                if fill_hook is not None:return fill_hook(a,b,c,m)
                for i in range(c):m[a+i]=0
                return a
            raise ValueError('Helper')
        m=memory.copy();events=[]
        for port in (0,1):
            ctx=helper(0x10207ac0,[port,0,0,0],m,events)
            if ctx:
                for t in (0x102036e8,0x10203704):helper(t,[word(m,ctx+8),0,0,0],m,events)
                word(m,ctx+12,0)
        for a,n in ((0x2002e360,448),(0x2002ecc4,20),(BASE,760)):helper(0x102099cc,[a,0,n,0],m,events)
        for code,entry in ((old,0x11ad8),(new,0x1020854c)):
            a=execute(code,entry,0,0,memory,helper)
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=(('return',0),m,events):raise ValueError('Shutdown mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Independent stop/clear oracle with helper port mutation, availability and result variation; guarded memory and ABI. Memset/UART/lookup modeled; physical concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-done-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
