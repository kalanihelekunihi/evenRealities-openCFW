#!/usr/bin/env python3
"""Combined property caller/default with controlled selector R1 effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
stub='__attribute__((naked)) unsigned audio_uart_lv_selector_style_prop_44ce8a(){__asm volatile("bx lr");}\n__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}\n'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_property_44bdea',str(D/'display_lv_style_property.c'),str(D/'display_lv_property_default_model.c'),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for prop in (0x1c,0x23,0x31,0x78,0x5a,0x6f,0x7f):
  for seed in (0,0xa5000000,0xffffffff):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;u.mem_write(obj,b'\0'*64);u.mem_write(obj+0x28,struct.pack('<H',3));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,0x12340000);u.reg_write(UC_ARM_REG_R2,prop)
    selector=(sym['audio_uart_lv_selector_style_prop_44ce8a']&~1) if is_c else 0x44ce8a
    def hook(uc,a,size,_):
     if a==selector:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_R1,seed);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if not is_c and a in (0x43bb00,0x439be4):
      n=uc.reg_read(UC_ARM_REG_R2);dst=uc.reg_read(UC_ARM_REG_R0)
      uc.mem_write(dst,(b'\0'*n) if a==0x43bb00 else bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_style_property_44bdea'] if is_c else 0x44bdea)|1,0x600000,count=500)
    pair.append(u.reg_read(UC_ARM_REG_R0))
   assert pair[0]==pair[1],(hex(prop),hex(seed),list(map(hex,pair)))
   cases+=1
 print('PASS_DISPLAY_LV_PROPERTY_CALLER_NATIVE',cases)
