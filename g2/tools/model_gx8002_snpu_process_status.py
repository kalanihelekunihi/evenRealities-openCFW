#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent observable state/call model for the stock SNPU status handler."""
from __future__ import annotations
from dataclasses import dataclass
MASK=0xffffffff
STATE=0x20027350
POINTER=STATE+0x5c4
READ_INDEX=STATE+0x5b0
END_INDEX=STATE+0x5b4
LAST=STATE+0x5d0
CALLBACKS=(0x11001000,0x11002000)
TARGETS={0x102056f0:'events',0x102057e0:'clear',0x10205860:'completed',0x10205870:'overflow_address',0x10205838:'clear_overflow',0x10205a90:'suspend',0x10205b1c:'overtime'}
class PrefixReached(Exception):pass
@dataclass(frozen=True)
class Case:
    events:int=1
    start:int=0
    end:int=5
    target:int|None=3
    duplicate:bool=False
    callbacks:int=0x3ff
    mutation:str='none'
    seed:int=0
    prefix:int|None=None

class Model:
    def __init__(self,case):
        self.case=case;self.trace=[];self.calls=0;self.iterations=0
        if not 0<=case.start<10 or not 0<=case.end<10:raise ValueError('unqualified ring index')
        self.completed=((STATE+case.target*144+16)-0x20000000)&MASK if case.target is not None else 0x12345678
        self.memory={STATE:case.seed,POINTER:0xa0c00000,READ_INDEX:case.start,END_INDEX:case.end,LAST:self.completed if case.duplicate else self.completed^4}
        self.callback_addresses=set()
        for index in range(10):
            p=STATE+index*144+0x90;self.callback_addresses.add(p)
            self.memory[p]=CALLBACKS[index%2] if case.callbacks&(1<<index) else 0
            self.memory[p+4]=(case.seed^index^0x80000000)&MASK
            self.memory[p+8]=(0x21000000+index*16)&MASK
    def read(self,address):
        if address not in self.memory:raise ValueError(f'unqualified state read {address:#x}')
        value=self.memory[address];self.trace.append(['read',address,value])
        if address in self.callback_addresses:
            self.iterations+=1
            if self.case.prefix is not None and self.iterations>=self.case.prefix:raise PrefixReached
        return value
    def write(self,address,value):
        if address not in (STATE,READ_INDEX,LAST):raise ValueError('unexpected handler state write')
        self.memory[address]=value&MASK;self.trace.append(['write',address,value&MASK])
    def mutate(self,kind):
        mode=self.case.mutation
        if mode not in ('none','pointers','callbacks','all'):raise ValueError('mutation mode')
        changes=[]
        if mode in ('pointers','all'):
            changes.extend(((POINTER,0xa0c00000 if self.calls%2 else 0x22000000),(STATE,(self.case.seed^self.calls)&MASK)))
        if mode in ('callbacks','all') and kind in ('callback','suspend'):
            changes.extend(((READ_INDEX,(self.calls+3)%10),(END_INDEX,(self.calls+7)%10),(STATE,0xdecafbad)))
            # Current callback/module/private have already been loaded before
            # suspend; later iterations must see refreshed record fields.
            for index,p in enumerate(sorted(self.callback_addresses)):
                changes.extend(((p,CALLBACKS[(index+self.calls)%2] if (index+self.calls)%3 else 0),(p+4,(self.case.seed^self.calls^index)&MASK),(p+8,0x23000000+self.calls*256+index*4)))
        for address,value in changes:
            self.memory[address]=value;self.trace.append(['helper_write',address,value])
    def call(self,name,arg0=None,arg1=None):
        if name in ('events','completed','overflow_address'):
            value=self.case.events if name=='events' else self.completed if name=='completed' else self.case.seed^0x87654321
            self.trace.append([name,arg0,value]);self.calls+=1;self.mutate(name);return value&MASK
        if name in ('clear','clear_overflow'):self.trace.append([name,arg0,arg1])
        elif name in ('suspend','overtime'):self.trace.append([name])
        else:raise ValueError('unknown helper')
        self.calls+=1;self.mutate(name)
        return (self.case.seed^0xcafe0000^self.calls)&MASK
    def callback(self,target,module,state,private):
        if target not in CALLBACKS:raise ValueError('unknown callback')
        self.trace.append(['callback',target,module,state,private]);self.calls+=1;self.mutate('callback')
        return (self.case.seed^0xface0000^self.calls)&MASK
    def result(self,value,status='return'):return self.trace,self.memory,value,status

def expected(case):
    m=Model(case)
    try:
        events=m.call('events',m.read(POINTER))
        m.call('clear',m.read(POINTER),events)
        if events&1:
            completed=m.call('completed',m.read(POINTER))
            if m.read(LAST)==completed:return m.result(0)
            m.write(LAST,completed)
            index=m.read(READ_INDEX);end=m.read(END_INDEX);next_state=1
            while True:
                descriptor=STATE+index*144+16
                p=STATE+index*144+0x90
                callback=m.read(p);module=m.read(p+4);private=m.read(p+8)
                index=(index+1)%10
                if index==end:next_state=2;m.call('suspend')
                matched=descriptor==((completed+0x20000000)&MASK)
                if matched:m.write(STATE,next_state);m.write(READ_INDEX,index)
                if callback:m.callback(callback,module,next_state,private)
                if matched:return m.result(0)
        if events&12:m.call('overtime');return m.result(0)
        if events&32:
            m.call('overflow_address',m.read(POINTER));base=m.read(POINTER);m.read(READ_INDEX)
            m.call('clear_overflow',base,events);return m.result(0)
        return m.result(1 if events&64 else 2)
    except PrefixReached:return m.result(None,'ring_prefix')
