#!/usr/bin/env python3
"""Native/C Cordio ECC message, HCI command, generation and key-copy effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_ecc.c'
stub='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18],audio_ble_ecc_key_storage[0x60],audio_ble_stack_state_20072cb8[0x50];
__attribute__((naked)) void *WsfMsgAlloc(uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void WsfMsgEnq(void*q,uint8_t h,void*m){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_ble_hci_cmd_alloc_52ae38(uint16_t op,uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_hci_cmd_send(void*m){__asm volatile("bx lr");}
__attribute__((naked)) void __aeabi_memcpy(void*d,const void*s,unsigned n){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmSecGenerateEccKeyReq',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('request','hci','generate','copy'):
  for allocated in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    dm=sym['audio_ble_dm_handler_state'] if is_c else 0x20073b78
    ecc=sym['audio_ble_ecc_key_storage'] if is_c else 0x200726d0
    queue=(sym['audio_ble_stack_state_20072cb8']+0x28) if is_c else 0x20072ce0
    packet=0x2007f200;key=0x2007f400;command=0x2007f700
    u.mem_write(dm+0xc,b'\x07');u.mem_write(packet,bytes([0xa5]*0xa0));u.mem_write(key,bytes(range(96)))
    u.mem_write(ecc,bytes([0x77]*96));u.mem_write(queue,bytes([0]*16))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='request':u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0x41)
    if mode=='copy':u.reg_write(UC_ARM_REG_R0,key)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x4bf99e,sym['WsfMsgAlloc']&~1):seen.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,packet if allocated else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4bf9de,sym['WsfMsgEnq']&~1):seen.append(('enq',uc.reg_read(UC_ARM_REG_R0)-queue,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)-packet));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52ae38,sym['audio_ble_hci_cmd_alloc_52ae38']&~1):seen.append(('cmd_alloc',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,command if allocated else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52ae5e,sym['audio_ble_hci_cmd_send']&~1):seen.append(('cmd_send',uc.reg_read(UC_ARM_REG_R0)-command));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x439be4,sym['__aeabi_memcpy']&~1):
      p=uc.reg_read(UC_ARM_REG_R0);q=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);uc.mem_write(p,bytes(uc.mem_read(q,n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'request':'audio_ble_dm_ecc_request','hci':'HciLeReadLocalP256PubKey','generate':'DmSecGenerateEccKeyReq','copy':'DmSecSetEccKey'}[mode]] if is_c else {'request':0x53673e,'hci':0x52b1f4,'generate':0x5348ec,'copy':0x5348fc}[mode]
    u.emu_start(entry|1,0x600000,count=500)
    pair.append((seen,bytes(u.mem_read(packet,0x40)) if mode in ('request','generate') else None,bytes(u.mem_read(ecc,96)) if mode=='copy' else None,u.reg_read(UC_ARM_REG_R0) if mode=='request' else None))
   assert pair[0]==pair[1],(mode,allocated,pair)
   cases+=1
 print('PASS_BLE_DM_ECC_NATIVE',cases)
