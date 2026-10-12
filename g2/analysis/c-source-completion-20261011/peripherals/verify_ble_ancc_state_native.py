#!/usr/bin/env python3
"""Compare compiled C and stock ANCC state children on actual RAM effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_state_children.c'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text('''#include <stdint.h>\nuint8_t audio_ble_ancc_state[0x600];\nvoid audio_ble_ancc_reset_state_machine(void){}\n''')
 elf=t/'ancc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_action_pop_4bea36',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,name,init,arg0=0,arg1=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_ble_ancc_state'] if c else 0x200695c8
  u.mem_write(base,bytes(init))
  reset=(sy['audio_ble_ancc_reset_state_machine']&~1) if c else 0x4bf6c4
  effects=[]
  def hook(uc,a,size,user):
   if a==reset:effects.append('reset');uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,arg0),(UC_ARM_REG_R1,arg1),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  addr=(sy[name]&~1) if c else {'audio_ble_ancc_conn_open_4bea04':0x4bea04,'audio_ble_ancc_conn_close_4bea14':0x4bea14,'audio_ble_ancc_no_connection_active_4bea24':0x4bea24,'audio_ble_ancc_action_pop_4bea36':0x4bea36}[name]
  u.emu_start(addr|1,0x600000,count=30000)
  return bytes(u.mem_read(base,len(init))),u.reg_read(UC_ARM_REG_R0),effects
 init=bytearray(0x600)
 cases=0
 for name in ('audio_ble_ancc_conn_open_4bea04','audio_ble_ancc_conn_close_4bea14','audio_ble_ancc_no_connection_active_4bea24','audio_ble_ancc_action_pop_4bea36'):
  for mode in (0,1,2,3):
   b=bytearray(init);b[0]=0 if mode==0 else 3
   if mode==1:b[0x318]=1
   if mode==2:b[0x30c]=1
   if mode==3:b[0x24]=1
   a=run(False,name,b,0x5a,0x12345678);d=run(True,name,b,0x5a,0x12345678)
   # ARM native R7 is an ambient return for open/close; compare only effects.
   assert a[0]==d[0] and a[2]==d[2] and (name in ('audio_ble_ancc_conn_open_4bea04','audio_ble_ancc_conn_close_4bea14') or a[1]==d[1]),(name,mode,a[:2],d[:2])
   cases+=1
 print('PASS_BLE_ANCC_STATE_NATIVE',cases)
