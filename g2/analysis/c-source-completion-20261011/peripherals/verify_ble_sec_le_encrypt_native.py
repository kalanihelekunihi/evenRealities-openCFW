#!/usr/bin/env python3
"""Actual ARM C/stock LE encrypt queue and reversed block effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_sec_le_encrypt.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[128],encrypt_key[16],encrypt_plain[16];
uint32_t enq_handler,enq_buffer,enq_count,encrypt_count;
void WStrReverseCpy(uint8_t*d,const uint8_t*s,uint16_t n){for(uint16_t i=0;i<n;i++)d[n-1-i]=s[i];}
void WsfMsgEnq(void*q,uint8_t h,void*b){(void)q;enq_handler=h;enq_buffer=(uint32_t)b;enq_count++;}
void HciLeEncryptCmd(const uint8_t*k,const uint8_t*p){for(int i=0;i<16;i++){encrypt_key[i]=k[i];encrypt_plain[i]=p[i];}encrypt_count++;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SecLeEncryptCmd',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for seed in (0,0x31):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   key,plain,buf=0x20080000,0x20080100,0x20080200
   u.mem_write(key,bytes((seed+i)&255 for i in range(16)))
   u.mem_write(plain,bytes((seed+0x80+i)&255 for i in range(16)))
   observed=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x4bf9de:
      observed.append(('enq',uc.reg_read(UC_ARM_REG_R1)&255,uc.reg_read(UC_ARM_REG_R2)))
     else:
      k,p=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)
      observed.append(('encrypt',bytes(uc.mem_read(k,16)),bytes(uc.mem_read(p,16))))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x4bf9de,0x52b266):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,plain)
   u.reg_write(UC_ARM_REG_R2,buf);u.reg_write(UC_ARM_REG_R3,0x36)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['SecLeEncryptCmd'] if compiled else 0x5363ae)|1,0x600000,count=10000)
   if compiled:
    val=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    if val('enq_count'):observed.append(('enq',val('enq_handler'),val('enq_buffer')))
    if val('encrypt_count'):observed.append(('encrypt',bytes(u.mem_read(sy['encrypt_key'],16)),bytes(u.mem_read(sy['encrypt_plain'],16))))
   pair.append(observed)
  assert pair[0]==pair[1],(seed,pair)
print('PASS_BLE_SEC_LE_ENCRYPT_NATIVE 2')
