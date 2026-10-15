#!/usr/bin/env python3
"""Compare label rectangle copy, including overlapping source/destination."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_rect_copy.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
 image=Path(temp)/'rect_copy.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for shift in (-16,-12,-8,-4,0,4,8,12,16):
  for seed in range(16):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    base=0x20011000;src=base+32;dst=src+shift
    initial=b''.join(((seed*0x9e3779b9+i*0x1234567)&0xffffffff).to_bytes(4,'little') for i in range(20))
    cpu.mem_write(base,initial)
    cpu.reg_write(UC_ARM_REG_R0,dst);cpu.reg_write(UC_ARM_REG_R1,src)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.emu_start((syms['audio_uart_ambiq_label_rect_copy_53fa94'] if compiled else 0x53fa94)|1,0x600000,count=40)
    observations.append(bytes(cpu.mem_read(base,len(initial))))
   assert observations[0]==observations[1],(shift,seed)
   count+=1
 print('PASS_AMBIQ_LABEL_RECT_COPY_NATIVE',count)
