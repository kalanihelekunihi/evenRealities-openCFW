#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted execution comparison of stock and upstream queue-read code."""
import json
import re
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_queue_source import verify, ROOT
from verify_gx8002_analog_source import FLAGS, sha
from analyze_gx8002_upstream_objects import IMAGE
from build_transparent_image import Elf32


def signed(value):
    return value if value < 0x80000000 else value - 0x100000000


def execute(code, memory, start):
    registers = {f'r{i}': 0x98760000+i for i in range(32)}
    registers.update(r0=0x1000, r1=0x3000)
    pc, condition = start, False
    trace = []
    for _ in range(10000):
        op, args, width = code[pc]
        parts = [p.strip() for p in args.split(',')]
        next_pc = pc + width
        if op == 'mov': registers[parts[0]] = registers[parts[1]]
        elif op == 'movi': registers[parts[0]] = int(parts[1], 0)
        elif op in ('cmpne', 'cmplt'):
            a, b = (registers[p] for p in parts)
            condition = a != b if op == 'cmpne' else signed(a) < signed(b)
        elif op in ('bt', 'bf', 'br'):
            if op == 'br' or (condition if op == 'bt' else not condition): next_pc = int(parts[0], 0)
        elif op in ('addu', 'subu', 'mult', 'divs', 'addi'):
            a = registers[parts[0] if len(parts) == 2 else parts[1]]
            b = int(parts[-1], 0) if op == 'addi' else registers[parts[-1]]
            if op in ('addu', 'addi'): result = a + b
            elif op == 'subu': result = a - b
            elif op == 'mult': result = a * b
            else:
                a, b = signed(a), signed(b)
                if not b: raise ValueError('division by zero')
                result = (abs(a) // abs(b)) * (-1 if (a < 0) != (b < 0) else 1)
            registers[parts[0]] = result & 0xffffffff
        elif op in ('ld.w', 'st.w', 'ldr.b', 'str.b', 'stbi.b', 'ldbi.b'):
            m = re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+)|(, r\d+ << 0))?\)', args)
            if not m: raise ValueError('unsupported memory operand: '+args)
            value, base, immediate, indexed = m.groups()
            offset = registers[indexed.split()[1]] if indexed else int(immediate or '0', 0)
            address = registers[base] + offset
            size = 4 if op.endswith('.w') else 1
            reading = op.startswith('ld')
            if any(address+i not in memory for i in range(size)): raise ValueError('out-of-bounds access')
            trace.append(('read' if reading else 'write', address, size))
            if reading: registers[value] = sum(memory[address+i] << (i*8) for i in range(size))
            else:
                for i in range(size): memory[address+i] = (registers[value] >> (i*8)) & 255
            if op in ('stbi.b', 'ldbi.b'): registers[base] += 1
        elif op == 'rts': return registers['r0'], trace
        else: raise ValueError('unsupported instruction: '+op)
        pc = next_pc
    raise ValueError('execution bound exceeded')


def verify_get(prefix=None, sdk=None, output=None):
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = output or ROOT / 'build/gx8002-queue-get'
    authentication = verify(prefix, sdk, output)
    flags = ['-Os', *FLAGS[1:], '-fno-ivopts']
    obj = output / 'queue-size.o'
    subprocess.run([str(prefix/'csky-unknown-elf-gcc'), *flags, '-I', str(output), '-I', str(sdk/'include'),
                    '-c', str(sdk/'lvp/common/lvp_queue.c'), '-o', str(obj)], check=True)
    candidate = decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'), '-dr',
                        '--section=.text.LvpQueueGet', str(obj)], text=True))
    # Authenticated by verify(); wrapper is analysis-only.
    import struct
    wrapper = output/'stock.elf'
    subprocess.run([str(prefix/'csky-unknown-elf-objcopy'), '-I', 'binary', '-O', 'elf32-csky-little',
                    '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    original = decode(subprocess.check_output([str(prefix/'csky-unknown-elf-objdump'), '-D',
                      '--start-address=0x1053c','--stop-address=0x10586',str(wrapper)],text=True))
    cases=0
    for member in (1,2,3,4,8,16):
        for slots in (2,3,8,17):
            size=member*slots
            for head in range(0,size,member):
                for tail in range(0,size,member):
                    memory={0x2000+i:(i*73+19)%256 for i in range(size)}
                    memory.update({0x3000+i:0xa5 for i in range(member)})
                    for offset,value in enumerate((tail,head,0x2000,size,member)):
                        for i in range(4):memory[0x1000+offset*4+i]=(value>>(i*8))&255
                    before=memory.copy()
                    other=memory.copy()
                    a,at=execute(original,memory,0x1053c)
                    b,bt=execute(candidate,other,0)
                    if a!=b or memory!=other or at!=bt:raise ValueError('stock/upstream execution mismatch')
                    expected=before.copy()
                    if head!=tail:
                        for i in range(member):expected[0x3000+i]=before[0x2000+(head+i)%size]
                        new_head=(head+member)%size
                        for i in range(4):expected[0x1004+i]=(new_head>>(8*i))&255
                    if a!=int(head!=tail) or memory!=expected:raise ValueError('independent FIFO oracle mismatch')
                    cases+=1
    elf=Elf32(obj.read_bytes(),str(obj));section=next(s for s in elf.sections if s['name']=='.text.LvpQueueGet')
    if section['size'] > 74 or 0x1053c % section['align'] or elf.relocations(section['index']):
        raise ValueError('queue read placement or relocation changed')
    report={'symbol':'LvpQueueGet', 'stock_occurrences':[{'symbol':'LvpQueueGet', 'package_offset':0x1053c,
             'bytes':74, 'sha256':sha(IMAGE.read_bytes()[0x1053c:0x10586]), 'region':'image_a_xip_text'}],
            'upstream_files':authentication['upstream_files'],'compile_flags':flags,'cases':cases,
            'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
            'exact_memory_trace_comparison':True,'source_admitted':True,
            'limits':['Finite valid queue states, no concurrent mutation or aliasing.','Not a full processor emulator; experimental same-entry placement; no hardware qualification.']}
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(verify_get(),indent=2))
