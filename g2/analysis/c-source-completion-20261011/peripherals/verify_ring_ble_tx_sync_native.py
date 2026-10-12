#!/usr/bin/env python3
"""Actual compiled C versus stock for bounded BLE TX semaphore branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_ble_tx_sync.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_wsf_thread_state[0x30];
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint32_t audio_delay(uint32_t x){return x;}
int32_t audio_semaphore_acquire(void *p,uint32_t x){(void)p;(void)x;return 0;}
int32_t audio_semaphore_release(void *p){(void)p;return 0;}
uint32_t audio_semaphore_get_count(void *p){(void)p;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_tx_ready_wait',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 mappings={'g2_flashdb_candidate_tick':0x4490cc,'audio_delay':0x449376,'audio_semaphore_acquire':0x44994e,'audio_semaphore_release':0x4499b8,'audio_semaphore_get_count':0x449a0e,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
 cases=[('take',False,0,0,0),('take',True,0,0,0),('take',True,1,0,0),('notify',False,0,0,0),('notify',True,0,0,0),('notify',True,1,0,0),('notify',True,0,1,7),('wait',True,0,0,0),('wait',True,1,0,0),('wait',True,1,0,7)]
 for kind,sem_present,sem_status,count,level in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sym['audio_ble_wsf_thread_state'] if is_c else 0x20004068;sem=0x2007f000
   u.mem_write(state+0x14,struct.pack('<I',sem if sem_present else 0))
   trace=[]
   for n,a in mappings.items():
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
     if n=='audio_semaphore_acquire':trace.append(('acquire',r0,r1));uc.reg_write(UC_ARM_REG_R0,sem_status)
     elif n=='audio_semaphore_release':trace.append(('release',r0));uc.reg_write(UC_ARM_REG_R0,sem_status)
     elif n=='audio_semaphore_get_count':trace.append(('count',r0));uc.reg_write(UC_ARM_REG_R0,count)
     elif n=='audio_delay':trace.append(('delay',r0));uc.reg_write(UC_ARM_REG_R0,0)
     elif n=='g2_flashdb_candidate_tick':trace.append(('tick',));uc.reg_write(UC_ARM_REG_R0,123)
     elif n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
     elif n=='audio_log_extended':trace.append(('extended',r0))
     else:trace.append(('compressed',r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   names={'take':('audio_ble_take_tx_ready',0x4d0b36),'notify':('audio_ble_tx_complete_notify',0x4d0c36),'wait':('audio_ble_tx_ready_wait',0x4d0b64)}
   name,stock=names[kind]
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,10)
   u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=10000)
   pair.append((trace,u.reg_read(UC_ARM_REG_R0) if kind=='take' else None))
  assert pair[0]==pair[1],(kind,sem_present,sem_status,count,level,pair)
 print('PASS_RING_BLE_TX_SYNC_NATIVE',len(cases))
