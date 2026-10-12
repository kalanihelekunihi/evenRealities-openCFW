"""Actual compiled-C/native call and region effects for LV basic theme callback."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_theme_basic_apply.c'
CALLS={
 'init':(0x48cad8,'audio_uart_lv_basic_state_init_48cad8'),
 'box':(0x48c80e,'audio_uart_lv_basic_box_init_48c80e'),
 'x':(0x48c920,'audio_uart_lv_basic_x_48c920'),
 'y':(0x48c94e,'audio_uart_lv_basic_y_48c94e'),
 'ox':(0x44e486,'audio_uart_lv_obj_x_44e486'),
 'oy':(0x44e498,'audio_uart_lv_obj_y_44e498'),
 'item':(0x48cfe0,'audio_uart_lv_basic_item_48cfe0'),
 'done':(0x48cbda,'audio_uart_lv_basic_state_done_48cbda'),
 'w':(0x48c81a,'audio_uart_lv_basic_width_48c81a'),
 'h':(0x48c824,'audio_uart_lv_basic_height_48c824'),
 'invalid':(0x43f1a4,'audio_uart_lv_basic_invalidate_43f1a4'),
 'event':(0x451670,'audio_uart_lv_obj_event_451670'),
}
SHIM='''#include <stdint.h>
void audio_uart_lv_basic_state_init_48cad8(void*a,void*b){}
void audio_uart_lv_basic_box_init_48c80e(void*a,uint32_t b){}
int32_t audio_uart_lv_basic_x_48c920(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_y_48c94e(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_obj_x_44e486(void*a){return 0;}
int32_t audio_uart_lv_obj_y_44e498(void*a){return 0;}
void audio_uart_lv_basic_item_48cfe0(void*a,void*b,void*c){}
void audio_uart_lv_basic_state_done_48cbda(void*a){}
int32_t audio_uart_lv_basic_width_48c81a(void*a,uint32_t b){return 0;}
int32_t audio_uart_lv_basic_height_48c824(void*a,uint32_t b){return 0;}
void audio_uart_lv_basic_invalidate_43f1a4(void*a){}
uint32_t audio_uart_lv_obj_event_451670(void*a,uint32_t b,void*c){return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_theme_basic_apply_48ca3c',str(SRC),str(stub),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for count,w in ((0,8),(2,8),(2,0x3fffffff)):
  traces=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;children=0x20003100;items=0x20003200
   u.mem_write(obj+8,struct.pack('<I',children));u.mem_write(obj+0x14,struct.pack('<ii',100,200))
   u.mem_write(children,struct.pack('<I',items));u.mem_write(children+0x30,struct.pack('<H',count))
   u.mem_write(items,struct.pack('<II',0x20003400,0x20003500))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   mapping={(syms[s]&~1 if is_c else a):n for n,(a,s) in CALLS.items()}
   call=[]
   def hook(uc,a,size,_):
    if a not in mapping:return
    n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if n=='item':
     r2=uc.reg_read(UC_ARM_REG_R2);call.append((n,r0,struct.unpack('<ii',uc.mem_read(r2+8,8))))
    elif n=='event':call.append((n,r0,r1,uc.reg_read(UC_ARM_REG_R2)))
    elif n in ('x','y','w','h'):call.append((n,r0,r1))
    else:call.append((n,r0 if n=='invalid' else None))
    uc.reg_write(UC_ARM_REG_R0,{'x':7,'y':11,'ox':2,'oy':3,'w':w,'h':12}.get(n,0))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_uart_lv_theme_basic_apply_48ca3c'] if is_c else 0x48ca3c)|1,0x600000,count=400)
   traces.append(call)
  assert traces[0]==traces[1],(count,w,traces)
 print('PASS 3 compiled-C/native LV basic-theme callback cases')
