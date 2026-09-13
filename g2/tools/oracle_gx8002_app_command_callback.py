# SPDX-License-Identifier: MIT
"""Independent command baseline expectations; helper results are supplied."""
from verify_gx8002_power_initialize import word

def expected(command,length,gain,result,seed):
    state,reply,data=0x2002e8f0,0x20026d5c,0x20041000
    m=seed.copy();events=[]
    def log(a,*args):events.append(('print',a,*args))
    def call(a,*args):events.append((hex(a),*args))
    def response(code,value):call(0x102093f4,0,code,value)
    if command==368:
        log(0x1020b735);call(0x10207404,0);word(m,state+40,result);response(112,int(result!=0))
    elif command==369:log(0x1020b74c);call(0x10206908);response(113,0)
    elif command==258:
        log(0x1020b766);events.extend(('token',v) for v in (b'0',b'0',b'2',b'3'))
        for i,v in enumerate((3,2,0,0,0,0,2,3)):m[state+44+i]=v
        m[reply+4]=2;m[reply+5]=2;m[reply+7]=1;word(m,reply+16,state+48);word(m,reply+24,4)
        events.append(('enqueue',514,1,bytes((0,0,2,3))))
    elif command==263:
        log(0x1020b77d);response(7,1);call(0x10205f24,0,0);call(0x10205f24,1,0);call(0x10207a80)
    elif command in (265,266):
        log(0x1020b794 if command==265 else 0x1020b7a8);response(command-256,1);m[state+52]=int(command==265);m[state+53]=0
    elif command==267:
        final=gain
        for i in range(length):final=seed[data+i];log(0x1020b7bd,final)
        word(m,state+56,final)
        if final<=48:
            call(0x102043ac,2,final);log(0x1020b7c4 if result==0 else 0x1020b7dd,final);response(11,int(result==0))
        else:log(0x1020b7f3,final);response(11,0)
    elif command==268:
        log(0x1020b81b);log(0x1020b832);call(0x102065dc,0,7);call(0x102065dc,1,9);response(12,1)
    elif command==269:
        log(0x1020b844);log(0x1020b85c);call(0x102065dc,0,1);call(0x102065dc,1,1);call(0x10205f24,0,0);call(0x10205f24,1,0);response(13,1)
    elif command==270:
        log(0x1020b86f);call(0x102049b0,0,1);m[reply+4]=14;m[reply+5]=1;m[reply+7]=1
        word(m,reply+16,0x20070000-20-8);word(m,reply+24,1);events.append(('enqueue',270,1,b'\x01'))
    elif command==271:
        log(0x1020b88d);word(m,state+60,1);m[state+64]=seed[data];log(0x1020b8a9,seed[data])
    return ('return',0),m,events
