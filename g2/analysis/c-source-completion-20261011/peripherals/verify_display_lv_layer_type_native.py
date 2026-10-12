#!/usr/bin/env python3
"""Actual ARM/C LV layer-type decision and generated getter property IDs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_layer_type.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('#include <stdint.h>\n__attribute__((naked)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_layer_type_44cd9e',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in ('plain','rotation','opa','blend'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007f100)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x44bdea,sym['audio_uart_lv_style_property_44bdea']&~1):
     prop=uc.reg_read(UC_ARM_REG_R2);seen.append(prop);val={0x6e:0x100,0x6f:0x100,0x63:0xff}.get(prop,0)
     if mode=='rotation' and prop==0x70:val=1
     if mode=='opa' and prop==0x63:val=0
     if mode=='blend' and prop==0x75:val=1
     uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_obj_layer_type_44cd9e'] if is_c else 0x44cd9e)|1,0x600000,count=180)
   pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(mode,pair)
 print('PASS_DISPLAY_LV_LAYER_TYPE_NATIVE',4)
