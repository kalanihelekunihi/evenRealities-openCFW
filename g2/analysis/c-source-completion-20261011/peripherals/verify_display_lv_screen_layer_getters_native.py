#!/usr/bin/env python3
"""Actual compiled-C/stock display screen getter effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_screen_layer_getters.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('__attribute__((naked)) void *audio_uart_display_default_get(){__asm volatile("bx lr");}\n__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_display_previous_screen_44fc90',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native,offset in [('audio_uart_lv_display_previous_screen_44fc90',0x44fc90,0x2cc),('audio_uart_lv_display_top_layer_44fcbe',0x44fcbe,0x2c0),('audio_uart_lv_display_system_layer_44fcfc',0x44fcfc,0x2bc),('audio_uart_lv_display_bottom_layer_44fd38',0x44fd38,0x2c8)]:
  for mode in ('explicit','default','missing'):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    disp=0x2007f100;u.mem_write(disp,b'\0'*0x300);u.mem_write(disp+offset,struct.pack('<I',0x2007f800+offset));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,disp if mode=='explicit' else 0)
    getters=[sym['audio_uart_display_default_get']&~1, sym['audio_uart_lvgl_log']&~1] if is_c else [0x44fa1a,0x44d25c];seen=[]
    def hook(uc,a,size,_):
     if a==getters[0]:seen.append(0);uc.reg_write(UC_ARM_REG_R0,0 if mode=='missing' else disp);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if a==getters[1]:seen.append(1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym[name] if is_c else native)|1,0x600000,count=100)
    pair.append((u.reg_read(UC_ARM_REG_R0),seen))
   assert pair[0]==pair[1],(name,mode,pair)
   cases+=1
 print('PASS_DISPLAY_LV_SCREEN_LAYER_GETTERS_NATIVE',cases)
