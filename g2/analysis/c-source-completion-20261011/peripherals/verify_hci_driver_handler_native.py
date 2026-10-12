#!/usr/bin/env python3
"""Bounded stock/C HciDrvHandler control and RAM effects at child ABI cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_handler.c'
names=['audio_ble_hci_read_buf_size_cmd_52b620','WsfTimerStartMs','WsfTimerStop','audio_ble_hci_serial_rx_incoming_530186','audio_ble_wsf_set_event','audio_ble_radio_exchange_receive_52e1ea','audio_ble_radio_exchange_begin_52e0d2','audio_ble_hci_ring_consume_5300e2','audio_ble_hci_error_check_4b47ae','audio_ble_hci_boot_delay_491102','audio_ble_hci_driver_radio_shutdown','audio_ble_hci_driver_radio_boot','audio_ble_hci_driver_empty_queue_4b4d18','audio_ble_dm_device_reset']
native=[0x52b620,0x52a4c4,0x52a4d2,0x530186,0x52b91e,0x52e1ea,0x52e0d2,0x5300e2,0x4b47ae,0x491102,0x4b49ce,0x4b48a6,0x4b4d18,0x4b3026]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_ble_hci_read_buf_size_cmd_52b620(void){}
void WsfTimerStartMs(void*a,uint32_t b){(void)a;(void)b;}
void WsfTimerStop(void*a){(void)a;}
uint32_t audio_ble_hci_serial_rx_incoming_530186(void*a,uint16_t b){(void)a;(void)b;return 0;}
void audio_ble_wsf_set_event(uint32_t a,uint32_t b){(void)a;(void)b;}
int32_t audio_ble_radio_exchange_receive_52e1ea(void*a,void*b,uint32_t*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_ble_radio_exchange_begin_52e0d2(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_ble_hci_ring_consume_5300e2(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void audio_ble_hci_error_check_4b47ae(uint32_t a){(void)a;}
void audio_ble_hci_boot_delay_491102(uint32_t a){(void)a;}
void audio_ble_hci_driver_radio_shutdown(void){}
void audio_ble_hci_driver_radio_boot(uint8_t a){(void)a;}
void audio_ble_hci_driver_empty_queue_4b4d18(void){}
void audio_ble_dm_device_reset(void){}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_handler_4b4ab2',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('event2','idle','partial','complete','ready_error','queue_send'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_write(0x20010000,b'\0\0'+(b'\2' if mode=='event2' else b'\0')+b'\0')
   u.mem_write(0x20074638,struct.pack('<II',8 if mode in ('partial','complete') else 0,0))
   u.mem_write(0x20000dac,struct.pack('<I',0x20020000));u.mem_write(0x20073ba8,b'\0'*32)
   if mode=='ready_error':
    u.mem_write(0x40010410,struct.pack('<I',0x00200000));u.mem_write(0x20074640,struct.pack('<I',0x55667788))
   if mode=='queue_send':
    u.mem_write(0x20073bb0,struct.pack('<I',1));u.mem_write(0x20073bbc,struct.pack('<I',0x20030000));u.mem_write(0x20030000,struct.pack('<I',4)+b'\x01\x02\x03\x04')
   u.mem_write(0x20074fcb,b'\x17');u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R1,0x20010000);u.reg_write(UC_ARM_REG_R3,0x12345678)
   mapping=dict(zip((sym[n]&~1 for n in names) if is_c else native,range(len(names))));events=[]
   def hook(uc,a,size,_):
    idx=mapping.get(a)
    if idx is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    events.append((idx,r1 if idx in (1,3,4) else 0))
    if idx==7:uc.mem_write(0x20073bb0,struct.pack('<I',0))
    ret=(4 if mode=='partial' else 8) if idx==3 else 1 if idx==5 and mode=='ready_error' else 0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_handler_4b4ab2'] if is_c else 0x4b4ab2)|1,0x600000,count=5000)
   pair.append((u.reg_read(UC_ARM_REG_R0),events,bytes(u.mem_read(0x20074638,8))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_HCI_DRIVER_HANDLER_NATIVE',cases)
