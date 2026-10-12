#!/usr/bin/env python3
"""Bounded native/C SMP repeated-attempt record and timer effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_db_max_attempts.c'
STUB='''#include <stdint.h>
const uint8_t *audio_ble_comm_registration_slot;
uint8_t *smpDbGetRecord(uint8_t c){(void)c;return 0;}
void smpDbStartServiceTimer(void){}
void audio_ble_smp_db_diagnostic(const char*n,uint32_t l,const char*m,uint8_t a,uint32_t x,uint32_t y){(void)n;(void)l;(void)m;(void)a;(void)x;(void)y;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,SmpDbMaxAttemptReached',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mult in (0,1,2,0xffff):
  for timeout,max_timeout in ((3000,64000),(40000,50000)):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for addr,data in seg:u.mem_write(addr,data)
    record,cfg=0x20080000,0x20080100
    u.mem_write(record,bytes([0xa5]*0x18));u.mem_write(record+8,mult.to_bytes(2,'little'))
    u.mem_write(cfg,timeout.to_bytes(4,'little'))
    u.mem_write(cfg+0xc,max_timeout.to_bytes(4,'little'))
    u.mem_write(cfg+0x10,(12345).to_bytes(4,'little'))
    u.mem_write(cfg+0x14,(3).to_bytes(2,'little'))
    slot=sy['audio_ble_comm_registration_slot'] if compiled else 0x200004b8
    u.mem_write(slot,cfg.to_bytes(4,'little'))
    calls=[]
    addrs={name:sy[name]&~1 for name in ('smpDbGetRecord','audio_ble_smp_db_diagnostic','smpDbStartServiceTimer')} if compiled else {'smpDbGetRecord':0x541fb8,'trace_level':0x4c9c50,'WsfTrace':0x52a63c,'smpDbStartServiceTimer':0x541e34}
    def hook(uc,pc,n,user):
     if pc==addrs['smpDbGetRecord']:uc.reg_write(UC_ARM_REG_R0,record)
     elif pc==addrs.get('trace_level'):uc.reg_write(UC_ARM_REG_R0,0)
     elif pc==addrs['smpDbStartServiceTimer']:calls.append('timer')
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for addr in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
    u.reg_write(UC_ARM_REG_R0,5);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['SmpDbMaxAttemptReached'] if compiled else 0x5426c0)|1,0x600000,count=3000)
    pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(record,0x18)),calls))
   assert pair[0]==pair[1],(mult,timeout,max_timeout,pair)
print('PASS_BLE_SMP_DB_MAX_NATIVE 8')
