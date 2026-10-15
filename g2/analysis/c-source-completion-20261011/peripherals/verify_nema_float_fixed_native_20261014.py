#!/usr/bin/env python3
"""Compare finite Nema float to signed 16.16 conversion with native."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_S0,UC_ARM_REG_SP,UC_ARM_REG_LR
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_fixed.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
F=lambda x:int.from_bytes(struct.pack('<f',x),'little')
with tempfile.TemporaryDirectory() as temp:
 image=Path(temp)/'fixed.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 values=[F(v) for v in (-1000.,-64.,-3.5,-2.,-1.5,-1.,-0.5,-0.00001,0.,0.00001,0.5,1.,1.5,2.,3.5,64.,1000.,32767.)]
 values += [F((i-128)/37.0) for i in range(256)]
 for bits in values:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cpu.reg_write(UC_ARM_REG_S0,bits);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.emu_start((syms['audio_uart_nema_float_fixed_5242cc'] if compiled else 0x5242cc)|1,0x600000,count=40)
   observations.append(cpu.reg_read(UC_ARM_REG_R0))
  assert observations[0]==observations[1],(hex(bits),observations)
 print('PASS_NEMA_FLOAT_FIXED_NATIVE',len(values))
