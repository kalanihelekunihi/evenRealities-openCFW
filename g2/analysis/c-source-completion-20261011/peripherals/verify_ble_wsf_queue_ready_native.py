#!/usr/bin/env python3
"""Native/C WSF queue pointer, enqueue metadata and ready transitions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_queue_ready.c'
stub='''
#include <stdint.h>
uint8_t audio_wsf_task_state[0x40];
__attribute__((naked)) void WsfQueueEnq(void*q,void*m){__asm volatile("bx lr");}
__attribute__((naked)) void WsfCsEnter(void){__asm volatile("bx lr");}
__attribute__((naked)) void WsfCsExit(void){__asm volatile("bx lr");}
__attribute__((naked)) void WsfSetOsSpecificEvent(void){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfTaskMsgQueue',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('queue','enq','ready'):
  for bit in (0,1,4):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    state=sym['audio_wsf_task_state'] if is_c else 0x20073230
    payload=0x2007f008;queue=state+0x34
    u.mem_write(payload-8,bytes([0xa5]*20));u.mem_write(state+0x3c,bytes((0x40,)))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='enq':u.reg_write(UC_ARM_REG_R0,queue);u.reg_write(UC_ARM_REG_R1,7);u.reg_write(UC_ARM_REG_R2,payload)
    else:u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,bit)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x538c24,sym['WsfQueueEnq']&~1):seen.append(('enq',uc.reg_read(UC_ARM_REG_R0)-state,uc.reg_read(UC_ARM_REG_R1)-payload));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52b8a4,sym['WsfCsEnter']&~1):seen.append(('enter',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52b8b6,sym['WsfCsExit']&~1):seen.append(('exit',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52b8d8,sym['WsfSetOsSpecificEvent']&~1):seen.append(('signal',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'queue':'WsfTaskMsgQueue','enq':'WsfMsgEnq','ready':'WsfTaskSetReady'}[mode]] if is_c else {'queue':0x52b97c,'enq':0x4bf9de,'ready':0x52b95e}[mode]
    u.emu_start(entry|1,0x600000,count=300)
    pair.append(((u.reg_read(UC_ARM_REG_R0)-state) if mode=='queue' else None,seen,bytes(u.mem_read(payload-8,20)) if mode=='enq' else bytes(u.mem_read(state+0x3c,1)) if mode=='ready' else b''))
   assert pair[0]==pair[1],(mode,bit,pair)
   cases+=1
 print('PASS_BLE_WSF_QUEUE_READY_NATIVE',cases)
