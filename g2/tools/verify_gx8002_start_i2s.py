# SPDX-License-Identifier: MIT
"""I2S startup independent helper trace/configuration and state oracle."""
import json,subprocess
from itertools import product
from build_gx8002_start_i2s import build,ROOT,IMAGE_SHA,sha,Elf32,DIAGNOSTICS
from execute_gx8002_start_i2s import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
APP=0x2002e8c4
PENDING=0x20026d34

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x1257c','--stop-address=0x126c8',str(path)],text=True));new=decode((ROOT/'build/gx8002-start-i2s/candidate.disassembly.txt').read_text())
    targets={a:n.removeprefix('open_cfw_gx8002_i2s_') for n,a in candidate['bindings'].items() if n.startswith('open_cfw_gx8002_i2s_')};diagnostics={a:n for n,(a,t) in DIAGNOSTICS.items()};cases=0
    for enabled,handle,size,result in product((0,1,0xffffffff),(0,7,0xffffffff),(0,1,640,0x7fffffff,0x80000000,0xffffffff),(0,0xffffffff)):
        m={APP+i:0xa5 for i in range(32)};m[PENDING]=7;word(m,APP+20,enabled);word(m,APP+4,handle);expected=m.copy()
        wanted=[('print','log',DIAGNOSTICS['name'][0],277)]
        half=abs(size if size<0x80000000 else size-0x100000000)//2
        if size>=0x80000000:half=(-half)&0xffffffff
        if not enabled:
            word(expected,APP+20,1);expected[PENDING]=1;word(expected,APP+4,result);word(expected,APP,half);word(expected,APP+24,0x20050000);word(expected,APP+28,(0x20051000+half)&0xffffffff)
            if handle!=0xffffffff:wanted.extend([('print','close_log',DIAGNOSTICS['name'][0],290,handle),('close',handle),('shutdown',)])
            wanted.extend([('padmux',i,3) for i in range(7,11)])
            wanted.extend([('clock_set',8,5),('initialize',0),('clock_get',11),('open',0),('callback',result,0x10208d98,0),('mode',result,0),('buffer_size',),('channel',result,0),('buffer_base',),('buffer_base',),('buffers',result,0x20050000,(0x20051000+half)&0xffffffff,half),('format',result,16000,2,16,0,0,24576000),('clock_get',11),('print','mclk',24576000),('print','lrclk',16000),('print','bits',16),('print','done',DIAGNOSTICS['master'][0])])
        for code,entry in ((old,0x1257c),(new,0x10208ff0)):
            bases=[0]
            def helper(t,a,mem,events,sp):
                if t==0x10206c24:
                    name=diagnostics[a[0]];count=3 if name=='close_log' else 2 if name=='log' else 1
                    events.append(('print',name,*a[1:1+count]));return result
                name=targets[t]
                if name in ('callback','buffers'):events.append((name,a[0],*[word(mem,a[1]+4*i) for i in range(2 if name=='callback' else 3)]))
                elif name=='format':events.append((name,a[0],word(mem,a[1]),*[mem[a[1]+i] for i in range(4,8)],word(mem,a[1]+8)))
                else:
                    count=0 if name in ('shutdown','buffer_size','buffer_base') else 2 if name in ('padmux','clock_set','mode','channel') else 1
                    events.append((name,*a[:count]))
                if name=='clock_get':return 24576000
                if name=='buffer_size':return size
                if name=='buffer_base':value=0x20050000+bases[0]*4096;bases[0]+=1;return value
                return result
            ret,actual,events=execute(code,entry,[],m,helper);events=[e for e in events if e[0]!='write_byte']
            if (ret,actual,events)!=(('return',0xffffffff if enabled else 0),expected,wanted):raise ValueError(('Startup mismatch',enabled,handle,size,result,hex(entry),ret,events,wanted))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent baseline checks helper inputs, configuration layouts, signed halving, return failures and integer ABI; helper mutations remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-start-i2s-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
