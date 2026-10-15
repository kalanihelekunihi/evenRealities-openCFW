#!/usr/bin/env python3
"""Compare native single-point wrapper's seven forwarded lower arguments."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/transform_point.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_lv_transform_area_4513c8\n.thumb_func\naudio_uart_lv_transform_area_4513c8:\n bx lr\n')
 image=d/'point.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,256,256,0),(90,256,256,1),(-45,0x10000,0xffffffff,0x12345678)]
 cases += [((i*17)-800,(i*0x12345)&0xffffffff,(i*0x23456)&0xffffffff,(i*0x9e3779b9)&0xffffffff) for i in range(128)]
 for angle,sx,sy,flags in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cpu.reg_write(UC_ARM_REG_R0,0x20013000);cpu.reg_write(UC_ARM_REG_R1,angle&0xffffffff)
   cpu.reg_write(UC_ARM_REG_R2,sx);cpu.reg_write(UC_ARM_REG_R3,sy)
   sp=0x200ff000;cpu.reg_write(UC_ARM_REG_SP,sp);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.mem_write(sp,(0x20014000).to_bytes(4,'little')+flags.to_bytes(4,'little'))
   target=(syms['audio_uart_lv_transform_area_4513c8'] if compiled else 0x4513c8)&~1
   calls=[]
   def hook(u,address,_size,_user):
    if address!=target:return
    stack=u.reg_read(UC_ARM_REG_SP)
    calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),
     u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),
     rd(u,stack),rd(u,stack+4),rd(u,stack+8)))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((syms['audio_uart_lv_transform_point_4513ae'] if compiled else 0x4513ae)|1,0x600000,count=70)
   observations.append(calls)
  assert observations[0]==observations[1],((angle,sx,sy,flags),observations)
 print('PASS_LV_TRANSFORM_POINT_WRAPPER_NATIVE',len(cases))
