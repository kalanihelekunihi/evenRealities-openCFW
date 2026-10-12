#!/usr/bin/env python3
"""Native/C DM reset, privacy clear, role and SMP compare descendants."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_pair_children.c'
stub='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];uint8_t audio_dm_connection_records[256];
__attribute__((naked)) void *WsfMsgAlloc(uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void WsfMsgSend(uint8_t h,void*m){__asm volatile("bx lr");}
__attribute__((naked)) void SmpScGetCancelMsgWithReattempt(uint8_t c,void*m,uint8_t e){__asm volatile("bx lr");}
__attribute__((naked)) void SmpDmMsgSend(void*m){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_pair_compare_trace(void){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmPrivClearResList',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('clear','reset','role','value','rsp','ready'):
  opts={'clear':[(a,0) for a in (0,1)],'reset':[(a,0) for a in (0,1)],'role':[(a,0) for a in range(256)],'value':[(a,0) for a in (0,1,999999,1000000,0x12345678,0xffffffff)],'rsp':[(a,b) for a in (0,1) for b in (0,1)],'ready':[(0,0)]}[mode]
  for value,other in opts:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    dm=sym['audio_ble_dm_handler_state'] if is_c else 0x20073b78
    conn=sym['audio_dm_connection_records'] if is_c else 0x200712a4
    u.mem_write(dm+0xc,b'\x09');u.mem_write(dm+0x10,b'\x01')
    roles=bytearray(256)
    for i in range(1,4):roles[i*48-0x17]=i+3
    u.mem_write(conn,bytes(roles))
    rec=0x2007f100;message=0x2007f200;buf=bytearray(64);buf[0]=2;buf[4]=2;buf[0xc:0x10]=int(value).to_bytes(4,'big');buf[0x10:0x14]=int(value).to_bytes(4,'big');u.mem_write(rec,bytes(buf));u.mem_write(message,bytes([0xa5]*64))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='role':u.reg_write(UC_ARM_REG_R0,value)
    elif mode=='value':u.reg_write(UC_ARM_REG_R0,rec)
    elif mode=='rsp':u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,other)
    elif mode=='ready':u.reg_write(UC_ARM_REG_R0,rec)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x4bf99e,sym['WsfMsgAlloc']&~1):seen.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,message if value else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4bf9ba,sym['WsfMsgSend']&~1):seen.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-message));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x56d188,sym['SmpScGetCancelMsgWithReattempt']&~1):seen.append(('cancel',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-message,uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x537bd6,sym['SmpDmMsgSend']&~1):seen.append(('smp_send',uc.reg_read(UC_ARM_REG_R0)-message));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x534948,sym['DmSecGetCompareValue']&~1) and mode=='ready':seen.append(('compare',uc.reg_read(UC_ARM_REG_R0)-rec));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x4bd91e,sym['audio_ble_pair_compare_trace']&~1):seen.append(('trace',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x534910,sym['DmSecCompareRsp']&~1) and mode=='ready':seen.append(('rsp',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'clear':'DmPrivClearResList','reset':'DmDevReset','role':'DmConnRole','value':'DmSecGetCompareValue','rsp':'DmSecCompareRsp','ready':'audio_ble_pair_key_ready'}[mode]] if is_c else {'clear':0x4d28b0,'reset':0x4b3026,'role':0x4b73c4,'value':0x534948,'rsp':0x534910,'ready':0x4bb030}[mode]
    u.emu_start(entry|1,0x600000,count=400)
    result=(seen,bytes(u.mem_read(dm+0x10,1)) if mode=='reset' else None,bytes(u.mem_read(message,8)) if mode in ('clear','reset','rsp') else None,u.reg_read(UC_ARM_REG_R0) if mode in ('role','value') else None)
    pair.append(result)
   assert pair[0]==pair[1],(mode,value,other,pair)
   cases+=1
 print('PASS_BLE_DM_PAIR_CHILDREN_NATIVE',cases)
