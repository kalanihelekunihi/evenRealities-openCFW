#!/usr/bin/env python3
"""Compare native/C MSPI option init failure ladder and hardware writes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_sync_sem_new',0x44989a),('g2_main_mspi_handle_init_4c0812',0x4c0812),('audio_uart_font_flash_power',0x4c26e0),('g2_main_mspi_handle_config_4c08a8',0x4c08a8),('g2_norflash_configure_mspi_4c099c',0x4c099c),('g2_norflash_enable_mspi_4c0e1e',0x4c0e1e),('g2_norflash_clock_select_4c32b4',0x4c32b4),('display_driver_uled_interrupt_clear_4c23de',0x4c23de),('display_driver_uled_interrupt_enable_4c2328',0x4c2328),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
stages={'g2_main_mspi_handle_init_4c0812':1,'audio_uart_font_flash_power':2,'g2_main_mspi_handle_config_4c08a8':3,'g2_norflash_configure_mspi_4c099c':4,'g2_norflash_enable_mspi_4c0e1e':5,'display_driver_uled_interrupt_clear_4c23de':6,'display_driver_uled_interrupt_enable_4c2328':7}
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'init.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_config.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for failure in range(8):
  for flags in (0,2,7):
   observations=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
    for base,data in segments:u.mem_write(base,data)
    u.mem_write(0x20074004,(0x44332211).to_bytes(4,'little'));u.mem_write(0x20001000,(0xabcdef12).to_bytes(4,'little'))
    calls=[];power_count=[0]
    def lower(uc,at,size,user):
     name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
     regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3));sp=uc.reg_read(UC_ARM_REG_SP)
     if name=='g2_main_mspi_handle_init_4c0812':calls.append((name,regs[0]));uc.mem_write(regs[1],(0x11223344).to_bytes(4,'little'))
     elif name=='g2_main_mspi_handle_config_4c08a8':calls.append((name,regs[0],bytes(uc.mem_read(regs[1],12))))
     elif name=='g2_norflash_configure_mspi_4c099c':calls.append((name,regs[:2]))
     elif name=='g2_flashdb_candidate_flags':calls.append((name,));value=flags
     elif name=='g2_flashdb_candidate_log':calls.append((name,regs,tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(2))));value=0
     elif name=='audio_log_simple':calls.append((name,regs[:3]));value=0
     elif name=='audio_uart_font_flash_power':calls.append((name,regs[:3]));power_count[0]+=1
     else:calls.append((name,regs[:3] if name=='audio_uart_sync_sem_new' else regs[:2] if name in ('g2_norflash_clock_select_4c32b4','display_driver_uled_interrupt_clear_4c23de','display_driver_uled_interrupt_enable_4c2328') else regs[0] if name=='g2_norflash_enable_mspi_4c0e1e' else None))
     if name not in ('g2_flashdb_candidate_flags','g2_flashdb_candidate_log','audio_log_simple'):
      value=0x12340000 if name=='audio_uart_sync_sem_new' else 7 if stages.get(name)==failure and not (name=='audio_uart_font_flash_power' and power_count[0]>1) else 0
     uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for name,at in callees:
     target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_R1,0x55667788);u.reg_write(UC_ARM_REG_R2,0x20002000);u.reg_write(UC_ARM_REG_R3,0x20003000)
    u.emu_start((syms['display_driver_uled_option_config_59cf1a'] if compiled else 0x59cf1a)|1,0x600000,count=2000)
    cells=tuple(bytes(u.mem_read(a,n)) for a,n in ((0x20074534,4),(0x20074538,4),(0x2007453c,4),(0x20001000,4),(0xe000e414,1),(0xe000e100,4)))
    observations.append((calls,u.reg_read(UC_ARM_REG_R0),cells))
   assert observations[0]==observations[1],(failure,flags,observations)
   cases+=1
 print('PASS_ULED_OPTION_CONFIG_NATIVE',cases)
