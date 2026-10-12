#!/usr/bin/env python3
"""Bounded original/C ring read-consume effects, privileged ARM mode."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_handler_children.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_wsf_msg_alloc(uint16_t a){(void)a;return 0;}
void audio_ble_hci_cmd_send(void*a){(void)a;}
void audio_ble_wsf_timer_insert(void*a,uint32_t b){(void)a;(void)b;}
void audio_ble_hci_radio_scheduler_53006c(void*a,const void*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
void audio_delay_us(uint32_t a){(void)a;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_ring_consume_5300e2',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for available,count,output in ((0,1,False),(1,1,False),(2,1,True),(4,3,True),(8,4,True)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   ring=bytearray(32)
   for offset,value in ((4,2),(8,available),(12,8),(16,2),(20,0x20020000)):struct.pack_into('<I',ring,offset,value)
   u.mem_write(0x20010000,bytes(ring));u.mem_write(0x20020000,bytes(range(8)));u.mem_write(0x20030000,b'\xa5'*16)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20010000);u.reg_write(UC_ARM_REG_R1,0x20030000 if output else 0);u.reg_write(UC_ARM_REG_R2,count)
   u.emu_start((sym['audio_ble_hci_ring_consume_5300e2'] if is_c else 0x5300e2)|1,0x600000,count=3000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20010000,32)),bytes(u.mem_read(0x20030000,16))))
  assert pair[0]==pair[1],(available,count,output,pair)
  cases+=1
 print('PASS_HCI_RING_CONSUME_NATIVE',cases)
