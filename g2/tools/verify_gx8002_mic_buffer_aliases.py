# SPDX-License-Identifier: MIT
"""Microphone output/header alias oracle."""
import json,subprocess
from itertools import product
from build_gx8002_mic_buffer import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_mic_buffer import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
HEADER=0x20040000
OUT=0x20041000

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(w.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x1240c','--stop-address=0x12490',str(w)],text=True));new=decode((ROOT/'build/gx8002-mic-buffer/candidate.disassembly.txt').read_text());cases=0
    for mic,index,address_out,length_out in product((0,1),(0,1,0xffffffff),(OUT,HEADER+8,HEADER+80,HEADER+84),(OUT,OUT+4,HEADER+8,HEADER+80,HEADER+84)):
        total=4096
        m={a+i:0xa5 for a,n in ((HEADER,96),(OUT,16),(0x20070000,4)) for i in range(n)}
        for offset,value in ((8,2),(28,10),(36,1),(32,16000),(80,0x20050000),(84,total)):word(m,HEADER+offset,value)
        args=[HEADER,mic,index,address_out,length_out]
        word(m,0x20070000,args[4]);expected=m.copy();events=[];result=0
        address=(0x20050000+mic*(total//2)+(index%(total//2//320))*320)&0xffffffff
        word(expected,address_out,address);word(expected,length_out,320)
        def helper(t,a,m,e):
            if t!=0x10206c24:raise ValueError('Helper')
            e.append(a[0]);return 0
        for code,entry in ((old,0x1240c),(new,0x10208e80)):
            ret,actual,trace=execute(code,entry,args,m,helper)
            filtered=[x for x in trace if not isinstance(x,tuple) or x[0]!='write_byte']
            if (ret,actual,filtered)!=(('return',result),expected,events):raise ValueError(('Mic mismatch',mic,index,address_out,length_out,hex(entry)))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Output-to-output and output-to-header aliases with independent write-order oracle. Nonzero divisors only; hardware pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-mic-buffer-aliases.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
