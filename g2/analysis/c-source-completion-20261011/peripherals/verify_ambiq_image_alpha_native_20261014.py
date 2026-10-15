#!/usr/bin/env python3
"""Compare image alpha's register and optional command calls with Apollo."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_alpha.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_ambiq_color_register_4b1474',0x4b1474),('audio_uart_nema_alpha_command_522960',0x522960)]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_ in callees)+'.bss\n.global audio_uart_nema_boot_state_200043a8\naudio_uart_nema_boot_state_200043a8: .space 4\n')
 image=d/'alpha.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for state in (0,1,255):
  for alpha in [0,1,0xff000000,0xffffffff]+[(i*0x9e3779b9)&0xffffffff for i in range(64)]:
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cell=syms['audio_uart_nema_boot_state_200043a8'] if compiled else 0x200043a8
    cpu.mem_write(cell,bytes([state]));cpu.reg_write(UC_ARM_REG_R0,alpha)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    targets={((syms[n] if compiled else a)&~1):n for n,a in callees};calls=[]
    def hook(u,address,_size,_user):
     n=targets.get(address)
     if n is None:return
     if n.endswith('4b1474'):calls.append((n,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
     else:calls.append((n,u.reg_read(UC_ARM_REG_R0)))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((syms['audio_uart_ambiq_image_alpha_513e2e'] if compiled else 0x513e2e)|1,0x600000,count=80)
    observations.append(calls)
   assert observations[0]==observations[1],(state,hex(alpha),observations)
   count+=1
 print('PASS_AMBIQ_IMAGE_ALPHA_NATIVE',count)
