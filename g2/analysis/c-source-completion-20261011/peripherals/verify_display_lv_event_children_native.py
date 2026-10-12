#!/usr/bin/env python3
"""Actual ARM C/stock LV event active, base callback, bubble and flag children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_core_children.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_active_input_452ef8','-Wl,--defsym=audio_uart_display_lv_root=0x2006f548',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for code in range(0x80):
  for bubble,stop in ((0,0),(1,0),(1,4)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;ev=0x2007f200;u.mem_write(obj,b'\0'*64);u.mem_write(ev,b'\0'*28);u.mem_write(obj+0x24,struct.pack('<I',0x4000 if bubble else 0));u.mem_write(ev,struct.pack('<I',obj));u.mem_write(ev+8,struct.pack('<I',code));u.mem_write(ev+24,bytes([stop]));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ev)
    u.emu_start((sym['audio_uart_lv_event_is_bubbled_451b34'] if is_c else 0x451b34)|1,0x600000,count=150);pair.append(u.reg_read(UC_ARM_REG_R0))
   assert pair[0]==pair[1],(code,bubble,stop,pair)
   cases+=1
 for name,nat in [('audio_uart_lv_active_input_452ef8',0x452ef8),('audio_uart_lv_obj_has_flag_43e0e0',0x43e0e0),('audio_uart_lv_object_event_base_4516f8',0x4516f8)]:
  for mode in range(4):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x300000,0x1000);u.mem_write(0x300000,b'\x70\x47')
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;ev=0x2007f200;cls=0x2007f300;u.mem_write(obj,b'\0'*64);u.mem_write(ev,b'\0'*28);u.mem_write(cls,b'\0'*32);u.mem_write(ev,struct.pack('<I',obj));u.mem_write(obj,struct.pack('<I',cls));u.mem_write(obj+0x24,struct.pack('<I',0x4000 if mode&1 else 0));u.mem_write(0x2006f548+0x50,struct.pack('<I',0x2007f400 if mode&1 else 0))
    if mode>=2:u.mem_write(cls+12,struct.pack('<I',0x300001))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ev if name.endswith('4516f8') else obj);u.reg_write(UC_ARM_REG_R1,0x4000 if name.endswith('43e0e0') else ev)
    if name.endswith('4516f8'):u.reg_write(UC_ARM_REG_R0,0)
    seen=[]
    def hook(uc,a,size,_):
     if a==0x300000:seen.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym[name] if is_c else nat)|1,0x600000,count=200)
    pair.append((u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(ev+12,4))))
   assert pair[0]==pair[1],(name,mode,pair)
   cases+=1
 print('PASS_DISPLAY_LV_EVENT_CHILDREN_NATIVE',cases)
