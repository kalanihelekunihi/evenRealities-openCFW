# SPDX-License-Identifier: MIT
"""Independent command publication model; helper boundaries can change live state."""
from dataclasses import dataclass
MASK=0xffffffff
STATE=0x20027350
@dataclass(frozen=True)
class Case:
    descriptor:int=0x20027360
    previous:int=0
    state:int=0
    completed:int=0
    head:int=0x34560
    mutation:bool=False
    seed:int=0
class Model:
    def __init__(self,case):
        self.case=case;self.trace=[];self.calls=0
        self.words={STATE:case.state,STATE+0x5c0:case.previous,STATE+0x5c4:0xa0c00000}
        for pointer in (0x20028000,0x20028100,0x20028200,case.previous):
            if pointer:self.words[pointer+4]=case.seed
        if case.completed:self.words[(case.completed+0x20000004)&MASK]=case.head
    def read(self,address):
        if address not in self.words:raise ValueError('submit read bounds')
        value=self.words[address];self.trace.append(('read',address,value));return value
    def write(self,address,value):
        if address not in self.words:raise ValueError('submit write bounds')
        self.words[address]=value&MASK;self.trace.append(('write',address,value&MASK))
    def call(self,name,*args):
        self.trace.append((name,*args));self.calls+=1
        if self.case.mutation:
            for address,value in ((STATE+0x5c4,0xa0c00000+self.calls*0x100),(STATE+0x5c0,0x20028000+(self.calls%3)*0x100)):
                self.write(address,value)
        return (self.case.seed^self.calls*0x1020304)&MASK

def expected(case,model=None):
    m=Model(case) if model is None else model;head=(case.descriptor+16)&0xfffffff
    tail=m.read(STATE+0x5c0)
    start=not tail
    if not start:
        state=m.read(STATE)
        if state==2:
            m.call('get_completed',m.read(STATE+0x5c4))
            if case.completed:
                m.write(m.read(STATE+0x5c0)+4,head)
                head=m.read((case.completed+0x20000004)&MASK)
            start=True
        else:
            m.call('flush_descriptor',case.descriptor)
            previous=m.read(STATE+0x5c0)
            m.write(previous+4,head)
            m.call('clean_range',previous,8)
    if start:
        m.write(STATE,1)
        m.call('set_head',m.read(STATE+0x5c4),head)
        m.call('flush_descriptor',case.descriptor)
        m.call('enable',m.read(STATE+0x5c4))
    m.write(STATE+0x5c0,case.descriptor)
    return m.trace,m.words
