#!/usr/bin/env python3
"""Compare Nema buffer-creator adapter at Apollo 0x53cf78."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3];source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/base.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('void audio_uart_nema_buffer_create_514070(unsigned *o,unsigned a,unsigned b){}\n')
 image=Path(directory)/'base.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,pool,size,ignored,result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  calls=[]
  def lower(uc,at,n,user):
   out=uc.reg_read(UC_ARM_REG_R0);a=uc.reg_read(UC_ARM_REG_R1);b=uc.reg_read(UC_ARM_REG_R2)
   calls.append((a,b));uc.mem_write(out+8,result.to_bytes(4,'little'))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  at=syms['audio_uart_nema_buffer_create_514070']&~1 if compiled else 0x514070
  u.hook_add(UC_HOOK_CODE,lower,begin=at,end=at)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,v in ((UC_ARM_REG_R0,pool),(UC_ARM_REG_R1,size),(UC_ARM_REG_R2,ignored)):u.reg_write(reg,v)
  u.emu_start((syms['audio_uart_ambiq_buffer_base_53cf78'] if compiled else 0x53cf78)|1,0x600000,count=100)
  return calls,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for pool in (0,1,3,0xffffffff):
  for size in (0,1,1024,0xffffffff):
   for ignored in (0,0x102):
    for result in (0,0x20004000):
     native=run(False,pool,size,ignored,result);source=run(True,pool,size,ignored,result)
     assert native==source,(pool,size,ignored,result,native,source)
     cases+=1
 print('PASS_AMBIQ_BUFFER_BASE_NATIVE',cases)
