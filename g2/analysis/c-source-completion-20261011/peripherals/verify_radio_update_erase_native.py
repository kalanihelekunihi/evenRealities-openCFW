#!/usr/bin/env python3
"""Stock/C erase command packet, log and response status."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_erase.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint64_t audio_ble_radio_exchange_52e612(void *x,const void *p,uint32_t n,void *r,uint32_t *z){(void)x;(void)p;(void)n;(void)r;(void)z;return 0;}
void audio_ble_hci_boot_log_4733ee(const char *x,...){(void)x;}
void __aeabi_memclr4(void *p,unsigned n){volatile unsigned char *q=p;for(unsigned i=0;i<n;i++)q[i]=0;}
void __aeabi_memclr(void *p,unsigned n){volatile unsigned char *q=p;for(unsigned i=0;i<n;i++)q[i]=0;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_update_erase_52e9b4',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for transport,controller in ((0,0),(4,0),(0,7)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20070000)
   exchange=(sym['audio_ble_radio_exchange_52e612']&~1) if is_c else 0x52e612
   log=(sym['audio_ble_hci_boot_log_4733ee']&~1) if is_c else 0x4733ee
   events=[]
   def hook(uc,a,size,_):
    if a==log:
     r0=uc.reg_read(UC_ARM_REG_R0);events.append(('log',bytes(uc.mem_read(r0,64)).split(b'\0',1)[0]));ret=0
    elif a==exchange:
     r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     events.append(('exchange',r0,r2,bytes(uc.mem_read(r1,r2))))
     uc.mem_write(r3,b'\0'*16);uc.mem_write(r3+6,bytes([controller]));ret=transport
    else:return
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_update_erase_52e9b4'] if is_c else 0x52e9b4)|1,0x600000,count=3000)
   pair.append((events,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(transport,controller,pair)
  count+=1
 print('PASS_RADIO_UPDATE_ERASE_NATIVE',count)
