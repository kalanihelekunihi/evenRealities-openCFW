"""Bounded actual ARM C/native LV object flag, parent, and outer dimensions."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_object_layout_fields.c'
SHIM='''
void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){(void)a;(void)b;(void)c;(void)d;}
int audio_uart_lv_area_width_451598(const int*r){return r[2]-r[0]+1;}
int audio_uart_lv_area_height_4515a4(const int*r){return r[3]-r[1]+1;}
'''
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text(SHIM);elf=Path(td)/'obj.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_has_flag_any_43e11c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for flags in (0,1,2,3,0x40000,0x80000000):
  for mask in (0,1,2,3,0x40000,0x80000000):cases.append(('audio_uart_lv_obj_has_flag_any_43e11c',0x43e11c,flags,mask))
 for parent in (0,0x20004100):cases.append(('audio_uart_lv_obj_parent_44dca2',0x44dca2,parent,0))
 for coords in ((0,0,0,0),(10,20,109,59),(-20,-30,20,30),(100,200,99,199)):
  for name,entry in (('audio_uart_lv_obj_width_43fd9e',0x43fd9e),('audio_uart_lv_obj_height_43fdda',0x43fdda)):
   cases.append((name,entry,coords,0))
 for name,entry,value,arg in cases:
  outs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000
   if name.endswith('43e11c'):u.mem_write(obj+0x24,struct.pack('<I',value))
   elif name.endswith('44dca2'):u.mem_write(obj+4,struct.pack('<I',value))
   else:u.mem_write(obj+0x14,struct.pack('<iiii',*value))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,arg)
   u.emu_start((syms[name] if is_c else entry)|1,0x600000,count=200)
   outs.append(u.reg_read(UC_ARM_REG_R0))
  assert outs[0]==outs[1],(name,value,arg,outs)
 print(f'PASS {len(cases)} compiled-C/native LV object field cases')
