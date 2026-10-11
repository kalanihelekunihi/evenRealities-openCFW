"""Actual ARM C/native Cordio OTA route-message allocation and layout check."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_ota_route_message.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ota_route_context[16];
void *audio_wsf_msg_alloc(){return 0;}
void audio_wsf_msg_send(){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_connection_route',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for allocated in (False,True):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cell=(syms['audio_ble_ota_route_context']&~1) if compiled else 0x20073b78
   u.mem_write(cell+12,b'\x09')
   u.mem_write(0x20001000,b'X'*36)
   for r,v in [(UC_ARM_REG_R0,3),(UC_ARM_REG_R1,7),(UC_ARM_REG_R2,0x13),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(r,v)
   cuts={(syms['audio_wsf_msg_alloc']&~1 if compiled else 0x4bf99e):'alloc',
         (syms['audio_wsf_msg_send']&~1 if compiled else 0x4bf9ba):'send'};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a]
    calls.append((k,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(0x20001000,6)) if k=='send' else None))
    uc.reg_write(UC_ARM_REG_R0,0x20001000 if allocated and k=='alloc' else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_ota_connection_route'] if compiled else 0x4b6c82)|1,0x600000,count=300)
   rows.append(calls)
  assert rows[0]==rows[1],(allocated,rows)
  print('PASS',allocated,rows[0])
