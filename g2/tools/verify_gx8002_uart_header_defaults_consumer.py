# SPDX-License-Identifier: MIT
"""Whole-entry decoded comparison for the upstream message receive dispatcher."""
import json,subprocess
from itertools import product
from execute_gx8002_uart_receive_callback import execute,word,BASE,MASK
from build_gx8002_uart_header_defaults import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from gx8002_uart_receive_callback_oracle import oracle
POINTER=0x2002e5d8
BUFFER=0x2002e520

def helper_for(data,body_result,crc_valid,queue_result):
    def helper(target,args,memory,events):
        a,b,c,d=args
        if target==0x10207ac0:
            events.append(('get',a));return {0:BASE,1:BASE+380}.get(a,0)
        if target==0x102035d8:
            events.append(('read',a,b,c));assert b==BUFFER and c==len(data)
            for i,value in enumerate(data):memory[b+i]=value
            return len(data)
        if target==0x102098a8:
            events.append(('crc',a,b,c,bytes(memory[b+i] for i in range(c)).hex()))
            return word(memory,b+10)^(0 if crc_valid else MASK)
        if target==0x10207cec:
            events.append(('body',a,b,c,word(memory,d)));word(memory,d,0);return body_result
        if target==0x100261b8:
            events.append(('queue',a,b,bytes(memory[b+i] for i in range(32)).hex()));return queue_result
        raise ValueError(('Unknown helper',hex(target)))
    return helper

def verify():
    candidate=build();d=Elf32((ROOT/'build/gx8002-uart-header-defaults/defaults.elf').read_bytes(),'defaults');initial=d.contents(next(s for s in d.sections if s['name']=='.header_counts'));pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11624','--stop-address=0x11838',str(wrapper)],text=True));path=ROOT/'build/gx8002-source-candidate/uart-receive-callback/callback.elf';elf=Elf32(path.read_bytes(),'callback');report=json.loads((ROOT/'docs/research/gx8002-uart-receive-callback-source-verification.json').read_text())
    for section in elf.sections:
        if section['flags']&2 and section['size']:assert any(row.get('compiled_sha256')==sha(elf.contents(section)) for row in report['functions'])
    new=decode(subprocess.check_output([pre+'objdump','-d',str(path)],text=True));cases=0
    for port,state,length,header_count,vef_count,pattern in product((0,1),range(5),(0,1,3,4,10,14,32,64),(int.from_bytes(initial[:4],'little'),),(0,1,3),range(3)):
        ctx=BASE+380*port;memory={BASE+i:(i*37)&255 for i in range(1440)}
        memory.update({0x20026c74+i:v for i,v in enumerate(initial)})
        word(memory,ctx+368,state);word(memory,0x20026c74+port*4,header_count);word(memory,0x2002e5dc+port*4,vef_count)
        word(memory,ctx,0x12345678);word(memory,ctx+28,0x12345678 if pattern==0 else 0)
        memory[ctx+35]=pattern;memory[ctx+36]=0 if pattern==0 else 8;memory[ctx+37]=0
        data=bytes((0x78,0x56,0x34,0x12)[i%4] if pattern==1 else (i*17+pattern)&255 for i in range(length))
        helper=helper_for(data,(0,1,MASK)[cases%3],cases%2,(0,1,MASK)[cases%3])
        a=execute(old,0x11624,port,length,memory,helper);b=execute(new,0x10208098,port,length,memory,helper)
        # Store widths/order can differ; compare final bytes plus every helper boundary.
        aa=(a[0],a[1],[e for e in a[2] if e[0]!='write_byte']);bb=(b[0],b[1],[e for e in b[2] if e[0]!='write_byte'])
        expected=oracle(port,length,memory,helper)
        if aa!=bb or aa!=expected:
            changed=[(hex(k),a[1].get(k),b[1].get(k)) for k in set(a[1])|set(b[1]) if a[1].get(k)!=b[1].get(k)]
            raise ValueError(('Mismatch',port,state,length,header_count,vef_count,pattern,a[0],b[0],aa[2],bb[2],expected[2],changed[:20],[(hex(k),a[1].get(k),expected[1].get(k)) for k in set(a[1])|set(expected[1]) if a[1].get(k)!=expected[1].get(k)][:20]))
        assert word(a[1],0x20026c74+(1-port)*4)==4 and word(b[1],0x20026c74+(1-port)*4)==4
        cases+=1
    return {'candidate':candidate,'consumer_elf_sha256':sha(path.read_bytes()),'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Compiled per-port counter defaults feed whole-entry stock/source comparison and independent oracle. Nonselected port counter remains four. Checks final nonstack memory and helper boundaries. UART/CRC/body/queue modeled. Independent semantic oracle also checked; helper mutations and nested helper execution remain pending; not source admission.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-header-defaults-consumer.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'])
