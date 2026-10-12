#!/usr/bin/env python3
"""Actual stock/C current-image and post-write CRC decision trees."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_crc.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_ble_radio_image_rows_52e788(uint32_t *a,uint32_t *b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_ble_radio_crc_remote_52e6ac(void *a,uint32_t b,uint32_t c,uint32_t *d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_ble_radio_crc_local_4d34f8(const void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void audio_ble_hci_boot_log_4733ee(const char *a,...){(void)a;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_update_current_52e7c0',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for name,stock in [('audio_ble_radio_update_current_52e7c0',0x52e7c0),('audio_ble_radio_update_check_52ec84',0x52ec84)]:
  for rows,remote_status,actual,expected in ((0,0,0,0),(1,7,0,0),(1,0,0x1234,0x5678),(1,0,0x1234,0x1234)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x2007b000,(0x2007b100).to_bytes(4,'little'))
    for off,val in ((0,0x2007c000),(4,0x123),(8,0x402000)):u.mem_write(0x2007b100+off,val.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20070000)
    maps={0x52e788:'rows',0x52e6ac:'remote',0x4d34f8:'local',0x4733ee:'log'} if not is_c else {sym[n]&~1:k for n,k in [('audio_ble_radio_image_rows_52e788','rows'),('audio_ble_radio_crc_remote_52e6ac','remote'),('audio_ble_radio_crc_local_4d34f8','local'),('audio_ble_hci_boot_log_4733ee','log')]}
    events=[]
    def hook(uc,a,size,_):
     kind=maps.get(a)
     if kind is None:return
     r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     if kind=='rows':uc.mem_write(r0,rows.to_bytes(4,'little'));uc.mem_write(r1,(0x2007b000).to_bytes(4,'little'));ret=0
     elif kind=='remote':events.append((kind,r0,r1,r2));uc.mem_write(r3,actual.to_bytes(4,'little'));ret=remote_status
     elif kind=='local':events.append((kind,r0,r1,r2));ret=expected
     else:
      msg=bytes(uc.mem_read(r0,128)).split(b'\0',1)[0]
      events.append((kind,msg,(r1,r2,r3)[:min(msg.count(b'%'),3)]));ret=0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=1500)
    pair.append((events,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(name,rows,remote_status,actual,expected,pair)
   count+=1
 print('PASS_RADIO_UPDATE_CRC_NATIVE',count)
