#!/usr/bin/env python3
"""Compare stock 0x0800d154 and source output-enable wrapper at setter cut."""
from pathlib import Path
import hashlib, itertools, json
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

D = Path(__file__).resolve().parent
root = D.parents[2]
blob = (root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest() == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw = blob[32:]
elf = D/'binary_3f_enable.elf'
with elf.open('rb') as f:
    e = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
    sym = {s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

rows = []
for seed, initial in itertools.product([0, 1, 0x12345678, 0xffffffff], [0, 0x60000000]):
    pair = []
    for original in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
        u.mem_map(0x08000000, (len(raw)+4095)&~4095); u.mem_write(0x08000000,raw)
        u.mem_map(0x20000000,0x10000); u.mem_map(0x00100000,0x10000)
        for a,b in segments: u.mem_write(a,b)
        u.reg_write(UC_ARM_REG_R0,initial); u.reg_write(UC_ARM_REG_SP,0x20008000)
        u.reg_write(UC_ARM_REG_LR,0x20001001)
        calls = []
        def hook(uc,a,size,_):
            if a in (0x080099e8,0x0010f000):
                calls.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)])
                uc.reg_write(UC_ARM_REG_R0,(seed+len(calls)*0x11111111)&0xffffffff)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((0x0800d154 if original else sym['case_binary_3f_enable'])|1,0x20001000,count=1000)
        row = [calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PC)]
        assert row[2] == 0x20001000,row
        pair.append(row)
    assert pair[0] == pair[1],(seed,initial,pair)
    assert pair[0][0] == [[3,0xae],[4,0xae],[5,3],[6,0x81]],pair
    rows.append([seed,initial,pair[0]])
out = dict(status='PASS_BINARY_3F_ENABLE_WRAPPER',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_3f_enable_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Setter 0x080099e8 is controlled, not sourced.','Physical output effects are unverified.','Isolated child; not a public binary command provider.'],rows=rows)
(D/'binary-3f-enable-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],len(rows))
