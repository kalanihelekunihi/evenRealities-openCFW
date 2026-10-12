#!/usr/bin/env python3
"""Actual compiled ARM C/stock WSF pool free-list transition comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_buf_free.c'
STUB='''#include <stdint.h>
void *audio_wsf_pool_list; volatile uint8_t audio_wsf_pool_count;
uint32_t cs_enter_count,cs_exit_count;
void WsfCsEnter(void){cs_enter_count++;}
void WsfCsExit(void){cs_exit_count++;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfBufFree',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case in ('empty','low','high','below'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   pool=0x20081000;block=0x20082000
   rows=bytearray(24)
   rows[4:8]=(0x20081800).to_bytes(4,'little')
   rows[8:12]=(0x20083000).to_bytes(4,'little')
   rows[16:20]=(0x20082800).to_bytes(4,'little')
   rows[20:24]=(0x20084000).to_bytes(4,'little')
   u.mem_write(pool,bytes(rows));u.mem_write(block,bytes([0xa5]*16))
   count=0 if case=='empty' else 2
   address=block if case=='low' else (0x20082a00 if case=='high' else 0x20081700)
   u.mem_write(address,bytes([0xa5]*16))
   if compiled:
    u.mem_write(sym['audio_wsf_pool_list'],pool.to_bytes(4,'little'))
    u.mem_write(sym['audio_wsf_pool_count'],bytes([count]))
   else:
    u.mem_write(0x20074eec,pool.to_bytes(4,'little'))
    u.mem_write(0x20075044,bytes([count]))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     calls.append(pc);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x52b8a4,0x52b8b6):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,address);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['WsfBufFree'] if compiled else 0x5304d4)|1,0x600000,count=4000)
   if compiled:
    v=lambda name:int.from_bytes(u.mem_read(sym[name],4),'little')
    calls=[0x52b8a4]*v('cs_enter_count')+[0x52b8b6]*v('cs_exit_count')
   pair.append((bytes(u.mem_read(pool,24)),bytes(u.mem_read(address,16)),calls))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_WSF_BUF_FREE_NATIVE 4')
