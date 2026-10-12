#!/usr/bin/env python3
"""Bounded original/C image-record pointer and error effects, logging disabled."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_record_data.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_record_data_52f99e',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for addresses in ((),(0,),(0x300000,),(0x300400,),(0x302000,),(0x302400,),(0x123456,),(0x300000,0x300400,0x302000,0x302400)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   records=b''.join(struct.pack('<IIII',0x10*i,0x20+i,a,0) for i,a in enumerate(addresses))
   u.mem_write(0x200731f0,records.ljust(64,b'\0'));u.mem_write(0x2007348c,b'\xa5'*48)
   u.mem_write(0x20074958,b'\xa5'*16)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20010000);u.reg_write(UC_ARM_REG_R1,len(addresses))
   try:u.emu_start((sym['audio_ble_radio_record_data_52f99e'] if is_c else 0x52f99e)|1,0x600000,count=5000)
   except Exception as ex:raise RuntimeError((addresses,is_c,hex(u.reg_read(UC_ARM_REG_PC)),ex)) from ex
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200731f0,64)),bytes(u.mem_read(0x2007348c,48)),bytes(u.mem_read(0x20074958,16))))
  assert pair[0]==pair[1],(addresses,pair)
  cases+=1
 print('PASS_RADIO_RECORD_DATA_NATIVE',cases)
