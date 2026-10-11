#!/usr/bin/env python3
"""Verify stock RX event callback binding and no-op body."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
assert fw[32+0x5e6a:32+0x5e6c]==b'\x70\x47'
for n in ('08008758.c','08008998.c'):
    p=R/'g2/research/corpus/case/ghidra/open-2026-09-29/decomp'/n
    assert 'FUN_08005e6a(param_1,(short)param_1[0x17])' in p.read_text()
src=R/'g2/components/case/source_candidate_20261010/uart_event_callback.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__uart_event_callback.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'callback.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
elfpath=H/'callback.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','HAL_UARTEx_RxEventCallback',str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='HAL_UARTEx_RxEventCallback')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(original,uart,size,primask):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(uart,size,0x11223344,0x55667788)):u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    u.emu_start(0x08005e6b if original else entry|1,0x20000000,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000000
    return ([u.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],
            bytes(u.mem_read(0x20000000,0x10000)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0,0x20000e24,0x20004000,0xffffffff),(0,1,255,0xffff),(0,1)):
    assert run(True,*vals)==run(False,*vals),vals;cases.append(vals)
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'binding':'Stock RX8 and RX16 decomp callers both target 0x08005e6a; stock two-byte body is bx lr.',
     'limits':['Only this stock-selected TOIDLE event callback body; no claim for RX completion parser or registered callback overrides.','No physical UART execution.']}
(H/('archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
