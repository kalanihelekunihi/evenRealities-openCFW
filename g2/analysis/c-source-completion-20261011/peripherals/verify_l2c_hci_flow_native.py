#!/usr/bin/env python3
"""Original/C L2CAP flow callback event and preserved incoming R3 byte."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/l2c_hci_flow_callback.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_l2c_state[0x30];
uint8_t DmConnIdByHandle(uint16_t h){(void)h;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'flow.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_hci_flow_530aa4',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,conn,count,ambient,mutate=False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_l2c_state'] if c else 0x200737d8
  for i in range(3):u.mem_write(state+12+i*4,struct.pack('<I',0x20090001+i*0x100))
  dm=(sy['DmConnIdByHandle']&~1) if c else 0x4b6e96
  callbacks={0x20090000+i*0x100 for i in range(3)};calls=[]
  def hook(uc,addr,size,user):
   if addr==dm:
    uc.reg_write(UC_ARM_REG_R0,conn);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif addr in callbacks:
    p=uc.reg_read(UC_ARM_REG_R0);calls.append((addr,bytes(uc.mem_read(p,4))))
    if mutate and len(calls)<3:
     v=int.from_bytes(bytes(uc.mem_read(p,4)),'little')^0x55a00110
     uc.mem_write(p,struct.pack('<I',v))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,0x1234),(UC_ARM_REG_R1,count),(UC_ARM_REG_R2,0x11223344),(UC_ARM_REG_R3,ambient),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_ble_l2c_hci_flow_530aa4'] if c else 0x530aa4)|1,0x600000,count=20000)
  return u.reg_read(UC_ARM_REG_R0),calls
 cases=0
 for mutate in (False,True):
  for conn in (0,1,5):
   for count in (0,1,255,0x1234):
    for ambient in (0,0x12000000,0xffabcdef):
     a=run(False,conn,count,ambient,mutate);b=run(True,conn,count,ambient,mutate)
     assert a==b,(conn,count,ambient,mutate,a,b)
     cases+=1
 print('PASS_L2C_HCI_FLOW_NATIVE',cases)
