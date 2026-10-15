#!/usr/bin/env python3
"""Compare enable pair with native code while recording direct-callee order/args."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_type0_pre_593200',0x593200),('display_driver_uled_type0_step_5927ca',0x5927ca),('display_driver_uled_type0_get_592f9a',0x592f9a),('display_driver_uled_type0_start_5931c0',0x5931c0),('display_driver_uled_type0_finish_59328c',0x59328c),('display_driver_uled_type1_pre_5bcb6c',0x5bcb6c),('display_driver_uled_type1_get_5bc76e',0x5bc76e),('display_driver_uled_type1_step_5bbff2',0x5bbff2),('display_driver_uled_type1_post_5bcb28',0x5bcb28),('display_driver_uled_type1_finish_5bcbb4',0x5bcbb4),('display_driver_uled_delay_449376',0x449376),('display_driver_uled_select_4910f4',0x4910f4)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'stubs.c'
 stub.write_text('typedef unsigned u32;typedef unsigned short u16;\n'+'\n'.join(f'u32 {name}(u32 x){{return 0x33u;}}' for name,at in callees))
 image=Path(directory)/'enable.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_enable_pair.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,native in [('display_driver_uled_option_type0_enable_5926b4',0x5926b4),('display_driver_uled_option_type1_enable_5bbda4',0x5bbda4)]:
  for value in (0,1,0x100,0x101,0xffffffff):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    u.mem_map(0x40010000,0x10000)
    for base,data in segments:u.mem_write(base,data)
    calls=[]
    def lower(uc,at,size,user):
     calls.append((next((n for n,a in callees if (syms[n]&~1 if compiled else a)==at),hex(at)),uc.reg_read(UC_ARM_REG_R0)))
     uc.reg_write(UC_ARM_REG_R0,0x33)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in callees:u.hook_add(UC_HOOK_CODE,lower,begin=(syms[n]&~1 if compiled else at),end=(syms[n]&~1 if compiled else at))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value)
    u.emu_start((syms[name] if compiled else native)|1,0x600000,count=3000)
    normalized=[(n,0 if n in {'display_driver_uled_type1_get_5bc76e','display_driver_uled_type0_step_5927ca','display_driver_uled_type0_start_5931c0','display_driver_uled_type0_finish_59328c','display_driver_uled_type0_pre_593200','display_driver_uled_type1_pre_5bcb6c','display_driver_uled_type1_step_5bbff2','display_driver_uled_type1_post_5bcb28','display_driver_uled_type1_finish_5bcbb4'} else arg) for n,arg in calls]
    observed.append((u.reg_read(UC_ARM_REG_R0),normalized,bytes(u.mem_read(0x4001044c,4))))
   assert observed[0]==observed[1],(name,value,observed)
 print('PASS_DISPLAY_DRIVER_ULED_OPTION_ENABLE_PAIR_NATIVE',10)
