#!/usr/bin/env python3
"""Stock/C bounded dimension and area helper comparisons."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_render_area_helpers.c'
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text('__attribute__((naked)) void *audio_uart_display_default_get(){__asm volatile("bx lr");}\n');elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_display_width_44fa7e',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in [('audio_uart_lv_display_width_44fa7e',0x44fa7e),('audio_uart_lv_display_height_44faa8',0x44faa8),('audio_uart_lv_area_intersect_450bcc',0x450bcc),('audio_uart_lv_area_copy_4530fc',0x4530fc)]:
  for mode in range(6):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    d=0x2007f100;o=0x2007f900;a=0x2007f800;b=0x2007f820
    u.mem_write(d,b'\0'*0x300);u.mem_write(d,struct.pack('<II',15,20));u.mem_write(d+0x2fc,bytes([mode]));u.mem_write(a,struct.pack('<4i',mode,4,10,12));u.mem_write(b,struct.pack('<4i',3,6,8,9));u.mem_write(o,b'\xa5'*16)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if 'display_' in name:u.reg_write(UC_ARM_REG_R0,d)
    else:u.reg_write(UC_ARM_REG_R0,o);u.reg_write(UC_ARM_REG_R1,a);u.reg_write(UC_ARM_REG_R2,b)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=150)
    pair.append((u.reg_read(UC_ARM_REG_R0) if 'copy' not in name else 0,bytes(u.mem_read(o,16)) if 'display_' not in name else b''))
   assert pair[0]==pair[1],(name,mode,pair)
   cases+=1
 print('PASS_DISPLAY_LV_RENDER_AREA_HELPERS_NATIVE',cases)
