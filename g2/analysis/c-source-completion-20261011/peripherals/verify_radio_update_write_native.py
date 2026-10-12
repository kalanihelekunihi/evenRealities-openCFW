#!/usr/bin/env python3
"""Native/C chunked image-row write calls and error exits."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_write.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_ble_radio_image_rows_52e788(uint32_t *a,uint32_t *b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_ble_radio_write_command_52eaf8(void *a,uint32_t b,const void *c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_ble_radio_progress_52eba8(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_ble_hci_boot_log_4733ee(const char *a,...){(void)a;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_update_write_52ebca',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for length in (0,1,248,249,500):
  for fail_at in (0,2):
   for total in (0,1000):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segments:u.mem_write(a,d)
     u.mem_write(0x2007b000,(0x2007b100).to_bytes(4,'little'))
     for off,val in ((0,0x2007c000),(4,length),(8,0x402000)):u.mem_write(0x2007b100+off,val.to_bytes(4,'little'))
     u.mem_write(0x2007c000,bytes((i*3+1)&255 for i in range(500)))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,0x20070000);u.reg_write(UC_ARM_REG_R1,total)
     mapping={0x52e788:'rows',0x52eaf8:'write',0x52eba8:'progress',0x4733ee:'log'} if not is_c else {sym[n]&~1:k for n,k in [('audio_ble_radio_image_rows_52e788','rows'),('audio_ble_radio_write_command_52eaf8','write'),('audio_ble_radio_progress_52eba8','progress'),('audio_ble_hci_boot_log_4733ee','log')]}
     events=[];writes=[]
     def hook(uc,a,size,_):
      kind=mapping.get(a)
      if kind is None:return
      r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
      if kind=='rows':uc.mem_write(r0,(1).to_bytes(4,'little'));uc.mem_write(r1,(0x2007b000).to_bytes(4,'little'));ret=0
      elif kind=='write':
       events.append((kind,r0,r1,r2,r3,bytes(uc.mem_read(r2,r3))));writes.append(True)
       ret=7 if fail_at and len(writes)==fail_at else 0
      elif kind=='progress':events.append((kind,r0,r1));ret=0
      else:events.append((kind,bytes(uc.mem_read(r0,64)).split(b'\0',1)[0]));ret=0
      uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['audio_ble_radio_update_write_52ebca'] if is_c else 0x52ebca)|1,0x600000,count=4000)
     pair.append((events,u.reg_read(UC_ARM_REG_R0)))
    assert pair[0]==pair[1],(length,fail_at,total,pair)
    count+=1
 print('PASS_RADIO_UPDATE_WRITE_NATIVE',count)
