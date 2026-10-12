#!/usr/bin/env python3
"""Compare native and compiled ARM C two-timer BoxDetect_Init effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_box_detect_init.c'
STUB='''#include <stdint.h>
void *audio_box_detect_timer,*audio_box_reconnect_timer;
uint8_t audio_box_detect_timer_control_block[44],audio_box_reconnect_timer_control_block[44];
void audio_box_detect_timer_callback_4ac016(void*p){(void)p;}
void audio_box_reconnect_timer_callback_4ac020(void*p){(void)p;}
void *audio_uart_timer_new(void(*a)(void*),uint32_t b,void*c,const void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_box_detect_init_4ac02a',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for old_first,old_second,results in ((0,0,(0,0)),(0,0,(0x20060100,0x20060200)),(0x20060300,0,(0x20060200,0)),(0,0x20060400,(0x20060100,0))):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   first=sym['audio_box_detect_timer'] if is_c else 0x20074920
   second=sym['audio_box_reconnect_timer'] if is_c else 0x20074924
   u.mem_write(first,old_first.to_bytes(4,'little'));u.mem_write(second,old_second.to_bytes(4,'little'))
   trace=[];counter=[0]
   hooks=[('new','audio_uart_timer_new',0x4493b0),('flags','audio_log_level',0x43d0ce)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,pc,size,user,name=name):
     if name=='flags':uc.reg_write(UC_ARM_REG_R0,0)
     else:
      attr=uc.reg_read(UC_ARM_REG_R3);name_ptr=int.from_bytes(uc.mem_read(attr,4),'little')
      raw=bytes(uc.mem_read(name_ptr,32)).split(b'\0')[0]
      size=int.from_bytes(uc.mem_read(attr+12,4),'little')
      trace.append((raw,uc.reg_read(UC_ARM_REG_R1),size))
      uc.reg_write(UC_ARM_REG_R0,results[counter[0]]);counter[0]+=1
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_box_detect_init_4ac02a'] if is_c else 0x4ac02a)|1,0x600000,count=3500)
   pair.append((trace,bytes(u.mem_read(first,4)),bytes(u.mem_read(second,4))))
  assert pair[0]==pair[1],((old_first,old_second,results),pair)
print('PASS_BOX_DETECT_INIT_NATIVE 4')
