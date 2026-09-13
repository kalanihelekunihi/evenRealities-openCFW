# SPDX-License-Identifier: MIT
"""Decode UART receive setup through reconstructed cache invalidation."""
import json,subprocess
from itertools import product
from verify_gx8002_dcache_invalid_signed import verify as qualify
from verify_gx8002_dcache_invalid_range import execute as invalidate,expected,ADDRESS,ROOT
from verify_gx8002_uart_receive_dma import execute
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-uart-receive-dma/dma.elf'
    report_path=ROOT/'docs/research/gx8002-uart-receive-dma-source-verification.json'
    report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'uart-dma')
    for row in report.get('functions',[report]):
        sec=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(stock.read_bytes(),'stock')
    assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc71c','--stop-address=0xc7a8',str(stock)],text=True))
    caller=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    callee=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/dcache-invalid-range-candidate.elf')],text=True))
    cases=0;calls=0
    for port,channel,buffer,length in product((0,1,2),(0,3,0xffffffff),(0x20060000,0x2006000f,0xfffffff1),(0,1,16,127,128,129,0x80000000,0xffffffff)):
        traces=[]
        def cache(pointer,size):
            assert (pointer,size)==(buffer,length)
            trace,done=invalidate(callee,ADDRESS,pointer,size,0x12345678)
            assert done and trace==expected(pointer,size)
            traces.append(trace)
        args=(port,0x20050000,32,channel,0,1,0xffffffff)
        reference=execute(old,0xc71c,*args,cache_buffer=buffer,cache_length=length)
        result=execute(caller,0x10203190,*args,cache_hook=cache,cache_buffer=buffer,cache_length=length)
        assert result==reference
        assert len(traces)==sum(event[0]=='cache' for event in reference[1])
        calls+=len(traces);cases+=1
    return {'evidence':evidence,'caller_elf_sha256':sha(path.read_bytes()),'caller_report_sha256':sha(report_path.read_bytes()),'composed_cases':cases,'decoded_cache_calls':calls,'source_admitted':False,'limits':['Decoded UART setup output/state/order matched stock while invoking source cache invalidation. Channel selection, burst, callback and transfer services modeled; no physical DMA/cache-coherence qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-invalid-uart.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'],r['decoded_cache_calls'])
