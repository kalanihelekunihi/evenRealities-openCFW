#!/usr/bin/env python3
"""Compare Main CQ reservation 0x538ece with locked native code."""
import argparse, hashlib, itertools, json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == SHA
p = argparse.ArgumentParser()
p.add_argument('--elf', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.elf.open('rb') as f:
    elf = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    syms = {s.name: s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
QUEUE, OPS, RING, OUT, RET = 0x20006000, 0x20008000, 0x20009000, 0x2000a000, 0x200ff000
SCENARIOS = ((0x20,0x80,0x100,0,0), (0x70,0x80,0x100,0,0),
             (0x70,0x20,0x80,0,0), (0x70,0x08,0x80,0,0),
             (0x20,0x10,0x100,0,0), (0x20,0x80,0x100,0,255),
             (0x20,0x80,0x100,0xfffffffe,0))

def run(source, scenario, words, valid, reserve_free, outputs, pattern):
    write_offset, head_offset, limit_offset, read_index, index = SCENARIOS[scenario]
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    for address,size in ((QUEUE,0x80),(OPS,0x20),(RING,0x200),(OUT,0x20)):
        cpu.mem_write(address, bytes([pattern])*size)
    cpu.mem_write(QUEUE, (0x01cdcdcd if valid else 0).to_bytes(4,'little'))
    for offset,value in ((4,RING),(8,RING+limit_offset),(12,RING+head_offset),
                         (16,RING+write_offset),(20,RING+write_offset if reserve_free else RING+write_offset+8),
                         (28,read_index),(32,index),(36,OPS)):
        cpu.mem_write(QUEUE+offset, value.to_bytes(4,'little'))
    cpu.mem_write(OPS+4, (0x12345678).to_bytes(4,'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, QUEUE)
    cpu.reg_write(R.UC_ARM_REG_R1, words)
    cpu.reg_write(R.UC_ARM_REG_R2, OUT if outputs != 1 else 0)
    cpu.reg_write(R.UC_ARM_REG_R3, OUT+4 if outputs != 2 else 0)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET|1)
    refresh = syms['g2_main_cq_update_indices_538d18'] if source else 0x538d18
    events=[]
    def hook(machine,pc,_size,_user):
        if pc==RET:
            machine.emu_stop()
        elif pc==refresh:
            events.append(machine.reg_read(R.UC_ARM_REG_R0))
            machine.mem_write(QUEUE+28,read_index.to_bytes(4,'little'))
            machine.mem_write(QUEUE+12,(RING+head_offset).to_bytes(4,'little'))
            machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=syms['g2_main_cq_reserve_538ece'] if source else 0x538ece
    cpu.emu_start(entry|1,RET+2,count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),cpu.reg_read(R.UC_ARM_REG_R1),events,
            bytes(cpu.mem_read(QUEUE,0x80)),bytes(cpu.mem_read(RING,0x200)),
            bytes(cpu.mem_read(OUT,0x20)))

fixtures=list(itertools.product(range(len(SCENARIOS)),(0,1,3),
                                (False,True),(False,True),(0,1,2),(0,0xa5)))
for case,fixture in enumerate(fixtures):
    native=run(False,*fixture)
    candidate=run(True,*fixture)
    if native!=candidate:
        diff=[(field,hex(i),hex(x),hex(y)) for field in range(3,6)
              for i,(x,y) in enumerate(zip(native[field],candidate[field])) if x!=y]
        raise AssertionError((case,fixture,native[:3],candidate[:3],diff[:16]))
report={'status':'PASS_MAIN_MSPI_CQ_RESERVE_NATIVE_SOURCE','cases':len(fixtures),
        'stock_sha256':SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),
        'limits':['Index refresh provider intercepted with controlled head and read-index state; provider separately source-owned.',
                  'Synthetic queue/ring only; concurrent use and physical hardware unverified.',
                  'Full transfer dispatcher remains unresolved.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report['status'],len(fixtures))
