#!/usr/bin/env python3
"""Original/C serial receive FSM and allocation effects for bounded packets."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_serial_rx_incoming.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_ble_hci_msg_data_alloc(uint16_t a,uint8_t b){(void)a;(void)b;return 0;}
void *audio_wsf_msg_alloc(uint16_t a){(void)a;return 0;}
void audio_wsf_msg_enqueue(void*a,uint8_t b,void*c){(void)a;(void)b;(void)c;}
void audio_ble_wsf_set_event(uint32_t a,uint32_t b){(void)a;(void)b;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_serial_rx_incoming_530186',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for payload in (b'',b'\x99',b'\x04',b'\x04\x0e\x01',b'\x04\x0e\x01\xaa',b'\x02\x01\x00\x02\x00\xaa\xbb',b'\x02\x01\x00\x00\x00'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_write(0x20010000,payload.ljust(16,b'\0'));u.mem_write(0x200714f4,struct.pack('<H',100));u.mem_write(0x2007464c,b'\0'*12);u.mem_write(0x20074f30,b'\0'*4);u.mem_write(0x20074fcd,b'\0'*3)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20010000);u.reg_write(UC_ARM_REG_R1,len(payload))
   mapping=({sym['audio_ble_hci_msg_data_alloc']&~1:'data',sym['audio_wsf_msg_alloc']&~1:'msg',sym['audio_wsf_msg_enqueue']&~1:'core'} if is_c else {0x4bf990:'data',0x4bf99e:'msg',0x530c88:'core'})
   events=[]
   def hook(uc,a,size,_):
    k=mapping.get(a)
    if k is None:return
    events.append((k,(uc.reg_read(UC_ARM_REG_R1) if is_c else uc.reg_read(UC_ARM_REG_R0))&0xffff if k=='core' else uc.reg_read(UC_ARM_REG_R0)&0xffff))
    ret=0x20020000 if k=='data' else 0x20021000 if k=='msg' else 0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_hci_serial_rx_incoming_530186'] if is_c else 0x530186)|1,0x600000,count=5000)
   pair.append((u.reg_read(UC_ARM_REG_R0),events,bytes(u.mem_read(0x2007464c,12)),bytes(u.mem_read(0x20074f30,4)),bytes(u.mem_read(0x20074fcd,3)),bytes(u.mem_read(0x20020000,12)),bytes(u.mem_read(0x20021000,12))))
  assert pair[0]==pair[1],(payload,pair)
  cases+=1
 print('PASS_HCI_SERIAL_RX_NATIVE',cases)
