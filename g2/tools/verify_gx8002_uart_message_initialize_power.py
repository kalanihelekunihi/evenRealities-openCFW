# SPDX-License-Identifier: MIT
"""Initialization calls source-built suspend/resume registration functions."""
import json,struct,subprocess
from itertools import product
from compare_gx8002_power_registration import verify as qualify,execute as register
from verify_gx8002_uart_message_initialize import helper_for,oracle
from execute_gx8002_uart_message_initialize import execute,word,BASE
from build_gx8002_uart_message_initialize import ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    dependency=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    power={t:decode(subprocess.check_output([pre,'-d','--section=.text.open_cfw_gx8002_register_'+name,str(ROOT/'build/gx8002-app-tick/suspend-registration.elf')],text=True)) for t,name in ((0x102076c0,'suspend'),(0x10207718,'resume'))}
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x119e4','--stop-address=0x11ad8',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-uart-message-initialize/callback.disassembly.txt').read_text());cases=0;calls=0
    for port,count,match in product((0,1),range(9),(-1,0,7)):
        m={BASE+i:0 for i in range(760)};m.update({0x2002ecc4+i:0 for i in range(20)});config=0x20040000
        for i,v in enumerate((port,115200,0,1)):word(m,config+i*4,v)
        def fresh():
            state=bytearray(144)
            for mode in range(2):
                struct.pack_into('<I',state,8+4*mode,count)
                for i in range(8):struct.pack_into('<II',state,16+64*mode+8*i,0x10300000+i*4,i)
                if match>=0:struct.pack_into('<I',state,16+64*mode+8*match,(0x10207c74,0x10207c9c)[mode])
            base=helper_for(0)
            def helper(t,args,memory,events):
                nonlocal calls,state
                result=base(t,args,memory,events)
                if t not in power:return result
                mode=int(t==0x10207718);counter=8+mode*4;array=16+mode*64
                record=bytes(memory[args[0]+i] for i in range(8));callback=struct.unpack_from('<I',record)[0]
                n=struct.unpack_from('<I',state,counter)[0];index=next((i for i in range(8) if struct.unpack_from('<I',state,array+8*i)[0]==callback),None)
                expected=state.copy();wanted=0xffffffff
                if index is None and n<8:index=n;struct.pack_into('<I',expected,counter,n+1)
                if index is not None:expected[array+8*index:array+8*index+8]=record;wanted=0
                result,updated,_=register(power[t],t,0x10025738,state,record)
                if result!=wanted or updated!=bytes(expected):raise ValueError('Power registration composition')
                state=bytearray(updated);calls+=1;return result
            return helper
        expected=oracle(m,config,fresh())
        for code,entry in ((old,0x119e4),(new,0x10208458)):
            a=execute(code,entry,config,0,m,fresh())
            if (a[0],a[1],[e for e in a[2] if e[0]!='write_byte'])!=expected:raise ValueError('Initialization composition')
        cases+=1
    return {'power_dependency':dependency,'initialization_cases':cases,'registration_executions':calls,'source_admitted':False,'limits':['Decoded source power registrations share separate translated power-state storage across both calls; capacity and replacement checked. Nested memcpy modeled; physical concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-message-initialize-power.json').write_text(json.dumps(r,indent=2)+'\n');print(r['initialization_cases'],r['registration_executions'])
