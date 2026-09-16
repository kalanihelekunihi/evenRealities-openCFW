# SPDX-License-Identifier: MIT
"""Independent ordered SPI registration model with bounded valid lists."""
from dataclasses import dataclass
MASK=0xffffffff
HEAD=0x20017660
MASTER=0x2002b000
FLASH=0x2002c000
OLD=0x2002d000


@dataclass(frozen=True)
class Case:
    master:int=MASTER
    bus:int=0
    selects:int=1
    old_count:int=0
    flashes:tuple=()
    seed:int=0


class Model:
    def __init__(self,case):
        if not 0<=case.old_count<=3 or len(case.flashes)>8:raise ValueError('model list bound')
        self.case=case;self.trace=[];self.words={}
        def allocate(base,size):
            for offset in range(0,size,4):self.words[base+offset]=(case.seed^offset*0x1020304)&MASK
        allocate(HEAD,16);allocate(MASTER,36)
        self.words[MASTER]=case.bus&MASK;self.words[MASTER+4]=case.selects&MASK
        for i in range(case.old_count):allocate(OLD+i*64,36)
        def link(head,nodes):
            chain=[head,*nodes]
            for i,node in enumerate(chain):
                self.words[node]=chain[(i+1)%len(chain)]
                self.words[node+4]=chain[(i-1)%len(chain)]
        link(HEAD,[OLD+i*64+28 for i in range(case.old_count)])
        for i,(bus,select) in enumerate(case.flashes):
            base=FLASH+i*64;allocate(base,32)
            self.words[base]=bus&MASK
            self.words[base+4]=(case.seed^0xabcdef00)&MASK
            self.words[base+12]=(self.words[base+12]&0xffffff00)|(select&255)
        link(HEAD+8,[FLASH+i*64+24 for i in range(len(case.flashes))])

    def read(self,address):
        if address not in self.words:raise ValueError('SPI read bounds')
        value=self.words[address];self.trace.append(('read32',address,value));return value

    def read_byte(self,address):
        base=address&~3
        if base not in self.words:raise ValueError('SPI byte bounds')
        value=(self.words[base]>>((address&3)*8))&255
        self.trace.append(('read8',address,value));return value

    def write(self,address,value):
        if address not in self.words:raise ValueError('SPI write bounds')
        self.words[address]=value&MASK;self.trace.append(('write32',address,value&MASK))


def expected(case):
    m=Model(case)
    def result(value):return m.trace,m.words,value&MASK
    if not case.master:return result(-19)
    selects=m.read(case.master+4)
    if not selects:return result(-22)
    bus=m.read(case.master)
    if bus&0x80000000:return result(-22)
    previous=m.read(HEAD+4);entry=case.master+28
    for address,value in ((entry,HEAD),(HEAD+4,entry),(entry+4,previous),(previous,entry)):
        m.write(address,value)
    node=m.read(HEAD+8)
    for _ in range(len(case.flashes)+1):
        next_node=m.read(node)
        if node==HEAD+8:return result(0)
        flash=node-24
        if m.read(flash)==bus and m.read_byte(flash+12)<selects:
            m.write(flash+4,case.master)
            return result(0)
        node=next_node
    raise ValueError('SPI malformed or cyclic list')
