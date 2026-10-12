#!/usr/bin/env python3
"""Bounded actual C/native effect comparison for ring-connect protobuf parent."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ring_connect_notify_impl.c'
names=['file_heap_allocate','audio_uart_buffer_zero','audio_pb_ostream_from_buffer','audio_uart_checksum_copy','g2_flashdb_candidate_tick','audio_uart_ring_target_addr_copy_4a2190','audio_ble_master_auth_mode_set','audio_ble_master_clear_failure_notify','audio_ble_slave_security_state','audio_pb_encode','audio_ble_notify_direct_475aa6','file_heap_free','audio_log_flags','audio_log_extended','compressed_log_output']
native=[0x474cd2,0x43c0e4,0x4905f4,0x439c04,0x4490cc,0x4a2190,0x4a2168,0x4a15c0,0x4b82e8,0x490c32,0x475aa6,0x474d16,0x43d0ce,0x43d574,0x43ce9e]
STUB='''#include <stdint.h>
void *file_heap_allocate(uint32_t x){(void)x;return 0;} void file_heap_free(void *p){(void)p;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void audio_uart_checksum_copy(void *p,const void *s,uint32_t n){(void)p;(void)s;(void)n;}
void audio_pb_ostream_from_buffer(void *s,void *p,uint32_t n){(void)s;(void)p;(void)n;}
uint32_t audio_pb_encode(void *s,const void *d,const void *p){(void)s;(void)d;(void)p;return 0;}
const uint8_t audio_ble_ring_connect_pb_descriptor[4]={1,2,3,4};
uint32_t g2_flashdb_candidate_tick(void){return 0;}
void audio_uart_ring_target_addr_copy_4a2190(uint8_t *p,uint32_t q){(void)p;(void)q;}
uint32_t audio_ble_master_auth_mode_set(uint8_t n){return n;}
void audio_ble_master_clear_failure_notify(void){}
void audio_ble_slave_security_state(uint8_t n){(void)n;}
uint32_t audio_ble_notify_direct_475aa6(uint8_t a,uint8_t b,void *p,uint16_t n){(void)a;(void)b;(void)p;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,PB_TxEncodeNotifyRingConnectInfoImpl',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for alloc,conn,encode,send,flags in ((False,0,True,False,0),(True,0,False,False,0),(True,1,False,False,0),(True,0,True,False,0),(True,1,True,False,0),(True,1,True,True,0),(False,0,True,False,2),(True,1,False,False,1),(True,1,True,True,4),(True,1,True,False,2)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   packet=0x20080000;u.mem_write(packet,b'\xcc'*0x1a8)
   addr=[sy[n]&~1 for n in names] if is_c else native;calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
    if ix==0:calls.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,packet if alloc else 0)
    elif ix==1:uc.mem_write(r0,bytes([r2&255])*r1);calls.append(('zero',r0==packet,r1,r2))
    elif ix==2:
     uc.mem_write(r0,(0).to_bytes(4,'little')+r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(8));calls.append(('ostream',r1==packet,r2))
    elif ix==3:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));calls.append(('copy',r2))
    elif ix==4:uc.reg_write(UC_ARM_REG_R0,0x1234);calls.append(('tick',))
    elif ix==5:uc.mem_write(r0,b'ABCDEF');calls.append(('target',r0==packet+0xe0,bool(r1)))
    elif ix==6:calls.append(('auth',r0&255));uc.reg_write(UC_ARM_REG_R0,3)
    elif ix==7:calls.append(('clear',))
    elif ix==8:calls.append(('security',r0&255))
    elif ix==9:
     uc.mem_write(r0+12,(18).to_bytes(4,'little'));calls.append(('encode',r2==packet+0xd4));uc.reg_write(UC_ARM_REG_R0,1 if encode else 0)
    elif ix==10:calls.append(('send',r0&255,r1&255,r2==packet,r3&0xffff,bytes(uc.mem_read(packet+0xd4,0x26))));uc.reg_write(UC_ARM_REG_R0,1 if send else 0)
    elif ix==11:calls.append(('free',r0==packet))
    elif ix==12:uc.reg_write(UC_ARM_REG_R0,flags)
    elif ix==13:
     sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');value=int.from_bytes(uc.mem_read(sp+8,4),'little')
     calls.append(('log',r0&255,line,value if line in (0x1b5,0x1bb) else None))
    elif ix==14:calls.append(('compact',r0,r3 if r0==0x10400000 else None))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['PB_TxEncodeNotifyRingConnectInfoImpl'] if is_c else 0x4bc1b4)|1,0x600000,count=4000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(packet+0xd4,0x26)) if alloc else b''))
  assert pair[0]==pair[1],(alloc,conn,encode,send,flags,pair)
print('PASS_BLE_RING_CONNECT_NOTIFY_IMPL_NATIVE 10 INCLUDING_LOGS')
