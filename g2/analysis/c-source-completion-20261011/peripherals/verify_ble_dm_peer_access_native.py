#!/usr/bin/env python3
"""Native/C DM peer record accessors over all 256 connection IDs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_peer_access.c'
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text('unsigned char audio_dm_connection_records[0x4000];\n');elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmConnPeerAddr',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('type','address'):
  for conn in range(256):
   values=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    base=sym['audio_dm_connection_records'] if is_c else 0x200712a4
    u.mem_write(base-0x30,bytes((i&0xff) for i in range(0x3300)))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,conn)
    entry=sym['DmConnPeerAddrType' if mode=='type' else 'DmConnPeerAddr'] if is_c else (0x4b6ed8 if mode=='type' else 0x4b6eea)
    u.emu_start(entry|1,0x600000,count=80)
    result=u.reg_read(UC_ARM_REG_R0)
    values.append(result if mode=='type' else result-base)
   assert values[0]==values[1],(mode,conn,values)
   cases+=1
 print('PASS_BLE_DM_PEER_ACCESS_NATIVE',cases)
