#!/usr/bin/env python3
"""Direct stock/C effects of configuration cell setters 0x52e5ce/f2."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_reconfigure_cells.c'
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_configure_52e5ce',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for name,stock,addresses in [('audio_ble_radio_configure_52e5ce',0x52e5ce,(0x2007422c,0x20074f50,0x20074230)),('audio_ble_radio_tune_52e5f2',0x52e5f2,(0x20074234,0x20074238))]:
  for ptr in (0,1,0x200036dc):
   for value in (0,1,0x12345678,0xffffffff):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segments:u.mem_write(a,d)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_R2,0xaabbccdd)
     u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=150)
     pair.append((u.reg_read(UC_ARM_REG_R0),tuple(bytes(u.mem_read(a,4)) for a in addresses)))
    assert pair[0]==pair[1],(name,ptr,value,pair)
    count+=1
 print('PASS_RADIO_RECONFIGURE_CELLS',count)
