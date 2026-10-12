#!/usr/bin/env python3
"""Actual C/native security-auth allocation/encode/send parent effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_security_auth_notify_impl.c'
N=['file_heap_allocate','audio_uart_buffer_zero','audio_pb_ostream_from_buffer','audio_uart_checksum_copy','g2_flashdb_candidate_tick','audio_pb_encode','audio_ble_notify_direct_475aa6','file_heap_free','audio_log_flags','audio_log_extended','compressed_log_output']
A=[0x474cd2,0x43c0e4,0x4905f4,0x439c04,0x4490cc,0x490c32,0x475aa6,0x474d16,0x43d0ce,0x43d574,0x43ce9e]
STUB='''#include <stdint.h>
uint8_t audio_ble_pair_auth_flag_20074ffc;
void *file_heap_allocate(uint32_t x){(void)x;return 0;} void file_heap_free(void *p){(void)p;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void audio_uart_checksum_copy(void *p,const void *s,uint32_t n){(void)p;(void)s;(void)n;}
void audio_pb_ostream_from_buffer(void *s,void *p,uint32_t n){(void)s;(void)p;(void)n;}
uint32_t audio_pb_encode(void *s,const void *d,const void *p){(void)s;(void)d;(void)p;return 0;}
const uint8_t audio_ble_ring_connect_pb_descriptor[4]={1,2,3,4};
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint32_t audio_ble_notify_direct_475aa6(uint8_t a,uint8_t b,void *p,uint16_t n){(void)a;(void)b;(void)p;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,PB_TxEncodeNotifySecAuthImpl',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,True,True,0,0,0),(1,False,True,0,0,0),(1,True,False,0,0,0),(1,True,True,0,0,0),(1,True,True,1,1,0),(1,True,True,0,1,0),(1,False,True,0,0,2),(1,True,False,0,0,1),(1,True,True,1,1,4)]
 for enabled,alloc,encode,send,auth,flags in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sy['audio_ble_pair_auth_flag_20074ffc'] if is_c else 0x20074ffc;u.mem_write(cell,bytes([enabled]))
   packet=0x20080000;u.mem_write(packet,b'\xcc'*0x1a8)
   addr=[sy[n]&~1 for n in N] if is_c else A;calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
    if ix==0:calls.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,packet if alloc else 0)
    elif ix==1:uc.mem_write(r0,bytes([r2&255])*r1);calls.append(('zero',r1,r2))
    elif ix==2:uc.mem_write(r0,(0).to_bytes(4,'little')+r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(8));calls.append(('ostream',r1==packet,r2))
    elif ix==3:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));calls.append(('copy',r2))
    elif ix==4:uc.reg_write(UC_ARM_REG_R0,0x1234);calls.append(('tick',))
    elif ix==5:uc.mem_write(r0+12,(18).to_bytes(4,'little'));calls.append(('encode',r2==packet+0xd4));uc.reg_write(UC_ARM_REG_R0,1 if encode else 0)
    elif ix==6:calls.append(('send',r0&255,r1&255,r2==packet,r3&0xffff,bytes(uc.mem_read(packet+0xd4,16))));uc.reg_write(UC_ARM_REG_R0,send)
    elif ix==7:calls.append(('free',r0==packet))
    elif ix==8:uc.reg_write(UC_ARM_REG_R0,flags)
    elif ix==9:
     sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');fmt=int.from_bytes(uc.mem_read(sp+4,4),'little')
     calls.append(('log',r0&255,line,bytes(uc.mem_read(fmt,64)).split(b'\0')[0]))
    elif ix==10:calls.append(('compact',r0,bytes(uc.mem_read(r1,64)).split(b'\0')[0]))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,auth);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['PB_TxEncodeNotifySecAuthImpl'] if is_c else 0x4bb73a)|1,0x600000,count=4000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(packet+0xd4,16)) if alloc and enabled else b''))
  assert pair[0]==pair[1],(enabled,alloc,encode,send,auth,flags,pair)
print('PASS_BLE_SECURITY_AUTH_NOTIFY_IMPL_NATIVE',len(cases))
