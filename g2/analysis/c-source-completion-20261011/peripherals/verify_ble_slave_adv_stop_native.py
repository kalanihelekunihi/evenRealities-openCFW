#!/usr/bin/env python3
"""Compiled-C/native slave disconnect discovery callback branch comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_adv_stop.c'
STUB='''#include <stdint.h>
uint8_t *audio_ble_slave_subcontext;
uint8_t audio_ble_subsystem_rows_200733fc[48];
void audio_ble_service_discovery_restart_531f20(uint8_t c){(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,dmSlaveAdvStopOnDisconnect',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,disconnected,match,action,range_hit,status):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  event=0x20081000;sub=0x20082000;data=0x20083000;values=0x20084000
  rows=sy['audio_ble_subsystem_rows_200733fc'] if compiled else 0x200733fc
  cell=sy['audio_ble_slave_subcontext'] if compiled else 0x20074334
  u.mem_write(cell,sub.to_bytes(4,'little'));u.mem_write(sub,b'\x34\x12')
  ev=bytearray(12);ev[0]=1;ev[3]=0 if disconnected else 1;ev[4:8]=data.to_bytes(4,'little');ev[8:10]=action.to_bytes(2,'little');ev[10:12]=(0x1234 if match else 0x2345).to_bytes(2,'little');u.mem_write(event,bytes(ev))
  u.mem_write(data,b'\x10\x00\x20\x00');u.mem_write(values,(0x15 if range_hit else 0x30).to_bytes(2,'little'))
  row=bytearray(16);row[4:8]=values.to_bytes(4,'little');row[10]=1;row[11]=status;u.mem_write(rows,bytes(row))
  trace=[];a=(sy['audio_ble_service_discovery_restart_531f20']&~1) if compiled else 0x531f20
  def hook(uc,pc,n,user):
   trace.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R7,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['dmSlaveAdvStopOnDisconnect'] if compiled else 0x46dfd0)|1,0x600000,count=4000)
  return trace,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for disconnected in (0,1):
  for match in (0,1):
   for action in (0,4):
    for range_hit in (0,1):
     for status in (0,1):
      args=(disconnected,match,action,range_hit,status)
      a,b=run(False,*args),run(True,*args)
      assert a==b,(args,a,b)
      cases+=1
 print('PASS_BLE_SLAVE_ADV_STOP_NATIVE',cases)
