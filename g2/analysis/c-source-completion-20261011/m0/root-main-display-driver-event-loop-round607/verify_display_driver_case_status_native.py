#!/usr/bin/env python3
"""Compare Apollo in-box status across override and both native status bytes."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR
source=Path(__file__).with_name('display_driver_case_status.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 image=Path(d)/'case.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for override,left,right in itertools.product((0,1,2),repeat=3):
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   state=syms['display_driver_case_state_cells'] if compiled else 0x20074188
   cell=syms['display_driver_case_override_cell'] if compiled else 0x20075012
   cpu.mem_write(state+6,bytes([left,right]))
   cpu.mem_write(cell,bytes([override]))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   start=syms['audio_uart_case_status'] if compiled else 0x4acad0
   cpu.emu_start(start|1,0x600000,count=80)
   observations.append(cpu.reg_read(UC_ARM_REG_R0))
  assert observations[0]==observations[1],(override,left,right,observations)
  count+=1
print('PASS_DISPLAY_DRIVER_CASE_STATUS_NATIVE',count)
