#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent model for overtime diagnostics, head selection and restart."""
from dataclasses import dataclass
MASK=0xffffffff
STATE=0x20027350
FORMAT=0x1020ac0e
NEWLINE=0x1020b7c2
ADDRESSES=0x1020ac16
BEFORE=0x1020ac5c
COMMAND=0x1020ac7a
TYPE=0x1020ac91
ARITY={FORMAT:1,NEWLINE:0,ADDRESSES:3,BEFORE:0,COMMAND:0,TYPE:1}
TARGETS={0x102058b4:'base',0x102058c4:'current',0x10205860:'previous',0x102058a4:'head',0x10205600:'disable',0x10205880:'reset',0x10205950:'init',0x10205898:'set_head',0x102055f4:'enable'}
@dataclass(frozen=True)
class Case:
    seed:int=0
    current:int=0x30080
    previous:int=0
    head:int=0x12345678
    changing:bool=False
    pointers:bool=False
class Model:
    def __init__(self,case):
        self.case=case;self.trace=[];self.calls=0;self.mapped=(case.current+0x20000000)&MASK
        self.memory={STATE+0x5c4:0xa0c00000,STATE+0x5c8:0xa0300000,STATE+0x5cc:0xa0c00190}
    def read_state(self,address):
        if address not in self.memory:raise ValueError('overtime state address')
        value=self.memory[address];self.trace.append(['state_read',address,value]);return value
    def boundary(self):
        self.calls+=1
        if self.case.pointers:
            for offset in (0x5c4,0x5c8,0x5cc):
                address=STATE+offset;value=0x24000000+(self.calls%3)*0x10000+offset*4
                self.memory[address]=value;self.trace.append(['helper_write',address,value])
        return (self.case.seed^0xcafe0000^self.calls)&MASK
    def value(self,address):
        epoch=self.calls*0x9e3779b9 if self.case.changing else 0
        if self.case.previous and address==((self.case.previous+0x20000004)&MASK):return (self.case.head^epoch)&MASK
        if not self.mapped-128<=address<self.mapped+128:raise ValueError('overtime RAM bounds')
        return (self.case.seed^address^epoch)&MASK
    def read_word(self,address):
        if address&3:raise ValueError('overtime word alignment')
        value=self.value(address);self.trace.append(['read_word',address,value]);return value
    def read_byte(self,address):
        if address!=self.mapped:raise ValueError('overtime byte address')
        value=self.value(address)&255;self.trace.append(['read_byte',address,value]);return value
    def printf(self,fmt,*args):
        if fmt not in ARITY or len(args)<ARITY[fmt]:raise ValueError('overtime printf shape')
        self.trace.append(['printf',fmt,*args[:ARITY[fmt]]]);return self.boundary()
    def call(self,name,arg0=None,arg1=None):
        if name=='base':value=self.case.seed^0x87654321;self.trace.append([name,arg0,arg1,value])
        elif name in ('current','previous','head'):
            value=getattr(self.case,name);self.trace.append([name,arg0,value])
        elif name=='init':value=0;self.trace.append([name])
        elif name=='set_head':value=0;self.trace.append([name,arg0,arg1])
        elif name in ('disable','reset','enable'):value=0;self.trace.append([name,arg0])
        else:raise ValueError('overtime helper name')
        result=self.boundary();return value&MASK if name in ('base','current','previous','head') else result
    def dump(self,address):
        self.trace.append(['dump',address])
        for i in range(32):
            self.printf(FORMAT,self.read_word(address+4*i))
            if (i+1)%10==0:self.printf(NEWLINE)
        return self.printf(NEWLINE)
    def result(self):return self.trace,self.memory

def expected(case):
    m=Model(case)
    base=m.call('base',m.read_state(STATE+0x5cc),2)
    current=m.call('current',m.read_state(STATE+0x5c4))
    previous=m.call('previous',m.read_state(STATE+0x5c4))
    mapped=(current+0x20000000)&MASK
    m.printf(ADDRESSES,current,base,previous);m.printf(BEFORE);m.dump(mapped-128)
    m.printf(COMMAND);m.dump(mapped);m.printf(TYPE,m.read_byte(mapped))
    head=m.call('head',m.read_state(STATE+0x5c4)) if previous==0 else m.read_word((previous+0x20000004)&MASK)
    m.call('disable',m.read_state(STATE+0x5c4));m.call('reset',m.read_state(STATE+0x5c8));m.call('init')
    m.call('set_head',m.read_state(STATE+0x5c4),head);m.call('enable',m.read_state(STATE+0x5c4))
    return m.result()
