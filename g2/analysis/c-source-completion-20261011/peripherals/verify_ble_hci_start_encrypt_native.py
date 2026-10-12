#!/usr/bin/env python3
"""Actual C/native LE Start Encryption command bytes and send effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_start_encrypt.c'
STUB='''#include <stdint.h>
uint8_t *hciCmdAlloc(uint16_t o,uint8_t n){(void)o;(void)n;return 0;}
void hciCmdSend(uint8_t*c){(void)c;}
void __aeabi_memcpy(void*d,const void*s,unsigned n){uint8_t*x=d;const uint8_t*y=s;for(unsigned i=0;i<n;i++)x[i]=y[i];}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,HciLeStartEncryptionCmd',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocate in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   command,random,key=0x20080000,0x20080100,0x20080200
   u.mem_write(command,bytes([0xa5]*0x24));u.mem_write(random,bytes(range(8)))
   u.mem_write(key,bytes(range(16,32)))
   calls=[]
   addrs={'alloc':(sy['hciCmdAlloc']&~1) if compiled else 0x52ae38,
          'send':(sy['hciCmdSend']&~1) if compiled else 0x52ae5e}
   if not compiled:addrs['memcpy']=0x439be4
   def hook(uc,pc,n,user):
    r0,r1,r2=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if pc==addrs['alloc']:
     calls.append(('alloc',r0,r1));uc.reg_write(UC_ARM_REG_R0,command if allocate else 0)
    elif pc==addrs['send']:calls.append(('send',r0-command))
    else:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,0x3456);u.reg_write(UC_ARM_REG_R1,random)
   u.reg_write(UC_ARM_REG_R2,0x789a);u.reg_write(UC_ARM_REG_R3,key)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['HciLeStartEncryptionCmd'] if compiled else 0x52b5a2)|1,0x600000,count=2000)
   pair.append((bytes(u.mem_read(command,0x24)),calls))
  assert pair[0]==pair[1],(allocate,pair)
print('PASS_BLE_HCI_START_ENCRYPT_NATIVE 2')
