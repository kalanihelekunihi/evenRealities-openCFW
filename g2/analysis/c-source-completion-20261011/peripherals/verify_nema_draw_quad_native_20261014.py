#!/usr/bin/env python3
"""Compare Nema float quad conversion and 18-word packet with Apollo."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2,UC_ARM_REG_S3,UC_ARM_REG_S4,UC_ARM_REG_S5,UC_ARM_REG_S6,UC_ARM_REG_S7
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_draw_quad.c'
converter=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_fixed.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
F=lambda x:int.from_bytes(struct.pack('<f',x),'little')
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_nema_cl_get_space_514aec\n.thumb_func\naudio_uart_nema_cl_get_space_514aec:\n bx lr\n.bss\n.global audio_uart_nema_context_cell\naudio_uart_nema_context_cell: .space 4\n')
 image=d/'quad.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(converter),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[tuple(F(v) for v in xs) for xs in (
  (0.,0.,1.,0.,1.,1.,0.,1.),
  (-1.25,-2.5,3.75,4.125,-5.5,6.75,7.875,-8.125),
  (2048.,0.,0.,2048.,-2048.,0.,0.,-2048.),
  (0.00001,-0.00001,0.5,-0.5,1.5,-1.5,2.5,-2.5))]
 cases += [tuple(F((i*8+j-72)/19.0) for j in range(8)) for i in range(20)]
 count=0
 for args in cases:
  for allocate in (False,True):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
    cpu.mem_write(cell,(0x20088000).to_bytes(4,'little'))
    cpu.mem_write(0x20088018,(0x4a20).to_bytes(4,'little'))
    cpu.mem_write(0x20090000,bytes([0xcc])*72)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip((UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2,UC_ARM_REG_S3,UC_ARM_REG_S4,UC_ARM_REG_S5,UC_ARM_REG_S6,UC_ARM_REG_S7),args):cpu.reg_write(reg,value)
    alloc=(syms['audio_uart_nema_cl_get_space_514aec'] if compiled else 0x514aec)&~1
    events=[]
    def hook(u,address,_size,_user):
     if address!=alloc:return
     events.append(u.reg_read(UC_ARM_REG_R0))
     u.reg_write(UC_ARM_REG_R0,0x20090000 if allocate else 0)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=syms['audio_uart_nema_draw_quad_522db4'] if compiled else 0x522db4
    cpu.emu_start(start|1,0x600000,count=700)
    observations.append((events,bytes(cpu.mem_read(0x20090000,72))))
   assert observations[0]==observations[1],(args,allocate,observations)
   count+=1
 print('PASS_NEMA_DRAW_QUAD_NATIVE',count)
