#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check backup command writes and inline TX-empty/idle polling."""
import contextlib
import io
import json
import struct
import subprocess
from verify_gx8002_backup_spi_read import execute,build,ROOT,IMAGE,decode


def oracle(command,buffer,count,delay):
    status=0xa2000028
    events=[['read',status,1]]*delay+[['read',status,0]]
    events += [['write',0xa2000000+off,value] for off,value in [(8,0),(0x10,0),(0x4c,0),(0,0x407),(4,count),(0x10,1),(0x18,(count<<16)&0xffffffff),(0xf4,0),(8,1),(0x60,command)]]
    for i in range(count):
        byte=(i*71+255)&255
        events += [['read',status,0]]*delay+[['read',status,2],['buffer-read',buffer+i,byte],['write',0xa2000060,byte]]
    events += [['read',0xa2000020,3]]*delay+[['read',0xa2000020,0]]
    events += [['read',status,1]]*delay+[['read',status,0]]
    return events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-backup-flash-transport';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'write-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x3f5f0','--stop-address=0x3f674',str(w)],text=True))
    new=decode((out/'transport-linked.disassembly.txt').read_text());cases=0
    for command in (0,6,17,255,0xffffffff):
        for count in range(257):
            for buffer in ((0,0x20028000,0x20028001) if count==0 else (0x20028000,0x20028001)):
                for delay in (0,1,3):
                    events=oracle(command,buffer,count,delay)
                    if execute(old,0x3f5f0,command,buffer,count,events,0x0ffc76c0)!=0 or execute(new,0x10006cb0,command,buffer,count,events,0)!=0:raise ValueError('write return mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['All counts 0..256 with valid nonwrapping buffers; NULL only at count zero. Larger counts and other address domains remain unqualified.', 'Finite hardware readiness schedules; no hardware timing or liveness claim.']}
    (ROOT/'docs/research/gx8002-backup-spi-write-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
