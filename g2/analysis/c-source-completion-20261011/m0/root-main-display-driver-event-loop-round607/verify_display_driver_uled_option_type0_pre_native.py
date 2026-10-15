#!/usr/bin/env python3
"""Compare type-0 pre-enable C/native direct-callee sequence and MMIO."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_ble_hci_radio_mode_state_50938e',0x50938e),('display_driver_uled_type0_pin_prepare_592c78',0x592c78),('display_driver_uled_type0_mode4_5124fc',0x5124fc),('display_driver_uled_type1_power_5122ec',0x5122ec),('audio_delay',0x449376),('g2_norflash_clock_select_4c32b4',0x4c32b4),('audio_uart_font_flash_power',0x4c26e0),('g2_norflash_disable_mspi_4c0ea8',0x4c0ea8),('g2_norflash_configure_mspi_4c099c',0x4c099c),('g2_norflash_enable_mspi_4c0e1e',0x4c0e1e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,at in callees))
 image=Path(directory)/'pre.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_pre.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in (0,2,3,4,6,255):
  for handle in (0,0x20008000):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
    for base,data in segments:u.mem_write(base,data)
    u.mem_write(0x20002000,bytes([mode]));u.mem_write(0x20074524,handle.to_bytes(4,'little'))
    calls=[]
    def lower(uc,at,size,user):
     name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
     count=3 if name=='audio_uart_font_flash_power' else 2 if name in ('g2_norflash_clock_select_4c32b4','g2_norflash_configure_mspi_4c099c') else 1 if name in ('audio_ble_hci_radio_mode_state_50938e','audio_delay','g2_norflash_disable_mspi_4c0ea8','g2_norflash_enable_mspi_4c0e1e') else 0
     regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)
     calls.append((name,tuple(uc.reg_read(x) for x in regs[:count])))
     uc.reg_write(UC_ARM_REG_R0,0x20002000 if name=='audio_ble_hci_radio_mode_state_50938e' else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in callees:
     target=syms[n]&~1 if compiled else at
     u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms['display_driver_uled_type0_pre_593200'] if compiled else 0x593200)|1,0x600000,count=2000)
    observed.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x40010444,12))))
   assert observed[0]==observed[1],(mode,handle,observed)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_PRE_NATIVE',cases)
