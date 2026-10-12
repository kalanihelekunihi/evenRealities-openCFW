#!/usr/bin/env python3
"""Original/C ATT handler class dispatch over authenticated live table."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_att_handler.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_handler_4b5146',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for event in (None,0,0x20,0x40,0x60,0x80,0xff):
  for high in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20010000,b'\x01\x00'+bytes([event or 0])+b'\0')
    for slot,index in ((0x3c,0),(0x40,1),(0x48,2),(0x44,3)):
     u.mem_write(0x200610ac+slot,struct.pack('<I',0x20030000+index*16))
     u.mem_write(0x20030008+index*16,struct.pack('<I',0x500001+index*2))
    u.mem_write(0x200610f8,struct.pack('<I',0x500009 if high else 0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R1,0 if event is None else 0x20010000)
    seen=[]
    def hook(uc,a,size,_):
     if 0x500000<=a<=0x500008:
      seen.append((a,uc.reg_read(UC_ARM_REG_R0)))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_handler_4b5146'] if is_c else 0x4b5146)|1,0x600000,count=500)
    pair.append(seen)
   assert pair[0]==pair[1],(event,high,pair)
   cases+=1
 print('PASS_BLE_ATT_HANDLER_NATIVE',cases)
