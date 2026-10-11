"""Actual C/native profile handler layout and pointer writes."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_profile_handler_id;uint8_t audio_ble_profile_handler_entry_5fa056[1];
uint8_t audio_ble_profile_table_78f530[1]; const void *audio_ble_profile_dispatch_slot,*audio_ble_profile_table_slot;
uint32_t audio_ble_profile_runtime_rows[6];''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_profile_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_profile_handler_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for handler in (0,7,255):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   idx=syms['audio_ble_profile_handler_id'] if c else 0x20074f8a
   dispatch=syms['audio_ble_profile_dispatch_slot'] if c else 0x20074360
   table=syms['audio_ble_profile_table_slot'] if c else 0x20074364
   rows=syms['audio_ble_profile_runtime_rows'] if c else 0x20074310
   u.mem_write(idx,b'\xaa');u.mem_write(rows,b'\xaa'*24)
   u.reg_write(UC_ARM_REG_R0,handler);u.reg_write(UC_ARM_REG_R1,0x200727f0);u.reg_write(UC_ARM_REG_R2,0x200737b0)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_profile_handler_init'] if c else 0x535488)|1,0x600000,count=1000)
   rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
   ptrs=[rd(dispatch),rd(table)]
   if c:
    ptrs=[{syms['audio_ble_profile_handler_entry_5fa056']:0x5fa056,syms['audio_ble_profile_table_78f530']:0x78f530}.get(v,v) for v in ptrs]
   obs.append((u.mem_read(idx,1),ptrs,[rd(rows+i*4) for i in range(6)]))
  assert obs[0]==obs[1],(handler,obs)
  print('PASS BLE profile handler',handler)
