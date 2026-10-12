#!/usr/bin/env python3
"""Actual ARM C/native AppDbNewRecord free-slot and saturated-no-bond cases."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_record_create.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_privacy_rows[2000];uint32_t audio_ble_pair_timestamp_counter_20074344;
uint8_t audio_ble_pair_count(uint8_t role){uint8_t n=0;for(uint32_t i=0;i<10;i++)if(audio_ble_privacy_rows[i*200+47]&&audio_ble_privacy_rows[i*200+195]==role)n++;return n;}
uint8_t DmHostAddrType(uint8_t x){return x;}
void DmPrivRemDevFromResList(uint8_t a,const uint8_t*b,uint16_t c){(void)a;(void)b;(void)c;}
void audio_ble_pair_record_clear_full(uint8_t*x){x[47]=x[48]=0;}
void audio_uart_buffer_zero(void*x,uint32_t n,uint32_t v){volatile uint8_t*p=x;for(uint32_t i=0;i<n;i++)p[i]=v;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){volatile uint8_t*x=a;const volatile uint8_t*y=b;for(uint32_t i=0;i<n;i++)x[i]=y[i];return a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_record_create_47a71c',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('free','saturated'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   rows=sym['audio_ble_privacy_rows'] if compiled else 0x20067a30;counter=sym['audio_ble_pair_timestamp_counter_20074344'] if compiled else 0x20074344
   data=bytearray(2000)
   if kind=='saturated':
    for i in range(10):data[i*200+47]=1
   u.mem_write(rows,bytes(data));u.mem_write(counter,(7).to_bytes(4,'little'));address=0x20080000;u.mem_write(address,b'\x01\x02\x03\x04\x05\x06')
   for name,cs,stock in [('type','DmHostAddrType',0x4d2aa8),('flags','audio_log_flags',0x43d0ce)]:
    if compiled:continue
    def hook(uc,pc,n,user,name=name):
     if name=='flags':uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=stock,end=stock)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,address);u.reg_write(UC_ARM_REG_R2,1);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_pair_record_create_47a71c'] if compiled else 0x47a71c)|1,0x600000,count=7000)
   result=u.reg_read(UC_ARM_REG_R0);pair.append((result-rows if result else None,bytes(u.mem_read(rows,2000)),int.from_bytes(u.mem_read(counter,4),'little')))
  assert pair[0]==pair[1],(kind,pair[0][0],pair[1][0],pair[0][2],pair[1][2])
print('PASS_BLE_PAIR_RECORD_CREATE_NATIVE 2')
