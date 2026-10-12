"""Actual ARM C/native radio ring command write bounded transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_write.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_radio_scheduler_state[32];volatile uint8_t audio_ble_hci_driver_handler_id;
void audio_ble_hci_error_check_4b47ae(uint32_t n){(void)n;}
uint32_t audio_ble_hci_ring_commit_530084(void *r,const void *p,uint32_t n){(void)r;(void)p;(void)n;return 0;}
void audio_ble_wsf_set_event(uint32_t h,uint32_t e){(void)h;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_driver_write',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,length,full in (('empty',0,False),('short',8,False),('max',0x102,False),('oversize',0x103,False),('full',8,True)):
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   ring=syms['audio_ble_hci_radio_scheduler_state'] if is_c else 0x20073ba8
   handler=syms['audio_ble_hci_driver_handler_id'] if is_c else 0x20074fcb
   u.mem_write(ring,b'\x00'*32);u.mem_write(ring+8,struct.pack('<IIII',0,0 if full else 0x820,0x104,0x20006500));u.mem_write(handler,b'\x03')
   input=0x20005000;u.mem_write(input,bytes(range(256))*2)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,input)
   native={0x4b47ae:'error',0x530084:'commit',0x52b91e:'event'}
   compiled={syms['audio_ble_hci_error_check_4b47ae']&~1:'error',syms['audio_ble_hci_ring_commit_530084']&~1:'commit',syms['audio_ble_wsf_set_event']&~1:'event'}
   cuts=compiled if is_c else native;calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,0 if name=='commit' else uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name=='event' else 0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_driver_write'] if is_c else 0x4b4a02)|1,0x600000,count=6000)
   rows.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20006500,min(length+5,0x108)))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0],rows[0][1])
