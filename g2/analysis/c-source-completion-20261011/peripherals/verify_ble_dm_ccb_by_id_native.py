#!/usr/bin/env python3
"""Actual C/native DM connection row lookup on valid connection IDs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_ccb_by_id.c'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text('unsigned char audio_dm_connection_records[0x3000];\n');elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,dmConnCcbById',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for conn in (1,2,5):
  for live in (0,1):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    base=sy['audio_dm_connection_records'] if compiled else 0x200712a4
    u.mem_write(base+(conn-1)*0x30+0x16,bytes([live]))
    u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['dmConnCcbById'] if compiled else 0x4b62a8)|1,0x600000,count=300)
    value=u.reg_read(UC_ARM_REG_R0)
    pair.append(value-base if value else None)
   assert pair[0]==pair[1],(conn,live,pair)
print('PASS_BLE_DM_CCB_BY_ID_NATIVE 6')
