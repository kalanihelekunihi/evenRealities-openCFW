#!/usr/bin/env python3
"""Compare C locale descriptors and plural rules with authenticated Apollo data/code."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_context_registry.c'
data_addrs=(0x20001588,0x200017fc,0x20001a70,0x20001ce4,
            0x20001f58,0x200021cc,0x20002440,0x200026b4)
symbols=('en','de','es','fr','it','ja','zh_cn','zh_hk')
samples=(0,1,2,5,999999,1000000,2000000,0x7fffffff,0xffffffff,0xfffffffe,0x80000000)
with tempfile.TemporaryDirectory() as d:
 elf=Path(d)/'fixture.elf'
 aliases=['-Wl,--defsym,audio_uart_locale_data_'+name+'='+hex(address)
          for name,address in zip(symbols,data_addrs)]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_context',*aliases,str(src),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def engine():
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for address,data in segments:u.mem_write(address,data)
  return u
 u=engine();source_table=syms['audio_uart_display_context'];native_table=0x7560e4
 assert struct.unpack('<I',u.mem_read(source_table+32,4))[0]==0
 assert struct.unpack('<I',u.mem_read(native_table+32,4))[0]==0
 count=0
 for index in range(8):
  native_record=struct.unpack('<I',u.mem_read(native_table+4*index,4))[0]
  source_record=struct.unpack('<I',u.mem_read(source_table+4*index,4))[0]
  n=struct.unpack('<9I',u.mem_read(native_record,36))
  s=struct.unpack('<9I',u.mem_read(source_record,36))
  label=lambda address:bytes(u.mem_read(address,32)).split(b'\0')[0]
  assert label(n[0])==label(s[0]),(index,'locale')
  assert n[1:8]==s[1:8],(index,'data/reserved',n[1:8],s[1:8])
  for sample in samples:
   results=[]
   for callback in (n[8],s[8]):
    v=engine();v.reg_write(UC_ARM_REG_SP,0x200ff000)
    v.reg_write(UC_ARM_REG_LR,0x600001);v.reg_write(UC_ARM_REG_R0,sample)
    v.emu_start(callback|1,0x600000,count=10000)
    results.append(v.reg_read(UC_ARM_REG_R0))
   assert results[0]==results[1],(index,sample,results)
   count+=1
 print('PASS_DISPLAY_CONTEXT_REGISTRY_NATIVE',count)
