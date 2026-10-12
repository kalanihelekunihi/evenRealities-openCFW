"""Actual compiled-C/native basic-theme state initializer call and slot effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_theme_basic_state_init.c'
PAIRS={
 'mode':(0x44dce2,'audio_uart_lv_child_get_44dce2'),
 'box':(0x48c80e,'audio_uart_lv_basic_box_init_48c80e'),
 'a':(0x48cdec,'audio_uart_lv_basic_prepare_a_48cdec'),
 'b':(0x48cbf8,'audio_uart_lv_basic_prepare_b_48cbf8'),
 'hor':(0x48c860,'audio_uart_lv_basic_horizontal_48c860'),
 'ver':(0x48c856,'audio_uart_lv_basic_vertical_48c856'),
 'pad':(0x48c8a8,'audio_uart_lv_grid_base_dir_48c8a8'),
 'width':(0x48c81a,'audio_uart_lv_basic_width_48c81a'),
 'height':(0x48c824,'audio_uart_lv_basic_height_48c824'),
 'contentw':(0x43fe16,'audio_uart_lv_obj_content_width_43fe16'),
 'contenth':(0x43fe70,'audio_uart_lv_obj_content_height_43fe70'),
 'hmode':(0x48c9cc,'audio_uart_lv_basic_h_mode_48c9cc'),
 'vmode':(0x48c9d6,'audio_uart_lv_basic_v_mode_48c9d6'),
 'axis':(0x48d3c8,'audio_uart_lv_basic_axis_48d3c8'),
}
SHIM='''#include <stdint.h>
void *audio_uart_lv_child_get_44dce2(void*a,int32_t b){return 0;}
void audio_uart_lv_basic_box_init_48c80e(void*a,uint32_t b){}
void audio_uart_lv_basic_prepare_a_48cdec(void*a,void*b){}
void audio_uart_lv_basic_prepare_b_48cbf8(void*a,void*b){}
uint32_t audio_uart_lv_basic_horizontal_48c860(void*a,uint32_t b){return 0;}
uint32_t audio_uart_lv_basic_vertical_48c856(void*a,uint32_t b){return 0;}
uint8_t audio_uart_lv_grid_base_dir_48c8a8(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_width_48c81a(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_height_48c824(void*a,uint32_t b){return 0;}
uint32_t audio_uart_lv_obj_content_width_43fe16(void*a){return 0;}
uint32_t audio_uart_lv_obj_content_height_43fe70(void*a){return 0;}
uint8_t audio_uart_lv_basic_h_mode_48c9cc(void*a){return 0;}
uint8_t audio_uart_lv_basic_v_mode_48c9d6(void*a){return 0;}
uint32_t audio_uart_lv_basic_axis_48d3c8(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_basic_state_init_48cad8',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for mode,width,height,flags in ((0,10,20,0),(2,10,20,0),(1,0x3fffffff,0x3fffffff,0)):
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;state=0x20004000
   u.mem_write(obj+0x2a,struct.pack('<H',flags));u.mem_write(state,b'\x55'*32)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,state)
   mapping={(syms[s]&~1 if is_c else a):n for n,(a,s) in PAIRS.items()};calls=[];axis_count=[0]
   def hook(uc,a,size,_):
    if a not in mapping:return
    n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if n=='axis':
     sp=uc.reg_read(UC_ARM_REG_SP);stack=struct.unpack('<IIII',uc.mem_read(sp,16))
     calls.append((n,r0,r1,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),stack))
     axis_count[0]+=1
    else:calls.append(n)
    returns={'mode':mode,'hor':5,'ver':6,'pad':1,'width':width,'height':height,
             'contentw':100,'contenth':200,'hmode':3,'vmode':4}
    uc.reg_write(UC_ARM_REG_R0,(0x100+axis_count[0]) if n=='axis' else returns.get(n,0))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_uart_lv_basic_state_init_48cad8'] if is_c else 0x48cad8)|1,0x600000,count=200)
   traces.append((calls,bytes(u.mem_read(state,32))))
  assert traces[0]==traces[1],(mode,width,height,flags,traces)
 print('PASS 3 compiled-C/native LV basic-theme state cases')
