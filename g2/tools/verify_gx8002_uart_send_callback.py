# SPDX-License-Identifier: MIT
"""Compare complete transmit state-machine execution with an independent oracle."""
import json, subprocess
from itertools import product
from execute_gx8002_uart_send_callback import execute,word,BASE,MASK
from build_gx8002_uart_send_callback import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def make_helper(body_result,crc_result,mutation=None):
    def helper(target,args,memory,events):
        a,b,c,d=args; result=MASK
        if target==0x10207ac0:
            events.append(('get',a));result={0:BASE,1:BASE+380}.get(a,0)
        elif target==0x10203604:events.append(('uart',a,b,c));result=crc_result
        elif target==0x102098a8:events.append(('crc',a,b,c));result=crc_result
        elif target==0x10207b38:
            budget=word(memory,c);events.append(('body',a,b,budget));word(memory,c,0);result=body_result
        elif target==0x102077d4:events.append(('unlock',a));result=crc_result
        elif target==0x10207adc:events.append(('start',a))
        elif 0x10310000<=target<0x10310018:
            events.append(('completion',target,a,b));result=crc_result
        else:raise ValueError(('Helper',hex(target)))
        if mutation:mutation(target,memory)
        return result
    return helper

def oracle(port,length,memory,helper):
    memory=memory.copy();events=[];budget=length
    def call(target,*args):return helper(target,list(args)+[0]*(4-len(args)),memory,events)
    def put(addr,value):
        word(memory,addr,value);events.append(('write',addr,value))
    ctx=call(0x10207ac0,port&255)
    if not ctx:return ('return',MASK),memory,events
    packet=ctx+60
    for _ in range(20):
        state=word(memory,ctx+372)
        if state in (0,2):
            counter=(0x2002e560 if state==0 else 0x2002e568)+4*port
            limit=14 if state==0 else 4
            if state==2 and word(memory,counter)==0:
                crc=call(0x102098a8,0,word(memory,packet+16),word(memory,packet+24));put(0x2002e570+4*port,crc)
            count=word(memory,counter);amount=min(budget,(limit-count)&MASK)
            pointer=(packet if state==0 else 0x2002e570+4*port)+count
            call(0x10203604,port,pointer&MASK,amount)
            count=(word(memory,counter)+amount)&MASK
            if count==limit:count=0
            put(counter,count);budget=(budget-amount)&MASK
            if count==0:
                size=memory[ctx+68]+256*memory[ctx+69]
                put(ctx+372,1 if state==0 and size else 3)
        elif state==1:
            scratch=0x20080000;word(memory,scratch,budget)
            result=call(0x10207b38,port,packet,scratch);budget=word(memory,scratch)
            for i in range(4):del memory[scratch+i]
            if result==1:put(ctx+372,2 if memory[ctx+67] else 3)
        elif state==3:
            other=call(0x10207ac0,memory[packet+20])
            if other:
                call(0x102077d4,word(memory,other+376))
                for i in range(6):
                    row=0x2002e578+i*16
                    cmd=memory[packet+4]+256*memory[packet+5]
                    if word(memory,row+4)==cmd and word(memory,row)==memory[packet+20]:
                        call(word(memory,row+8),packet,word(memory,row+12));break
            if call(0x10207adc,port&255)==MASK:return ('return',0),memory,events
        elif budget:return ('bounded_loop',),memory,events
        if not budget:return ('return',0),memory,events
    raise ValueError('Oracle bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11494','--stop-address=0x11624',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-uart-send-callback/callback.disassembly.txt').read_text());cases=0
    for port,state,budget,count,flags,match in product((0,1),range(5),(0,1,3,4,13,14,15,32),(0,1,3,4,13,14),(0,1,255),range(-1,6)):
        ctx=BASE+380*port;memory={BASE+i:(i*37)&255 for i in range(1440)}
        word(memory,ctx+372,state);word(memory,0x2002e560+port*4,count);word(memory,0x2002e568+port*4,count)
        memory[ctx+67]=flags;memory[ctx+68]=flags;memory[ctx+69]=0;memory[ctx+80]=port
        memory[ctx+64]=0x34;memory[ctx+65]=0x12
        for i in range(6):
            row=0x2002e578+i*16;word(memory,row,port);word(memory,row+4,0x1234 if i==match else i);word(memory,row+8,0x10310000+i*4);word(memory,row+12,0x12340000+i)
        helper=make_helper((0,1,MASK)[cases%3],(0,1,0x80000000,MASK)[cases%4])
        expected=oracle(port,budget,memory,helper)
        for code,entry in ((old,0x11494),(new,0x10207f08)):
            actual=execute(code,entry,port,budget,memory,helper)
            if actual!=expected:raise ValueError(('Mismatch',port,state,budget,count,flags,match,hex(entry),actual[0],expected[0],actual[2],expected[2]))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite decoded cases and independent state-machine oracle; helpers modeled. Mutation and nested helper execution not yet qualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-send-callback-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'])
