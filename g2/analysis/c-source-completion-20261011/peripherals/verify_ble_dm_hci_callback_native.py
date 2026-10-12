#!/usr/bin/env python3
"""Original/C DM callback routing against the original immutable class map."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_hci_callback.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_handler_4d299c','-Wl,--defsym=audio_ble_dm_hci_event_class_map_6e006c=0x6e006c',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for code in (0,1,2,0x3e,0x80,0xff):
  for active in (0,1):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20010000,b'\0\0'+bytes([code])+b'\0')
    u.mem_write(0x20073b88,bytes([active]));u.mem_write(0x20000694,struct.pack('<I',0x20030000)*256)
    u.mem_write(0x20030004,struct.pack('<I',0x500001))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20010000)
    events=[]
    def hook(uc,a,size,_):
     if a==0x500000:
      events.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_dm_handler_4d299c'] if is_c else 0x4d299c)|1,0x600000,count=500)
    pair.append(events)
   assert pair[0]==pair[1],(code,active,pair)
   cases+=1
 for code in (0,1,7,8,0x20,0xff):
  for active in (0,1):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20010000,b'\0\0'+bytes([code])+b'\0')
    u.mem_write(0x20073b88,bytes([active]));u.mem_write(0x20000694,struct.pack('<I',0x20030000)*256)
    u.mem_write(0x20030008,struct.pack('<I',0x500001))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R1,0x20010000)
    events=[]
    def hook(uc,a,size,_):
     if a==0x500000:
      events.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_handler_4d2a5c'] if is_c else 0x4d2a5c)|1,0x600000,count=500)
    pair.append(events)
   assert pair[0]==pair[1],(code,active,pair)
   cases+=1
 print('PASS_BLE_DM_HCI_CALLBACK_NATIVE',cases)
