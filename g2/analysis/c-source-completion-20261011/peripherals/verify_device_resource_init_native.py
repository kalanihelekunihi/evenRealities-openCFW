#!/usr/bin/env python3
"""Compare native and compiled C device resource initialization effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_device_resource_init.c'
STUB='''#include <stdint.h>
uint8_t audio_device_manager_state[64],audio_device_manager_timer_control_block[44];void *audio_device_manager_timer;
void audio_device_manager_battery_sync_init(void){}void audio_ring_battery_callback_wrapper_4ff8d4(void){}void audio_box_detect_init_4ac02a(void){}
uint32_t SVC_Settings_Init(void){return 0;}uint32_t audio_uart_hand_initialize_466660(void){return 0;}
void *audio_queue_new(uint32_t a,uint32_t b,const void*c){(void)a;(void)b;(void)c;return 0;}
void *audio_uart_timer_new(void(*a)(void*),uint32_t b,void*c,const void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_device_manager_timer_callback_4c661c(void*p){(void)p;}int32_t osTimerStart(void*p,uint32_t n){(void)p;(void)n;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_device_manager_resource_init_4c632c',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for queue,timer,old in ((0,0,0),(0x20060100,0,0),(0x20060100,0x20060200,0),(0x20060100,0x20060200,0x20060300)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sym['audio_device_manager_state'] if is_c else 0x2000060c
   cell=sym['audio_device_manager_timer'] if is_c else 0x200744c0
   u.mem_write(cell,old.to_bytes(4,'little'));trace=[]
   hooks=[('battery','audio_device_manager_battery_sync_init',0x4acf7c),('ring_battery','audio_ring_battery_callback_wrapper_4ff8d4',0x4ff8d4),('box','audio_box_detect_init_4ac02a',0x4ac02a),('settings','SVC_Settings_Init',0x46be10),('hand','audio_uart_hand_initialize_466660',0x466660),('queue','audio_queue_new',0x449a32),('timer','audio_uart_timer_new',0x4493b0),('start','osTimerStart',0x449498),('flags','audio_log_level',0x43d0ce)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,pc,size,user,name=name):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if name=='queue':trace.append((name,r0,r1,r2));uc.reg_write(UC_ARM_REG_R0,queue)
     elif name=='timer':
      attr=uc.reg_read(UC_ARM_REG_R3);size=int.from_bytes(uc.mem_read(attr+12,4),'little')
      trace.append((name,r1,r2,size));uc.reg_write(UC_ARM_REG_R0,timer)
     elif name=='start':trace.append((name,r0,r1));uc.reg_write(UC_ARM_REG_R0,0)
     elif name=='flags':uc.reg_write(UC_ARM_REG_R0,0)
     else:trace.append((name,));uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_device_manager_resource_init_4c632c'] if is_c else 0x4c632c)|1,0x600000,count=5000)
   pair.append((trace,bytes(u.mem_read(state+12,4)),bytes(u.mem_read(cell,4))))
  assert pair[0]==pair[1],((queue,timer,old),pair)
print('PASS_DEVICE_RESOURCE_INIT_NATIVE 4')
