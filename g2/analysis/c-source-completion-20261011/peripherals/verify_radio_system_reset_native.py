#!/usr/bin/env python3
"""Native/C AIRCR reset write before the architectural reset boundary."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_reset.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_system_reset_44ab24',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for name,stock in [('audio_ble_system_reset_44ab24',0x44ab24),('audio_ble_radio_ready_44b0ae',0x44b0ae)]:
  for seed in (0,0xffffffff,0x12345678):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x1000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0xe000ed0c,seed.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    events=[]
    def reading(uc,access,a,size,value,_):
     if a==0xe000ed0c:events.append(('read',int.from_bytes(uc.mem_read(a,size),'little')))
    def written(uc,access,a,size,value,_):
     if a==0xe000ed0c:events.append(('write',value));uc.emu_stop()
    u.hook_add(UC_HOOK_MEM_READ,reading);u.hook_add(UC_HOOK_MEM_WRITE,written)
    u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=1000)
    pair.append(events)
   assert pair[0]==pair[1],(name,seed,pair)
   count+=1
 print('PASS_RADIO_SYSTEM_RESET_NATIVE',count)
