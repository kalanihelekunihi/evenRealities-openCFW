# SPDX-License-Identifier: MIT
"""Independent receive framing/state reference for decoded callback qualification."""
from verify_gx8002_power_initialize import word
MASK=0xffffffff
BUFFER=0x2002e520
POINTER=0x2002e5d8

def oracle(port,length,memory,helper):
    memory=memory.copy();events=[]
    def call(target,*args):return helper(target,list(args)+[0]*(4-len(args)),memory,events)
    def half(addr):return memory[addr]+(memory[addr+1]<<8)
    ctx=call(0x10207ac0,port&255)
    if not ctx:return ('return',MASK),memory,events
    word(memory,POINTER,BUFFER);remaining=call(0x102035d8,port,BUFFER,length)
    packet=ctx+28
    for _ in range(100):
        if not remaining:return ('return',0),memory,events
        state=word(memory,ctx+368);publish=False;empty=False
        if state==0:
            magic=word(memory,ctx);value=word(memory,packet);cursor=word(memory,POINTER);used=0
            while value!=magic and used<remaining:
                value=((value>>8)|(memory[cursor+used]<<24))&MASK
                word(memory,packet,value);used+=1
            if value==magic:
                remaining-=used;word(memory,POINTER,(cursor+used)&MASK);word(memory,ctx+368,1)
            else:remaining=0;word(memory,POINTER,BUFFER)
        elif state==1:
            address=0x20026c74+4*port;count=word(memory,address);cursor=word(memory,POINTER)
            used=min(remaining,max(0,14-count))
            for i in range(used):memory[packet+count+i]=memory[cursor+i]
            count=(count+used)&MASK;remaining-=used;word(memory,address,count)
            if remaining:word(memory,POINTER,(cursor+used)&MASK)
            if count==14:
                word(memory,address,4);wanted=word(memory,packet+10)
                actual=call(0x102098a8,0,packet,10)
                if actual!=wanted:word(memory,packet,0);word(memory,ctx+368,0)
                elif half(packet+8):word(memory,ctx+368,2)
                else:publish=True;empty=True
        elif state==2:
            scratch=0x20080000;word(memory,scratch,remaining)
            result=call(0x10207cec,port,packet,POINTER,scratch);remaining=word(memory,scratch)
            for i in range(4):del memory[scratch+i]
            if result==1:publish=True
            elif result==MASK:word(memory,ctx+368,0)
        elif state==3:
            address=0x2002e5dc+4*port;count=word(memory,address);cursor=word(memory,POINTER)
            used=min(remaining,(4-count)&MASK);value=word(memory,ctx+4)
            for i in range(used):value=((value>>8)|(memory[cursor+i]<<24))&MASK;word(memory,ctx+4,value)
            remaining-=used;word(memory,POINTER,(cursor+used)&MASK)
            count=(count+used)&MASK
            if count==4:
                word(memory,packet+28,value);word(memory,ctx+4,0);word(memory,address,0);publish=True
            else:word(memory,address,count)
        else:remaining=0
        if publish:
            word(memory,ctx+368,0);memory[packet+20]=port&255
            word(memory,packet+24,0 if empty else (half(packet+8)-(4 if memory[packet+7] else 0))&MASK)
            call(0x100261b8,0x2002ecc4,packet)
            word(memory,packet,0);word(memory,packet+24,0)
    raise ValueError('Reference receive loop bound')
