"""Actual compiled-C/native basic-theme object offsets and style selectors."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_theme_basic_children.c'
SHIM='''#include <stdint.h>
void audio_uart_lv_basic_box_clear_454746(void*a,uint32_t b,uint32_t c){}
uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){return 0;}
void audio_uart_lv_heap_free(void*a){}
int32_t audio_uart_lv_basic_x_base_48c84c(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_y_base_48c842(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_offset_48c892(void*a,uint32_t b){return 0;}
uint32_t audio_uart_lv_basic_flags_48c89c(void*a,uint32_t b){return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_x_44e486',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[(0x44e486,'audio_uart_lv_obj_x_44e486',0,0),(0x44e486,'audio_uart_lv_obj_x_44e486',0x20003100,0x12345678),
        (0x44e498,'audio_uart_lv_obj_y_44e498',0,0),(0x44e498,'audio_uart_lv_obj_y_44e498',0x20003100,0x87654321)]
 for native,name,parent,value in cases:
  outs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;u.mem_write(obj+8,struct.pack('<I',parent))
   if parent:u.mem_write(parent+(0x20 if native==0x44e486 else 0x24),struct.pack('<I',value))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   u.emu_start((syms[name] if is_c else native)|1,0x600000,count=30)
   outs.append(u.reg_read(UC_ARM_REG_R0))
  assert outs[0]==outs[1],(name,parent,outs)
 print('PASS 4 compiled-C/native LV basic object-offset cases')
