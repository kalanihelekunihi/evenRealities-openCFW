#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify recovered VAD curves against original C-SKY register-access traces."""
import argparse
import json
import random
import re
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_vad_curves.c'


def decode(objdump, path, name):
    text = subprocess.check_output([str(objdump), '-dr', '-j', '.text.'+name, str(path)], text=True)
    result = {}
    for line in text.splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([\w.]+)\s*(.*?)\s*$', line)
        if match:
            result[int(match[1],16)] = (len(match[2])//2, match[3], match[4].split('//')[0].strip())
    return result


def execute(code, a, b, readbacks):
    registers = {'r0':a & 0xffffffff, 'r1':b & 0xffffffff, 'r2':0xdead1234, 'r3':0xbeef5678}
    pc, condition, trace, read_index = 0, False, [], 0
    for _ in range(64):
        length, op, operand = code[pc]
        parts = [p.strip() for p in operand.split(',')]
        next_pc = pc+length
        if op in ('movi', 'movih', 'lrw'):
            registers[parts[0]] = int(parts[1],0) << (16 if op=='movih' else 0)
        elif op == 'cmphsi':
            condition = registers[parts[0]] >= int(parts[1],0)
        elif op == 'bt':
            if condition: next_pc=int(parts[0],0)
        elif op == 'br':
            next_pc=int(parts[0],0)
        elif op == 'zexth':
            registers[parts[0]]=registers[parts[1]] & 0xffff
        elif op == 'lsli':
            registers[parts[0]]=(registers[parts[1]] << int(parts[2],0)) & 0xffffffff
        elif op == 'addu':
            if len(parts)!=2: raise ValueError('unsupported add')
            registers[parts[0]]=(registers[parts[0]]+registers[parts[1]]) & 0xffffffff
        elif op == 'subi':
            if len(parts)!=2: raise ValueError('unsupported subtract')
            registers[parts[0]]=(registers[parts[0]]-int(parts[1],0)) & 0xffffffff
        elif op == 'ins':
            high,low=int(parts[2],0),int(parts[3],0)
            if not 0<=low<=high<32: raise ValueError('invalid insert field')
            mask=((1<<(high-low+1))-1)<<low
            registers[parts[0]]=(registers[parts[0]] & ~mask) | ((registers[parts[1]]<<low)&mask)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r[0-3]), \((r[0-3]), (0x[0-9a-f]+)\)',operand)
            if not match: raise ValueError('unsupported memory operand')
            reg,base,offset=match.groups()
            address=registers[base]+int(offset,0)
            if address not in range(0xa0a00184,0xa0a00198,4): raise ValueError('unexpected MMIO address')
            if op=='ld.w':
                if read_index>=len(readbacks): raise ValueError('too many reads')
                registers[reg]=readbacks[read_index]
                read_index+=1
                trace.append(('read32',address,registers[reg]))
            else:
                trace.append(('write32',address,registers[reg]))
        elif op=='rts':
            return registers['r0'],trace
        else:
            raise ValueError(f'unsupported instruction: {op}')
        pc=next_pc
    raise ValueError('execution limit exceeded')


def verify(prefix,sdk,output):
    candidates=analyze(sdk)
    output.mkdir(parents=True,exist_ok=True)
    obj=output/'runtime_gx8002_vad_curves.o'
    subprocess.run([str(prefix/'csky-unknown-elf-gcc'),*FLAGS,'-c',str(SOURCE),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj))
    if any(s['name'] and s['section']==0 for s in elf.symbols()): raise ValueError('undefined symbol')
    objdump=prefix/'csky-unknown-elf-objdump'
    results=[]
    boundary=(0,1,3072,3073,4096,4097,5119,5120,5121,7680,7681,8192,8193,17920,17921,32767,32768,60415,60416,65535)
    rng=random.Random(0x8002)
    pairs=[(a,b) for a in boundary for b in boundary]
    pairs += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(4096)]
    for curve in range(1,6):
        name=f'gx_audio_in_set_fftvad_curve_{curve}'
        section=next(s for s in elf.sections if s['name']=='.text.'+name)
        matches=[m for m in candidates['matches'] if m['symbol']==name]
        if not matches or any(section['size']>m['bytes'] or m['package_offset']%section['align'] for m in matches):
            raise ValueError('placement size/alignment mismatch')
        if elf.relocations(section['index']): raise ValueError('unexpected relocation')
        before=decode(objdump,sdk/'drivers_lib/audio_in/v2.0/audio_in.o',name)
        after=decode(objdump,obj,name)
        for a,b in pairs:
            if curve==3:
                a=a if a<32768 else a-65536
                b=b if b<32768 else b-65536
            # Different readbacks force preservation of distinct MMIO cycles.
            readbacks=(rng.getrandbits(32),rng.getrandbits(32))
            old,new=execute(before,a,b,readbacks),execute(after,a,b,readbacks)
            if old!=new: raise ValueError(f'{name}: differing hardware trace for {(a,b)}')
            expected_ops=[] if new[0]==0xffffffff else ['read32','write32']*(1 if curve==5 else 2)
            if new[0] not in (0,0xffffffff) or [t[0] for t in new[1]]!=expected_ops:
                raise ValueError('unexpected return/MMIO sequence')
        results.append({'symbol':name,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
                        'compiled_alignment':section['align'],'stock_occurrences':matches,'matching_cases':len(pairs),
                        'abi':'signed int16 arguments' if curve==3 else 'unsigned uint16 arguments'})
    report={'source_sha256':sha(SOURCE.read_bytes()),'compile_flags':FLAGS,'functions':results,
            'compiled_function_bytes':sum(r['compiled_bytes'] for r in results),
            'differential_cases':len(pairs)*5,'firmware_bytes_emitted':0,'hardware_qualified':False,
            'limits':['Finite trace comparison, not an all-input proof or hardware model.',
                      'Two independent MMIO readbacks are preserved for accepted pairs.',
                      'Smaller generated functions require explicit envelope ownership.']}
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix',type=Path,default=ROOT/'build/csky-macos/install/bin')
    p.add_argument('--sdk',type=Path,default=ROOT/'build/upstream-nationalchip-lvp-kws')
    p.add_argument('--output',type=Path,default=ROOT/'build/gx8002-vad-source')
    a=p.parse_args()
    print(json.dumps(verify(a.prefix.resolve(),a.sdk.resolve(),a.output.resolve()),indent=2))


if __name__=='__main__': main()
