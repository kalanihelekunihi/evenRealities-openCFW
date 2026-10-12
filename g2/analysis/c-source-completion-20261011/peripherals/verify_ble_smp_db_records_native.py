#!/usr/bin/env python3
"""Native/C bounded SMP record availability, add and existing-match search."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_db_records.c'
stub='''#include <stdint.h>
uint8_t audio_ble_smp_database[0x100];volatile uint8_t audio_ble_trace_level_cell;
__attribute__((naked)) uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t n){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t l,const char*m,const char*p,const char*n,uint32_t x,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_wsf_trace(const char*a,const char*b,...){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t DmConnPeerAddrType(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t DmHostAddrType(uint8_t t){__asm volatile("bx lr");}
__attribute__((naked)) const uint8_t *DmConnPeerAddr(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){__asm volatile("bx lr");}
__attribute__((naked)) int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){__asm volatile("bx lr");}
__attribute__((naked)) void __aeabi_memcpy(void*d,const void*s,unsigned n){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,smpDbGetRecord',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('inuse','add','get'):
  for state in range(5):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    db=sym['audio_ble_smp_database'] if is_c else 0x200708ec
    trace=sym['audio_ble_trace_level_cell'] if is_c else 0x2007502f
    address=0x2007f100;u.mem_write(address,b'ABCDEF');u.mem_write(db,bytes([0]*0x100));u.mem_write(trace,b'\x01')
    rec=db+0x18
    if mode=='inuse':
     if state==1:u.mem_write(rec+7,b'\x01')
     if state==2:u.mem_write(rec+0xc,struct.pack('<I',1))
     if state==3:u.mem_write(rec+8,struct.pack('<H',1))
     if state==4:u.mem_write(rec+0xb,b'\xff')
    if mode in ('add','get'):
     for i in range(state if state<4 else 9):u.mem_write(db+0x18+i*0x18+7,b'\x01')
     if mode=='get' and state==3:
      u.mem_write(db+0x18+0x18,b'ABCDEF');u.mem_write(db+0x18+0x18+6,b'\x01')
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='inuse':u.reg_write(UC_ARM_REG_R0,rec)
    elif mode=='add':u.reg_write(UC_ARM_REG_R0,address);u.reg_write(UC_ARM_REG_R1,1)
    else:u.reg_write(UC_ARM_REG_R0,2)
    seen=[]
    def hook(uc,a,size,_):
     if a==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a==(sym['g2_smp_candidate_compare']&~1):
      x=uc.reg_read(UC_ARM_REG_R1);y=uc.reg_read(UC_ARM_REG_R2);n=uc.reg_read(UC_ARM_REG_R3);bx=bytes(uc.mem_read(x,n));by=bytes(uc.mem_read(y,n));uc.reg_write(UC_ARM_REG_R0,((bx>by)-(bx<by))&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4b6ed8,sym['DmConnPeerAddrType']&~1,0x4d2aa8,sym['DmHostAddrType']&~1):uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4b6eea,sym['DmConnPeerAddr']&~1):uc.reg_write(UC_ARM_REG_R0,address);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43c0e4,sym['audio_uart_buffer_zero']&~1):
      p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(p,bytes([0]*n));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4751c8,sym['g2_lfs_memcmp']&~1):
      x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);bx=bytes(uc.mem_read(x,n));by=bytes(uc.mem_read(y,n));uc.reg_write(UC_ARM_REG_R0,((bx>by)-(bx<by))&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x439be4,sym['__aeabi_memcpy']&~1):
      p=uc.reg_read(UC_ARM_REG_R0);q=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);uc.mem_write(p,bytes(uc.mem_read(q,n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'inuse':'smpDbRecordInUse','add':'smpDbAddDevice','get':'smpDbGetRecord'}[mode]] if is_c else {'inuse':0x541e50,'add':0x541e72,'get':0x541fb8}[mode]
    u.emu_start(entry|1,0x600000,count=3000)
    rv=u.reg_read(UC_ARM_REG_R0)
    pair.append((rv-db if mode!='inuse' and rv else rv,bytes(u.mem_read(db,0x100))))
   assert pair[0]==pair[1],(mode,state,pair[0][0],pair[1][0],[(i,a,b) for i,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:12])
   cases+=1
 print('PASS_BLE_SMP_DB_RECORDS_NATIVE',cases)
