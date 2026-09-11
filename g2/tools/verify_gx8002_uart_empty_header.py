# SPDX-License-Identifier: MIT
"""Decoded empty-body header publication at the queue call boundary."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,port,status,queue_hook=None):
    context=0x20040000
    r={f'r{i}':0x90000000+i for i in range(32)}
    r.update(r4=context,r6=context+28,r9=port,r17=0)
    memory={context+i:0xa5 for i in range(380)};trace=[];pc=0x1180a
    def word(addr):return sum(memory[addr+i]<<(8*i) for i in range(4))
    for _ in range(16):
        if pc==0x116a4:
            return trace,word(context+368),word(context+28),word(context+52)
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('st.w','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Empty header store')
            src,base,off=m.groups();addr=r[base]+int(off,0);size=4 if op=='st.w' else 1
            trace.append(('write',addr-context,size,r[src]))
            for i in range(size):memory[addr+i]=(r[src]>>(8*i))&255
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if int(args,0)!=0xffe2f744 or (r['r0'],r['r1'])!=(0x2002ecc4,context+28):
                raise ValueError('Empty header queue boundary')
            packet=bytes(memory[context+28+i] for i in range(32))
            trace.append(('queue',packet.hex()))
            if queue_hook is not None:status=queue_hook(packet)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=status
        elif op=='br':pc=int(args,0);continue
        else:raise ValueError('Empty header instruction '+op)
        pc+=width
    raise ValueError('Empty header bound')


def verify():
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x1180a','--stop-address=0x11828',str(wrapper)],text=True))
    cases=0
    for port in (0,1):
        packet=bytearray([0xa5]*32);packet[20]=port;packet[24:28]=bytes(4)
        expected=[('write',368,4,0),('write',48,1,port),('write',52,4,0),
                  ('queue',packet.hex()),('write',28,4,0),('write',52,4,0)]
        for status in (0,1,0xffffffff):
            if execute(code,port,status)!=(expected,0,0,0):raise ValueError('Empty header publication order')
            cases+=1
    return {'decoded_cases':cases,'queue_runtime_target':0x100261b8,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Starts after zero length was decoded into r17. Queue boundary modeled, including caller clobbers and return status. Queue internals and full callback execution remain pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-empty-header.json').write_text(json.dumps(report,indent=2)+'\n');print('Empty header cases:',report['decoded_cases'])
