# SPDX-License-Identifier: MIT
"""Independent asynchronous task admission and descriptor-write model."""
from dataclasses import dataclass
MASK=0xffffffff
STATE=0x20027350
TASK=0x2002a000
@dataclass(frozen=True)
class Case:
    start:int=0
    end:int=0
    state:int=0
    task:int=TASK
    registers:int=0xa0c00000
    callback:int=0x10201000
    private:int=0x2002b000
    seed:int=0
    mutation:bool=False
class Model:
    def __init__(self,case):
        self.case=case;self.trace=[];self.calls=0
        self.words={STATE+o:(case.seed^o*0x1020305)&MASK for o in range(-16,0x5e0+16,4)}
        self.words.update({STATE:case.state,STATE+0x5b0:case.start,STATE+0x5b4:case.end,STATE+0x5c4:case.registers})
        self.words.update({TASK+o:(case.seed^0x10203040^o*0x87654321)&MASK for o in range(0,32,4)})
    def read(self,address):
        if address not in self.words:raise ValueError('run task read bounds')
        value=self.words[address];self.trace.append(('read',address,value));return value
    def write(self,address,value):
        if address not in self.words:raise ValueError('run task write bounds')
        self.words[address]=value&MASK;self.trace.append(('write',address,value&MASK))
    def call(self,name,*args):
        self.calls+=1;self.trace.append((name,*args))
        if self.case.mutation:
            for address,value in ((STATE,0x55+self.calls),(STATE+0x5b0,(self.case.start+1)%10),(STATE+0x5b4,(self.case.end+2)%10)):
                self.write(address,value)

def expected(case,model=None):
    m=Model(case) if model is None else model
    def result(value):return m.trace,m.words,value&MASK
    if not case.task:return result(-1)
    if not m.read(STATE+0x5c4):return result(-1)
    end=m.read(STATE+0x5b4)
    if not 0<=end<10:raise ValueError('model requires valid ring index')
    if (end+1)%10==m.read(STATE+0x5b0):return result(-1)
    base=STATE+m.read(STATE+0x5b4)*144
    m.write(base+0x90,case.callback)
    module=m.read(case.task)
    m.write(base+0x98,case.private)
    m.write(base+0x28,m.read(case.task+4))
    m.write(base+0x34,m.read(case.task+8))
    m.write(base+0x94,module)
    input_address=m.read(case.task+12);command=m.read(case.task+20)
    m.write(base+0x40,command);m.write(base+0x4c,input_address)
    for source,destination in ((16,0x58),(24,0x64),(28,0x70)):
        m.write(base+destination,m.read(case.task+source))
    descriptor=base+16;bus=descriptor&0xfffffff
    for offset,value in ((0x7c,bus),(0x88,0xfffffffe),(0x10,0x4100ff),(0x14,bus),(0x84,command)):
        m.write(base+offset,value)
    m.write(STATE+0x5b4,(m.read(STATE+0x5b4)+1)%10)
    if m.read(STATE)==2:m.call('resume')
    m.call('submit',descriptor)
    return result(0)
