#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted stock/upstream queue-write comparison; no source admission yet."""
import json
import subprocess
from compare_gx8002_queue_get import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_queue_source import verify, ROOT
from verify_gx8002_analog_source import FLAGS, sha
from analyze_gx8002_upstream_objects import IMAGE
from build_transparent_image import Elf32

def verify_put(prefix=None, sdk=None, output=None):
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = output or ROOT / 'build/gx8002-queue-put'
    authentication = verify(prefix, sdk, output)
    flags = ['-Os', *FLAGS[1:], '-fno-ivopts']
    obj = output / 'queue-size.o'
    subprocess.run([str(prefix/'csky-unknown-elf-gcc'), *flags, '-I', str(output), '-I', str(sdk/'include'),
                    '-c', str(sdk/'lvp/common/lvp_queue.c'), '-o', str(obj)], check=True)
    candidate = decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'), '-dr',
                        '--section=.sram_text', str(obj)], text=True))
    # Authenticated by verify(); wrapper is analysis-only.
    import struct
    wrapper = output/'stock.elf'
    subprocess.run([str(prefix/'csky-unknown-elf-objcopy'), '-I', 'binary', '-O', 'elf32-csky-little',
                    '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    original = decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'), '-D',
                      '--start-address=0x181cc','--stop-address=0x18226',str(wrapper)],text=True))
    cases=0
    for member in (1,2,3,4,8,16):
        for slots in (2,3,8,17):
            size=member*slots
            for head in range(0,size,member):
                for tail in range(0,size,member):
                    memory={0x2000+i:(i*73+19)%256 for i in range(size)}
                    memory.update({0x3000+i:(i*37+81)%256 for i in range(member)})
                    for offset,value in enumerate((tail,head,0x2000,size,member)):
                        for i in range(4):memory[0x1000+offset*4+i]=(value>>(i*8))&255
                    before=memory.copy()
                    other=memory.copy()
                    a,at=execute(original,memory,0x181cc)
                    b,bt=execute(candidate,other,0)
                    if a!=b or memory!=other or at!=bt:raise ValueError('stock/upstream execution mismatch')
                    expected=before.copy()
                    full=(tail+member)%size==head
                    if not full:
                        for i in range(member):expected[0x2000+(tail+i)%size]=before[0x3000+i]
                        new_tail=(tail+member)%size
                        for i in range(4):expected[0x1000+i]=(new_tail>>(8*i))&255
                    if a!=int(not full) or memory!=expected:raise ValueError('independent FIFO oracle mismatch')
                    cases+=1
    elf=Elf32(obj.read_bytes(),str(obj));section=next(s for s in elf.sections if s['name']=='.sram_text')
    if section['size'] > 90 or 0x181cc % section['align'] or elf.relocations(section['index']):
        raise ValueError('queue read placement or relocation changed')
    report={'symbol':'LvpQueuePut', 'section_name':'.sram_text', 'stock_occurrences':[{'symbol':'LvpQueuePut', 'package_offset':0x181cc,
             'bytes':90, 'sha256':sha(IMAGE.read_bytes()[0x181cc:0x18226]), 'region':'image_a_sram_text'}],
            'upstream_files':authentication['upstream_files'],'compile_flags':flags,'cases':cases,
            'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
            'exact_memory_trace_comparison':True,'source_admitted':True,
            'limits':['Finite valid queue states, no concurrent mutation or aliasing.','Not a full processor emulator; experimental same-entry placement; no hardware qualification.']}
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(verify_put(),indent=2))
