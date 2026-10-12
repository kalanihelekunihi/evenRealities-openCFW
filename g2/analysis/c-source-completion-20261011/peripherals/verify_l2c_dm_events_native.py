#!/usr/bin/env python3
"""Stock/C DM L2CAP event bytes including inherited registers."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/l2c_dm_event_children.c'
SHIM='''#include <stdint.h>
uint8_t audio_dm_connection_records[0xb0];
uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t h){(void)h;return 0;}
void audio_ble_dm_conn_upd_execute_4b6532(uint8_t*c,const uint8_t*e){(void)c;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'dm.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_l2c_conn_update_ind_55bc96',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=['audio_ble_dm_l2c_conn_update_ind_55bc96','audio_ble_dm_l2c_conn_update_cnf_56e580','audio_ble_dm_l2c_cmd_rej_ind_56e5a4']
 stock=[0x55bc96,0x56e580,0x56e5a4]
 def run(c,kind,found,ambient):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  cell=sy['audio_dm_connection_records'] if c else 0x200712a4
  callback=0x20090001;u.mem_write(cell+0x9c,struct.pack('<I',callback))
  child=(sy['audio_ble_dm_conn_ccb_by_handle_4b601c']&~1) if c else 0x4b601c
  execute=(sy['audio_ble_dm_conn_upd_execute_4b6532']&~1) if c else 0x4b6532
  effects=[]
  def hook(uc,addr,size,user):
   if addr==child:
    effects.append(('lookup',uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_R0,0x20082000 if found else 0)
   elif addr==execute:
    p=uc.reg_read(UC_ARM_REG_R1);effects.append(('execute',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,12 if kind==0 else 8))))
   elif addr==callback:
    p=uc.reg_read(UC_ARM_REG_R0);effects.append(('callback',bytes(uc.mem_read(p,8))))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  params={UC_ARM_REG_R0:0x1234 if kind else 5,UC_ARM_REG_R1:0xabcd if kind else 0x1234,
          UC_ARM_REG_R2:ambient if kind else 0x20080000,UC_ARM_REG_R3:ambient^0xa5c3f01d,
          UC_ARM_REG_R5:ambient,UC_ARM_REG_SP:0x200ff000,UC_ARM_REG_LR:0x600001}
  for reg,value in params.items():u.reg_write(reg,value)
  entry=(sy[names[kind]]&~1) if c else stock[kind]
  u.emu_start(entry|1,0x600000,count=20000)
  return effects
 cases=0
 for kind in range(3):
  for found in (False,True):
   for ambient in (0,0x12345678,0xffa50012):
    a=run(False,kind,found,ambient);b=run(True,kind,found,ambient)
    assert a==b,(kind,found,hex(ambient),a,b)
    cases+=1
 print('PASS_L2C_DM_EVENTS_NATIVE',cases)
