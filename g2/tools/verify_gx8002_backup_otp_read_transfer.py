# SPDX-License-Identifier: MIT
"""Ordered finite-transfer qualification of backup OTP-read source."""
import json,subprocess
from itertools import product
from verify_gx8002_backup_otp_read_prefix import execute,build,ROOT,IMAGE,MASK,decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def expected(offset,buffer,length,widths,delay,manufacturer=0x85):
    state=0x20016d60;address=(0xfffff000+offset+7*0x1234)&MASK
    trace=[['read',state+12,0x20028000],['read',0x20028014,0x20028100],['read',0x20028110,7],
           ['read',0x20028108,MASK],['read',0x20028100,0xfffff000],['read',0x20028104,0x1234],
           ['read',0x20028006,manufacturer],['ready',0x10007350,[]],['write',state+16,0x48]]
    command={0:0x48};epoch=0
    def read(a,v):trace.append(['read',a,v])
    def write(a,v):trace.append(['write',a,v&MASK])
    def writes(rows):
        for off,v in rows:write(0xa2000000+off,v)
    def poll(off,busy,ready):
        for _ in range(delay):read(0xa2000000+off,busy)
        read(0xa2000000+off,ready)
    def encode():
        width=widths[epoch%len(widths)];read(state+8,width)
        for i in range(1,5):
            shift=((width-i)*8)&63
            value=(address>>shift)&255 if shift<32 else 0
            command[i]=value;write(state+16+i,value)
        return width
    width=encode();done=0
    while done<length:
        chunk=min(length-done,32)
        poll(0x28,1,0)
        writes([(8,0)]);write(0xa0300090,2)
        writes([(0x4c,0),(0x10,0),(0,0x407),(4,(width+1)&MASK),(0x18,0),(0xf4,0),(8,1)])
        prefix=(width+2)&MASK
        assert prefix<=16
        for i in range(prefix):
            poll(0x28,0,2)
            value=command.get(i,(i*17)&255)
            trace.append(['byte-read',(state+16+i)&MASK,value]);writes([(0x60,value)])
        writes([(0x10,1)])
        poll(0x20,3,0);poll(0x28,1,0)
        writes([(8,0),(0x10,0),(0,0x807),(4,chunk-1),(0x18,0),(0x54,7),(0x4c,1),(8,1),(0x10,1),(0x60,0)])
        for i in range(chunk):
            poll(0x28,0,8)
            value=(0x12348000+(done+i)*73)&MASK
            read(0xa2000060,value);trace.append(['byte-write',(buffer+done+i)&MASK,value&255])
        poll(0x24,2,0);poll(0x28,1,0)
        writes([(8,0),(0x4c,0)]);write(0xa0300090,3);write(0xa0300090,1);writes([(8,1)])
        # Stock reads the new width before writing the updated address bytes.
        done+=chunk;address=(address+chunk)&MASK;epoch+=1;width=encode()
    trace.append(['ready',0x10007350,[]])
    return trace


def verify():
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x40328','--stop-address=0x40514',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-flash-otp-read/otp-read-linked.disassembly.txt').read_text())
    cases=0
    for offset,length,widths,delay,manufacturer in product((0,1,MASK),(1,2,31,32,33,63,64,65,257),
            ((3,),(0,),(4,),(MASK,),(0,3,4,MASK),(4,3,0)),(0,2),(0x5e,0x85)):
        events=expected(offset,0xfffffffe,length,widths,delay,manufacturer)
        for code,entry,delta in ((old,0x40328,0x10000000-0x38940),(new,0x100079e8,0)):
            assert execute(code,entry,delta,offset,0xfffffffe,length,events,seed=0x1234)==length
        cases+=1
    report={'build':evidence,'transfer_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite accepted transfers compare ordered MMIO, state/command accesses, buffer bytes and preserved ABI. Width changes at each observed reload and delayed controller/FIFO readiness covered. Flash ready-wait is normalized to successful status-read completion; real flash, transfer failures and billion-byte signed chunks remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-otp-read-transfer.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(verify()['transfer_cases'])
