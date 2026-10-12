#!/usr/bin/env python3
"""Actual C/native ATT hashable attribute classification and skip state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_hashable_attr.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,attsIsHashableAttr',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for uuid in (0x2800,0x2801,0x2802,0x2803,0x2900,0x2901,0x2903,0x2904,0x2905,0x1234):
  for wide in (0,1):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    attr,uuid_addr,length=0x20080000,0x20080100,0x20080200
    u.mem_write(attr,uuid_addr.to_bytes(4,'little'));u.mem_write(attr+8,length.to_bytes(4,'little'))
    u.mem_write(attr+0xe,bytes([wide]));u.mem_write(uuid_addr,uuid.to_bytes(2,'little'))
    u.mem_write(length,(3).to_bytes(2,'little'))
    flag=sy['audio_ble_atts_hash_skip_next'] if compiled else 0x20074f95
    u.mem_write(flag,b'\0')
    outputs=[]
    for index in range(2 if uuid==0x2803 else 1):
     u.reg_write(UC_ARM_REG_R0,attr);u.reg_write(UC_ARM_REG_SP,0x200ff000)
     u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((sy['attsIsHashableAttr'] if compiled else 0x534ea8)|1,0x600000,count=1000)
     outputs.append(u.reg_read(UC_ARM_REG_R0)&0xffff)
    pair.append((outputs,bytes(u.mem_read(flag,1))))
   assert pair[0]==pair[1],(uuid,wide,pair)
print('PASS_BLE_ATTS_HASHABLE_NATIVE 20')
