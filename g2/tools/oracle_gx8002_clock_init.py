# SPDX-License-Identifier: MIT
"""Independent initialization policy and state oracle, no instruction decoding."""
from verify_gx8002_power_initialize import word


def expected(mode,trim,success,initial,voltage_state=False,selector_state=False,module_state_model=None,divider_state_model=None,gate_state_model=None,pll_state_model=None,trim_state=False):
    state=dict(initial);calls=[(0x10024df8,6,1),('mode',)];events=[]
    if divider_state_model:divider_state_model(0x10024df8,(6,1),state,events)
    def program(target,*args):
        calls.append((target,*args))
        if divider_state_model:divider_state_model(target,args,state,events)
    def store(address,value):
        word(state,address,value)
        events.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
    def select(source,clock):
        calls.append(('selector',source,clock))
        if selector_state:store(0xa001008c,(word(state,0xa001008c)&~(1<<source))|(clock<<source))
    if mode==0:
        calls.append(('trim',))
        if trim_state and trim in (0,1) and gate_state_model:gate_state_model(9,1,state,events)
        if trim==1:
            store(0x20026900,1);feedback=word(initial,0x200268dc)
            for index,delta in enumerate((0,10,15,-10,-15)):
                value=(feedback+delta)&0xffffffff;store(0x200268dc,value);calls.append(('pll_retry',value))
                if pll_state_model:pll_state_model(state,events)
                if index==success:break
            else:return 'failure_loop',state,calls,events
            table=0x20026904
        else:table=0x20026954
        for i in range(10):select(word(state,table+8*i),state[table+8*i+4])
    elif mode==1:
        if trim==1:
            calls.append(('pll',word(state,0x200268c8)))
            if pll_state_model:pll_state_model(state,events)
        select(16,0);select(0,1)
    modules=((10,1),(6,1),(0,2),(1,0),(3,0),(4,0),(5,0),(2,1),(7,3),(8,6),(9,0),(22,0),(16,1),(11,1),(19,1),(12,1),(13,1),(14,1),(15,1))
    for module,source in modules:
        calls.append((0x10024be0,module,source))
        if module_state_model:module_state_model(module,source,state,events)
    program(0x10024f44,2,0x1000000,0)
    for x in ((6,1),(0,4),(1,3),(3,2),(2,2),(7,384),(8,12),(19,2)):program(0x10024df8,*x)
    program(0x10024f44,16,0x1000000,0);program(0x10024f44,11,0x1000000,1)
    for x in ((10,3),(12,1),(13,1),(15,2),(14,2)):program(0x10024df8,*x)
    def gate(module,enable):
        calls.append((0x10025080,module,enable))
        if gate_state_model:gate_state_model(module,enable,state,events)
    if mode==1:
        for i in range(11,26):gate(i,(word(state,0x20027318)>>i)&1)
    gate(5,1)
    store(0xa0005084,word(state,0xa0005084)&~1)
    store(0xa0005060,word(state,0xa0005060)&~2)
    for off in (0x40,0x44,0x48,0x4c):store(0xa0005000+off,0x59)
    calls.extend([(0x100246f0,0),(0x10024730,0)])
    if voltage_state:
        store(0xa0005054,word(state,0xa0005054)&0xf0)
        store(0xa0000038,16)
    return 'return',state,calls,events
