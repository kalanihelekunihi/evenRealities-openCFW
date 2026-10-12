#!/usr/bin/env python3
"""Compare pairing removal parent and lookup/clear RAM descendants with native."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_remove.c'
stub='''
#include <stdint.h>
uint8_t audio_ble_privacy_rows[2000];uint32_t audio_ble_pair_timestamp_counter_20074344;
__attribute__((naked)) uint8_t DmHostAddrType(uint8_t t){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_ble_privacy_compare_address(const uint8_t*a,const uint8_t*b){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_ble_privacy_rewrite_record(uint8_t *r){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t audio_ble_pair_record_validate(uint8_t *r){__asm volatile("bx lr");}
__attribute__((naked)) void DmPrivRemDevFromResList(uint8_t t,const uint8_t*r,uint8_t z){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_remove_pair',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('null','missing','found'):
  for flags in (0,1,2):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    addr=0x2007f000;row=0x20067a30;u.mem_write(addr,bytes((1,2,3,4,5,6)));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0 if mode=='null' else addr)
    seen=[]
    def string(uc,p):return bytes(uc.mem_read(p,180)).split(b'\0')[0]
    def hook(uc,a,size,_):
     if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43ce9e,sym['compressed_log_output']&~1):seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43d574,sym['audio_log_extended']&~1):
      line,p=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)));seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,p)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x47ad74,sym['audio_ble_pair_record_by_mac']&~1):seen.append(('lookup',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,row if mode=='found' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x47a47c,sym['audio_ble_pair_record_clear_full']&~1):seen.append(('clear',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4d2880,sym['DmPrivRemDevFromResList']&~1):seen.append(('privacy_remove',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_remove_pair'] if is_c else 0x47b59c)|1,0x600000,count=650)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(mode,flags,pair)
   cases+=1
 for match in (-1,0,5,9):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   base=sym['audio_ble_privacy_rows'] if is_c else 0x20067a30
   counter=sym['audio_ble_pair_timestamp_counter_20074344'] if is_c else 0x20074344
   rows=bytearray(2000)
   for i in range(10):rows[i*200+6]=1;rows[i*200+0x2f]=1
   u.mem_write(base,bytes(rows));u.mem_write(counter,struct.pack('<I',7))
   addr=0x2007f000;u.mem_write(addr,bytes((1,2,3,4,5,6)))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,addr)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x4d2aa8,sym['DmHostAddrType']&~1):seen.append(('type',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x4d294a,sym['audio_ble_privacy_compare_address']&~1):
     ix=(uc.reg_read(UC_ARM_REG_R0)-base)//200;seen.append(('compare',ix));uc.reg_write(UC_ARM_REG_R0,int(ix==match));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_pair_record_by_mac'] if is_c else 0x47ad74)|1,0x600000,count=650)
   ret=u.reg_read(UC_ARM_REG_R0);pair.append((seen,-1 if ret==0 else (ret-base)//200,bytes(u.mem_read(base,2000)),bytes(u.mem_read(counter,4))))
  assert pair[0]==pair[1],(match,pair)
  cases+=1
 print('PASS_BLE_PAIR_REMOVE_NATIVE',cases)
