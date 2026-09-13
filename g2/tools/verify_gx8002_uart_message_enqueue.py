# SPDX-License-Identifier: MIT
"""Decoded packet enqueue compared to an independent header/publication oracle."""
import json,subprocess
from itertools import product
from execute_gx8002_uart_message_enqueue import execute,word,BASE,MASK
from build_gx8002_uart_message_enqueue import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def helper_for(full,put_result,crc):
    def helper(t,args,m,events):
        a,b,c,d=args
        if t==0x10207ac0:events.append(('get',a));return {0:BASE,1:BASE+380}.get(a,0)
        if t==0x10207008:events.append(('full',a));return full
        if t==0x102098a8:events.append(('crc',a,b,c,bytes(m[b+i] for i in range(c)).hex()));return crc
        if t==0x10025664:events.append(('clean',a,b,bytes(m[a+i] for i in range(b)).hex()));return MASK
        if t==0x100261b8:events.append(('put',a,b,bytes(m[b+i] for i in range(32)).hex()));return put_result
        if t==0x10207adc:events.append(('start',a));return MASK
        raise ValueError(('Helper',hex(t)))
    return helper

def oracle(memory,packet,helper):
    m=memory.copy();events=[]
    def call(t,*args):return helper(t,list(args)+[0]*(4-len(args)),m,events)
    ctx=call(0x10207ac0,m[packet+20])
    if not ctx or not word(m,ctx+12) or (word(m,packet+24) and not word(m,packet+16)):return ('return',MASK),m,events
    if call(0x10207008,ctx+348):return ('return',MASK),m,events
    length=(word(m,packet+24)+(4 if m[packet+7] else 0))&65535
    m[packet+8]=length&255;m[packet+9]=length>>8
    if word(m,packet)==0:word(m,packet,word(m,ctx))
    if m[packet+5]!=2:
        seq=m[ctx+20];m[ctx+20]=(seq+1)&255;m[packet+6]=seq
    crc=call(0x102098a8,0,packet,10);word(m,packet+10,crc)
    call(0x10025664,packet,16)
    if not call(0x100261b8,ctx+348,packet):return ('return',MASK),m,events
    if not word(m,ctx+24):call(0x10207adc,m[ctx+8])
    return ('return',0),m,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11948','--stop-address=0x119e4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-message-enqueue/callback.disassembly.txt').read_text());cases=0
    for port,init,length,body,flags,cmd,full,put in product((0,1,2),(0,1),(0,1,65535,65536,MASK),(0,0x20050000),(0,1,255),(0x101,0x200,0x2ff,0x300),(0,1),(0,1)):
        p=0x20040000;ctx=BASE+380*(port%2);m={BASE+i:(i*37)&255 for i in range(760)};m.update({p+i:0 for i in range(32)})
        word(m,ctx+12,init);word(m,ctx+8,port);word(m,ctx+24,cases%2);m[ctx+20]=(0,254,255)[cases%3]
        word(m,p,0 if cases%2 else 0x87654321);word(m,p+16,body);word(m,p+24,length);m[p+20]=port;m[p+7]=flags;m[p+4]=cmd&255;m[p+5]=cmd>>8
        helper=helper_for(full,put,(0,1,0x87654321,MASK)[cases%4]);expected=oracle(m,p,helper)
        for code,entry in ((old,0x11948),(new,0x102083bc)):
            a=execute(code,entry,p,0,m,helper)
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError(('Enqueue',port,init,length,body,flags,cmd,full,put,hex(entry)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Independent packet/header/sequence oracle and helper publication snapshots; final guarded memory and ABI. Helpers modeled; mutation,aliasing and nested queue composition pending.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-message-enqueue-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'])
