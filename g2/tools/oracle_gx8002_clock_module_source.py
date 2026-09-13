# SPDX-License-Identifier: MIT
"""ID-based clock transition model, independent of decoded instruction layout."""
MASK=0xffffffff
def expected(module,source,modules,registers):
    state=dict(registers);calls=[];events=[]
    def result(status):return status&MASK,calls,events,state
    if module not in modules:return result(-1)
    mask=1
    if source==2:
        if module not in (0,1,2,6,9):return result(-1)
    elif source>2:
        if module==7:source//=4
        elif module==8:source-=5;mask=3
        else:return result(-1)
    calls.append(('lookup',module));param=modules[module];offset=param['clock_offset']
    if offset==-1:return result(-1)
    value=source
    if value==2 and module!=8:value=1;offset+=1
    base=0xa0010000 if module<10 else 0xa0300000
    select=base+(0x8c if module<10 else 0x88);gate=base+0x18
    def read(address):
        value=state[address];events.append(('read',address,value));return value
    def write(address,value):
        value&=MASK;state[address]=value;events.append(('write',address,value))
        if address==base+0x1c:state[gate]|=value
        if address==base+0x20:state[gate]&=~value&MASK
    def set_source():
        calls.append(('set',select,offset,value&MASK,mask))
        write(select,(read(select)&~(mask<<offset))|((value<<offset)&MASK))
    if (read(select)>>offset)&mask==value:return result(0)
    inhibit=read(gate)
    members=(module+1,module+2) if module in (16,19,22) else (module,)
    active=any(not(inhibit>>modules[m]['gate_all_offset']&1) for m in members)
    if not active:set_source();return result(0)
    high=1<<param['gate_high_offset']
    if module in (7,8):
        set_source();write(base+0x1c,high)
        inhibit=read(gate);selected=read(select)
        system_external=(selected>>modules[2]['clock_offset'])&1
        system_disabled=(inhibit>>modules[2]['gate_all_offset'])&1
        if system_external and system_disabled:
            pdm_internal=((selected>>modules[8]['clock_offset'])&3)==0
            adc_internal=((selected>>modules[7]['clock_offset'])&1)==0
            pdm_active=not(inhibit>>modules[8]['gate_all_offset']&1)
            adc_active=not(inhibit>>modules[7]['gate_all_offset']&1)
            if (pdm_internal and pdm_active) or (adc_internal and adc_active):write(base+0x20,high)
    elif value==1:write(base+0x20,high);set_source()
    else:set_source();write(base+0x1c,high)
    return result(0)
