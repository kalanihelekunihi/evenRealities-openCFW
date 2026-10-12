#!/usr/bin/env python3
"""Actual ARM C/stock HCI LE encrypt command assembly and send gating."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_le_encrypt_cmd.c'
STUB='''#include <stdint.h>
uint32_t allocation,alloc_opcode,alloc_length,send_ptr,send_count;
void *audio_ble_hci_cmd_alloc_52ae38(uint16_t op,uint16_t n){alloc_opcode=op;alloc_length=n;return (void *)allocation;}
void audio_ble_hci_cmd_send(void*p){send_ptr=(uint32_t)p;send_count++;}
void *memcpy(void*d,const void*s,unsigned long n){uint8_t*a=d;const uint8_t*b=s;for(unsigned long i=0;i<n;i++)a[i]=b[i];return d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,HciLeEncryptCmd',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocated in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   key,plain,cmd=0x20080000,0x20080100,0x20080200
   u.mem_write(key,bytes(range(16)));u.mem_write(plain,bytes(range(0x70,0x80)))
   u.mem_write(cmd,bytes([0xa5]*40))
   if compiled:u.mem_write(sy['allocation'],(cmd if allocated else 0).to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x52ae38:
      calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)&0xffff,uc.reg_read(UC_ARM_REG_R1)&0xffff))
      uc.reg_write(UC_ARM_REG_R0,cmd if allocated else 0)
     else:calls.append(('send',uc.reg_read(UC_ARM_REG_R0)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x52ae38,0x52ae5e):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,plain)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['HciLeEncryptCmd'] if compiled else 0x52b266)|1,0x600000,count=8000)
   if compiled:
    val=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    calls=[('alloc',val('alloc_opcode'),val('alloc_length'))]
    if val('send_count'):calls.append(('send',val('send_ptr')))
   pair.append((bytes(u.mem_read(cmd,40)),calls))
  assert pair[0]==pair[1],(allocated,pair)
print('PASS_BLE_HCI_LE_ENCRYPT_CMD_NATIVE 2')
