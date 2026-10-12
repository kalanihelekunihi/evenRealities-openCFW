#!/usr/bin/env python3
"""Connected stock/C SMP callback selection and order."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_smp_callback.c'
STUB='''#include <stdint.h>
uint8_t audio_dm_connection_records[256], audio_ble_dm_handler_state[32];
uint32_t callback_log[4], callback_count;
void att_callback(void *p){callback_log[callback_count++]=0xa0000000u|(uint32_t)p;}
void client_callback(void *p){callback_log[callback_count++]=0xb0000000u|(uint32_t)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmSmpCbackExec',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for event_code in (0x2a,0x2c,0x2b):
  for att_enabled in (False,True):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    conn=sym['audio_dm_connection_records'] if compiled else 0x200712a4
    core=sym['audio_ble_dm_handler_state'] if compiled else 0x20073b78
    u.mem_write(conn+0x90,(sym['att_callback']|1 if att_enabled else 0).to_bytes(4,'little'))
    u.mem_write(core+8,(sym['client_callback']|1).to_bytes(4,'little'))
    event=0x20080000;data=bytearray(16);data[2]=event_code;u.mem_write(event,bytes(data))
    u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sym['DmSmpCbackExec'] if compiled else 0x4d24a8)|1,0x600000,count=3000)
    n=int.from_bytes(u.mem_read(sym['callback_count'],4),'little')
    pair.append((n,bytes(u.mem_read(sym['callback_log'],n*4))))
   assert pair[0]==pair[1],(event_code,att_enabled,pair)
print('PASS_BLE_DM_SMP_CALLBACK_NATIVE 6')
