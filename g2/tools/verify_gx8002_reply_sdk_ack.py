# SPDX-License-Identifier: MIT
"""Qualify acknowledgement and its intentional persistent-payload correction."""
import json,subprocess
from itertools import product
from build_gx8002_i2s_ack import ROOT,IMAGE_SHA,sha,Elf32
from probe_gx8002_reply_sdk_types import probe as build
from execute_gx8002_i2s_ack import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12cfc','--stop-address=0x12d28',str(p)],text=True))
    new=decode((ROOT/'build/gx8002-reply-sdk-types/i2s_ack.disassembly.txt').read_text())
    base=0x20026d5c;constant=0x102093d8;cases=0
    for seed,result,mutate in product((0,0x55,0xff),(0,1,0xffffffff),(False,True)):
        for code,entry,pointer in ((old,0x12cfc,0x2006fffb),(new,0x10209770,constant)):
            memory={base+i:seed for i in range(32)};memory[constant]=1
            expected=memory.copy();trace=[]
            for address,value,size in ((base+16,pointer,4),(base+4,271,2),(base+7,1,1),(base+24,1,4)):
                for i in range(size):
                    expected[address+i]=(value>>(8*i))&255
                    trace.append(('write_byte',address+i,expected[address+i]))
            trace.append(('enqueue',base,pointer,1))
            if mutate:word(expected,base+24,7)
            def helper(t,a,m,e):
                assert t==0x102083bc and a[0]==base
                queued=word(m,base+16);assert m[queued]==1
                e.append(('enqueue',a[0],queued,m[queued]))
                # Queue retains the address: overwrite expired caller scratch.
                for address in range(0x2006fff8,0x2006fffc):m[address]=0x7e
                assert m[queued]==(0x7e if entry<0x100000 else 1)
                if mutate:word(m,base+24,7)
                return result
            ret,m,events=execute(code,entry,[],memory,helper)
            # Source has no scratch; helper's simulated later stack reuse is external.
            m={k:v for k,v in m.items() if not 0x2006fff8<=k<0x2006fffc}
            assert ret[0]=='return' and m==expected and events==trace,(ret,m,expected,events,trace)
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Payload lifetime intentionally fixed using shared immutable byte; original stack payload corrupts under reuse. Helper boundary, writes and integer ABI checked; nested DMA and hardware unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-reply-sdk-ack-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
