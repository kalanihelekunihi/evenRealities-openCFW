#!/usr/bin/env python3
"""Stock/C 0x4c507e branch/effect traces with native child ABIs controlled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_notify_event.c'
STUB='''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_event_loop_remove_delayed(void (*f)(void)){(void)f;return 0;}
void audio_event_loop_push_delayed(void (*f)(void),uint32_t a,uint32_t b){(void)f;(void)a;(void)b;}
void audio_uart_ring_msg_handler_4c4de8(void){}
void audio_uart_ring_exit_4c53a6(void){}
void audio_uart_ring_service_disc_followup_4c5032(void){}
void audio_ble_master_followup_delayed(void){}
void audio_uart_ring_status_delayed_4a285c(void){}
void audio_uart_ring_pair_enable_delayed_47257c(void){}
void audio_uart_ring_pair_disable_delayed_472588(void){}
void audio_uart_display_housekeep(void){}
uint32_t audio_settings_terminal_mode(void){return 0;}
void audio_uart_ring_mode_update_472362(uint16_t x){(void)x;}
void audio_uart_ring_heartbeat_472244(void){}
void audio_uart_ring_pair_mode_472546(void){}
'''
children=[('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e),('audio_event_loop_remove_delayed',0x476ace),('audio_event_loop_push_delayed',0x47697e),('audio_uart_ring_msg_handler_4c4de8',0x4c4de8),('audio_uart_ring_exit_4c53a6',0x4c53a6),('audio_uart_display_housekeep',0x47243a),('audio_settings_terminal_mode',0x46c630),('audio_uart_ring_mode_update_472362',0x472362),('audio_uart_ring_heartbeat_472244',0x472244),('audio_uart_ring_pair_mode_472546',0x472546)]
callbacks=[('audio_uart_ring_service_disc_followup_4c5032',0x4c5033),('audio_ble_master_followup_delayed',0x4c4ee5),('audio_uart_ring_status_delayed_4a285c',0x4a285d),('audio_uart_ring_pair_enable_delayed_47257c',0x47257d),('audio_uart_ring_pair_disable_delayed_472588',0x472589)]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_notify_event_4c507e',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[0,1<<22,1<<2,1<<3,1<<4,1<<5,1<<6,1<<11,1<<8,1<<23,(1<<2)|(1<<4)|(1<<6),(1<<22)|(1<<23)]
 for bits in cases:
  for level in (0,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    cb_map={((sym[n] if is_c else a)|1):n for n,a in callbacks}
    trace=[]
    for n,a in children:
     addr=sym[n] if is_c else a
     def hook(uc,address,size,data,n=n):
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
      if n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
      elif n=='audio_log_extended':trace.append(('extended',r0,bytes(uc.mem_read(r3,80)).split(b'\0')[0],int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')))
      elif n=='compressed_log_output':
       msg=bytes(uc.mem_read(r1,80)).split(b'\0')[0]
       trace.append(('compressed',r0,msg,r3 if b'%' in msg else None))
      elif n=='audio_settings_terminal_mode':trace.append(('mode',));uc.reg_write(UC_ARM_REG_R0,0)
      elif n in ('audio_event_loop_remove_delayed','audio_event_loop_push_delayed'):
       trace.append((n,cb_map.get(r0|1,hex(r0)),r1,r2) if 'push' in n else (n,cb_map.get(r0|1,hex(r0))))
       uc.reg_write(UC_ARM_REG_R0,0)
      elif n=='audio_uart_ring_mode_update_472362':trace.append((n,r0))
      else:trace.append((n,))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,bits);u.reg_write(UC_ARM_REG_R1,0x12345678)
    u.emu_start((sym['audio_uart_ring_notify_event_4c507e'] if is_c else 0x4c507e)|1,0x600000,count=10000)
    pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(hex(bits),level,pair)
 print('PASS_RING_NOTIFY_EVENT_NATIVE',len(cases)*2)
