#!/usr/bin/env python3
"""Native/C Cordio random ring, passkey event and SMP send effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SS=[R/'components/audio/uart_thread_source_candidate/display_ble_pair_key_process.c',R/'components/audio/uart_thread_source_candidate/display_ble_smp_send.c']
stub='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[0x50];uint8_t audio_ble_smp_handler_state[0xfc];
__attribute__((naked)) void HciLeRandCmd(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_slave_event_state(uint8_t e){__asm volatile("bx lr");}
__attribute__((naked)) void DmSecAuthRsp(uint8_t c,uint8_t k,const uint8_t*p){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_pair_passkey_trace(uint32_t n){__asm volatile("bx lr");}
__attribute__((naked)) void WsfMsgSend(uint8_t h,void*m){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_key_process',*[str(x) for x in SS],str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('random','passkey','connected','send'):
  opts={'random':[(cursor,count) for cursor in (0,1,3,4) for count in (0,1,4,8,9)],'passkey':[(gate,seed) for gate in (0,1) for seed in (0,1,0x12345678,0xffffffff)],'connected':[(cursor,0) for cursor in (0,1,2,3)],'send':[(i,0) for i in (0,1,7,255)]}[mode]
  for a,b in opts:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for x,d in seg:u.mem_write(x,d)
    state=sym['audio_ble_stack_state_20072cb8'] if is_c else 0x20072cb8
    smp=sym['audio_ble_smp_handler_state'] if is_c else 0x20070aec
    seed=bytes(range(32))+bytes(0x20);u.mem_write(state,seed);u.mem_write(state+0x3a,bytes((a if mode in ('random','connected') else 1,)));u.mem_write(smp+0xec,bytes((a if mode=='send' else 5,)))
    out=0x2007f000;msg=0x2007f100;u.mem_write(out,bytes([0xa5]*16));m=bytearray(16);m[0]=2;m[5]=a if mode=='passkey' else 1;u.mem_write(msg,bytes(m))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='random':u.reg_write(UC_ARM_REG_R0,out);u.reg_write(UC_ARM_REG_R1,b)
    else:u.reg_write(UC_ARM_REG_R0,msg)
    seen=[]
    def hook(uc,addr,size,_):
     if addr in (0x52b304,sym['HciLeRandCmd']&~1):seen.append(('hci_rand',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if addr in (0x4bd054,sym['audio_ble_slave_event_state']&~1):seen.append(('ui',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if addr in (0x53634e,sym['audio_ble_random_bytes']&~1) and mode=='passkey':
      seedv=b;uc.mem_write(uc.reg_read(UC_ARM_REG_R0),seedv.to_bytes(4,'little'));seen.append(('random',uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if addr in (0x4d24d4,sym['DmSecAuthRsp']&~1):seen.append(('auth',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R2),4))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if addr in (0x4bd7fa,sym['audio_ble_pair_passkey_trace']&~1):seen.append(('trace',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if addr in (0x4bf9ba,sym['WsfMsgSend']&~1):seen.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-msg));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'random':'audio_ble_random_bytes','passkey':'audio_ble_pair_key_process','connected':'audio_ble_pair_key_process','send':'SmpDmMsgSend'}[mode]] if is_c else {'random':0x53634e,'passkey':0x4bafda,'connected':0x4bafda,'send':0x537bd6}[mode]
    u.emu_start(entry|1,0x600000,count=500)
    pair.append((seen,bytes(u.mem_read(out,16)) if mode=='random' else None,bytes(u.mem_read(state+0x3a,1)) if mode=='random' else None))
   assert pair[0]==pair[1],(mode,a,b,pair)
   cases+=1
 print('PASS_BLE_PAIR_KEY_PROCESS_NATIVE',cases)
