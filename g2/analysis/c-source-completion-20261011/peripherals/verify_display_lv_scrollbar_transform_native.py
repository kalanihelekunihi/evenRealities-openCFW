#!/usr/bin/env python3
"""Stock/C connected 0x440dda with controlled native property-getter ABI."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SRC=[D/'display_lv_scrollbar_transform.c',D/'display_lv_transform_style.c',D/'display_lv_transform_points.c',D/'display_lv_trig.c',D/'display_lv_round_geometry.c']
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text('#include <stdint.h>\nuint32_t audio_uart_lv_style_property_44bdea(void *o,uint32_t s,uint32_t p){(void)o;(void)s;(void)p;return 0;}\n');elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_scrollbar_clip_child_440dda',*[str(x) for x in SRC],str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 presets=[{0x70:0,0x6e:256,0x6f:256,0x71:0,0x72:0},
          {0x70:0,0x6e:128,0x6f:384,0x71:2,0x72:3},
          {0x70:450,0x6e:256,0x6f:256,0x71:5,0x72:7},
          {0x70:-450,0x6e:128,0x6f:384,0x71:0,0x72:0}]
 for props in presets:
  for reverse in (0,1):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f000;area=0x2007f100;u.mem_write(obj+0x14,struct.pack('<4i',10,20,109,69));u.mem_write(area,struct.pack('<8i',10,20,109,20,10,69,109,69))
    getter=sym['audio_uart_lv_style_property_44bdea'] if is_c else 0x44bdea
    trace=[]
    def hook(uc,address,size,user_data):
     p=uc.reg_read(UC_ARM_REG_R2);trace.append(p)
     uc.reg_write(UC_ARM_REG_R0,props.get(p,0)&0xffffffff)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=getter&~1,end=getter&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,area);u.reg_write(UC_ARM_REG_R2,4);u.reg_write(UC_ARM_REG_R3,reverse)
    u.emu_start((sym['audio_uart_lv_scrollbar_clip_child_440dda'] if is_c else 0x440dda)|1,0x600000,count=20000)
    pair.append((bytes(u.mem_read(area,32)),trace))
   assert pair[0]==pair[1],(props,reverse,pair)
 print('PASS_DISPLAY_LV_SCROLLBAR_TRANSFORM_NATIVE',len(presets)*2)
