"""Compiled-C/native SendDataToBoth ownership and queue branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_settings_peer_send_queue,*audio_settings_peer_event;
void *audio_uart_alloc_retry(uint32_t a){(void)a;return 0;}
void audio_file_heap_free(void*a){(void)a;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_log_event_set_task(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_send_status_message',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_status_send.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for case in ('no_queue','alloc1_fail','alloc2_fail','success','queue_fail'):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   queue=syms['audio_settings_peer_send_queue'] if compiled else 0x200749cc
   event=syms['audio_settings_peer_event'] if compiled else 0x20074b10
   u.mem_write(queue,struct.pack('<I',0 if case=='no_queue' else 0x20088000));u.mem_write(event,struct.pack('<I',0x20089000))
   u.mem_write(0x20090000,b'PAYLOAD!');u.mem_write(0x20091000,b'\xaa'*12);u.mem_write(0x20092000,b'\xaa'*16)
   cuts={syms['audio_uart_alloc_retry']&~1:'alloc',syms['audio_file_heap_free']&~1:'free',syms['audio_uart_buffer_zero']&~1:'zero',syms['audio_queue_copy_bytes']&~1:'copy',syms['audio_cmsis_queue_put']&~1:'queue',syms['g2_log_event_set_task']&~1:'event',syms['audio_log_level']&~1:'level'} if compiled else {0x4646f0:'alloc',0x474d16:'free',0x43c0e4:'zero',0x439be4:'copy',0x449abe:'queue',0x4495e4:'event',0x43d0ce:'level'}
   calls=[];allocs=[0]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if not kind:return
    r0,r1,r2,r3=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    if kind=='level':uc.reg_write(UC_ARM_REG_R0,0)
    elif kind=='alloc':
     allocs[0]+=1;calls.append(('alloc',r0))
     ptr=0x20091000 if allocs[0]==1 else 0x20092000
     if (case=='alloc1_fail' and allocs[0]==1) or (case=='alloc2_fail' and allocs[0]==2):ptr=0
     uc.reg_write(UC_ARM_REG_R0,ptr)
    elif kind=='free':calls.append(('free',r0))
    elif kind=='zero':
     calls.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&0xff])*r1)
    elif kind=='copy':
     calls.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
    elif kind=='queue':
     calls.append(('queue',r0,r2,r3,struct.unpack('<I',uc.mem_read(r1,4))[0]));uc.reg_write(UC_ARM_REG_R0,5 if case=='queue_fail' else 0)
    elif kind=='event':calls.append(('event',r0,r1));uc.reg_write(UC_ARM_REG_R0,2)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x103,0x20090000,8,0x12345678)):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_send_status_message'] if compiled else 0x464d1c)|1,0x600000,count=5000)
   observations.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20091000,12)),bytes(u.mem_read(0x20092000,16))))
  assert observations[0]==observations[1],(case,observations)
  print('PASS status send',case)
