#!/usr/bin/env python3
"""Actual C/native AES queue request effects, allocation and token rollover."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_sec_aes.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[0x50];
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgEnq(void*q,uint8_t h,void*m){(void)q;(void)h;(void)m;}
void HciLeEncryptCmd(uint8_t*k,uint8_t*p){(void)k;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,SecAes',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for fail in (False,True):
  for initial in (0x21,0xff):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for addr,data in seg:u.mem_write(addr,data)
    state=sy['audio_ble_stack_state_20072cb8'] if compiled else 0x20072cb8
    msg,key,plain=0x20080000,0x20080100,0x20080200
    u.mem_write(msg,bytes([0xa5]*0x38));u.mem_write(state+0x38,bytes([initial]))
    u.mem_write(key,bytes(range(16)));u.mem_write(plain,bytes(range(16,32)))
    calls=[]
    addrs={name:sy[name]&~1 for name in ('WsfMsgAlloc','WsfMsgEnq','HciLeEncryptCmd')} if compiled else {'WsfMsgAlloc':0x4bf99e,'WsfMsgEnq':0x4bf9de,'HciLeEncryptCmd':0x52b266}
    def hook(uc,pc,n,user):
     a,b,c=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
     if pc==addrs['WsfMsgAlloc']:
      calls.append(('alloc',a));uc.reg_write(UC_ARM_REG_R0,0 if fail else msg)
     elif pc==addrs['WsfMsgEnq']:calls.append(('enq',a-state,b,c-msg))
     else:calls.append(('encrypt',a-key,b-plain))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,plain)
    u.reg_write(UC_ARM_REG_R2,0x19);u.reg_write(UC_ARM_REG_R3,5)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,(0x0b).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['SecAes'] if compiled else 0x536426)|1,0x600000,count=3000)
    pair.append((u.reg_read(UC_ARM_REG_R0)&255,bytes(u.mem_read(msg,0x38)),
                 bytes(u.mem_read(state+0x38,1)),calls))
   assert pair[0]==pair[1],(fail,initial,pair)
print('PASS_BLE_SEC_AES_NATIVE 4')
