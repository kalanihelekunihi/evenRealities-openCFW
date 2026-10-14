#!/usr/bin/env python3
"""Recheck Main MSPI transfer selector 26 clock mode against native code."""
import argparse, hashlib, itertools, json, random
from collections import Counter
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R

ROOT=Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
    elf=ELFFile(f)
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
    syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
HANDLE,CFG,MMIO,RET=0x20006000,0x20008000,0x40060000,0x200ff000
NATIVE={0x4c0758:'route',0x4c4530:'release',0x4c44bc:'acquire',0x4c07d0:'finish'}
SOURCE={syms[name]:label for name,label in (
    ('g2_main_mspi_clock_route_4c0758','route'),
    ('g2_main_mspi_clock_release_4c4530','release'),
    ('g2_main_mspi_clock_acquire_4c44bc','acquire'),
    ('g2_main_mspi_configure_finish_4c07d0','finish'))}

def run(source,module,mode,previous,ready,release_result,acquire_result,pattern,valid=True,enabled=True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
    cpu.mem_map(0x800000,0x10000)
    for address,body in segments:cpu.mem_write(address,body)
    cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000)
    cpu.mem_write(MMIO,bytes([pattern])*0x4000)
    cpu.mem_write(HANDLE,bytes([pattern])*0x900)
    cpu.mem_write(HANDLE,(0x01bebebe if valid else 0).to_bytes(4,'little'))
    cpu.mem_write(HANDLE+4,module.to_bytes(4,'little'))
    cpu.mem_write(HANDLE+8,bytes([int(enabled)]))
    cpu.mem_write(HANDLE+0x18,ready.to_bytes(4,'little'))
    cpu.mem_write(HANDLE+0x8c9,bytes([previous]))
    cpu.mem_write(CFG,bytes([mode])+bytes(15))
    cpu.reg_write(R.UC_ARM_REG_R0,HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1,CFG if source else 26)
    cpu.reg_write(R.UC_ARM_REG_R2,CFG)
    cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
    helpers=SOURCE if source else NATIVE;events=[]
    def hook(machine,pc,_size,_user):
        if pc==RET:machine.emu_stop();return
        if pc not in helpers:return
        label=helpers[pc]
        args=tuple(machine.reg_read(reg) for reg in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3))
        events.append((label,args[:4] if label=='route' else args[:2] if label in ('release','acquire') else args[:1]))
        result=release_result if label=='release' else acquire_result if label=='acquire' else 0x77
        machine.reg_write(R.UC_ARM_REG_R0,result)
        machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=syms['g2_main_mspi_transfer_mode26_candidate'] if source else 0x4c0f78
    cpu.emu_start(entry|1,RET+2,count=20000)
    assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),events,
            bytes(cpu.mem_read(HANDLE,0x900)),bytes(cpu.mem_read(MMIO,0x4000)))

all_cases=list(itertools.product(range(4),range(0,32),(0,4,5),(0,1),(0,4),(0,5),(0,0xa5)))
fixtures=random.Random(527).sample(all_cases,1500)
fixtures += list(itertools.product(range(4),range(0,25),(4,5),(0,1),(0,),(0,),(0,0xa5)))
paths=Counter()
for index,fixture in enumerate(fixtures):
    native=run(False,*fixture);candidate=run(True,*fixture)
    paths['>'.join(event[0] for event in native[1]) or 'validation_only']+=1
    if native!=candidate:
        handle_diff=[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(native[2],candidate[2])) if x!=y]
        mmio_diff=[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(native[3],candidate[3])) if x!=y]
        raise AssertionError((index,fixture,native[:2],candidate[:2],handle_diff[:12],mmio_diff[:12]))
validation=[(0,1,4,0,0,0,0,False,True),(0,1,4,0,0,0,0,True,False)]
for fixture in validation:
    native=run(False,*fixture);candidate=run(True,*fixture)
    paths['>'.join(event[0] for event in native[1]) or 'validation_only']+=1
    if native!=candidate:raise AssertionError(('validation',fixture,native[:2],candidate[:2]))
assert paths['validation_only']>0
assert any('route>release>acquire>route>finish' in path for path in paths)
report={'status':'PASS_MAIN_MSPI_TRANSFER_SELECTOR26_DEEP_NATIVE_SOURCE','cases':len(fixtures)+len(validation),
        'provider_event_paths':dict(sorted(paths.items())),'stock_sha256':SHA,
        'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),
        'limits':['Clock route, release/acquire and finish providers intercepted; each source-owned separately.',
                  'Synthetic MMIO; physical clock transition unverified.',
                  'Selector 26 only; full transfer dispatcher remains unresolved.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report['status'],report['cases'])
