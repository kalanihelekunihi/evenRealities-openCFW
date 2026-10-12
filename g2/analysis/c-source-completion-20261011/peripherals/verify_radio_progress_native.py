#!/usr/bin/env python3
"""Native/C update percentage arithmetic and logging ABI."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_progress.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('void audio_ble_hci_boot_log_4733ee(const char *x,...){(void)x;}')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_progress_52eba8',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for processed,total in ((0,10),(1,10),(3,10),(4,40),(1,3),(7,13),(250,1000),(0xffffffff,0x1000)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,processed);u.reg_write(UC_ARM_REG_R1,total)
   log=(sym['audio_ble_hci_boot_log_4733ee']&~1) if is_c else 0x4733ee;events=[]
   def hook(uc,a,size,_):
    if a==log:
     r0=uc.reg_read(UC_ARM_REG_R0);events.append((bytes(uc.mem_read(r0,40)).split(b'\0',1)[0],uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_progress_52eba8'] if is_c else 0x52eba8)|1,0x600000,count=1000)
   pair.append(events)
  assert pair[0]==pair[1],(processed,total,pair)
  count+=1
 print('PASS_RADIO_PROGRESS_NATIVE',count)
