#!/usr/bin/env python3
"""Compare two Apollo Ambiq mode wrappers at their shared lower call."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_gpu_mode_wrappers.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global display_driver_gpu_mode_lower_4b06c0\n'
                '.thumb_func\ndisplay_driver_gpu_mode_lower_4b06c0:\n bx lr\n')
 image=d/'mode.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for name,native in [('display_driver_gpu_mode_4b0730',0x4b0730),
                     ('display_driver_gpu_enable_4b0748',0x4b0748)]:
  for a,b in [(0,1),(1,0),(0xffffffff,0x80000000),(17,23)]:
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_R0,a);cpu.reg_write(UC_ARM_REG_R1,b)
    target=(syms['display_driver_gpu_mode_lower_4b06c0'] if compiled else 0x4b06c0)&~1
    calls=[]
    def hook(u,address,_size,_user):
     if address!=target:return
     sp=u.reg_read(UC_ARM_REG_SP)
     calls.append([u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]+
       [int.from_bytes(u.mem_read(sp+i,4),'little') for i in (0,4)])
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=80)
    observations.append(calls)
   assert observations[0]==observations[1] and len(observations[0])==1,(name,a,b,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_GPU_MODE_WRAPPERS_NATIVE',count)
