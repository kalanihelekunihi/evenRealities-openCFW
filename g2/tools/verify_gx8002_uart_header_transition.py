# SPDX-License-Identifier: MIT
"""Decode header-result transitions into the next receive state."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_header_stock import execute as header


def transition(code, result, length):
    state=1; r={'r3':0, 'r17':0};pc={0:0x116a4,1:0x11802,0xffffffff:0x1173c}[result]
    for _ in range(10):
        if pc==0x116a4:return state
        if pc==0x1180a:raise ValueError('Zero-body queue path not modeled here')
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='ld.h':
            if args!='r17, (r4, 0x24)':raise ValueError('Header length address')
            r['r17']=length
        elif op=='bnez':
            if r[p[0]]:pc=int(p[1],0);continue
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='st.w':
            if args!='r3, (r4, 0x170)':raise ValueError('Receive state address')
            state=r['r3']
        elif op=='br':pc=int(args,0);continue
        else:raise ValueError('Header transition instruction '+op)
        pc+=width
    raise ValueError('Header transition bound')


def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x1173c','--stop-address=0x1180a',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    cases=0
    for port in (0,1):
        for length in (1,2,4,255,256,32768,65535):
            payload=bytes([1,2,3,4,length&255,length>>8,0x78,0x56,0x34,0x12])
            for valid in (False,True):
                result=header(port,4,payload,0x12345678 if valid else 0)['result']
                actual=transition(code,result,length)
                if actual!=(2 if valid else 0):raise ValueError('Header next-state mismatch')
                cases+=1
        result=header(port,4,b'abc',0)['result']
        if transition(code,result,0)!=1:raise ValueError('Incomplete header state changed')
        cases+=1
    return {'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded stock header and state transition, CRC modeled. Zero-body queue insertion and subsequent body parsing remain pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-header-transition.json').write_text(json.dumps(report,indent=2)+'\n');print('Header transition cases:',report['decoded_cases'])
