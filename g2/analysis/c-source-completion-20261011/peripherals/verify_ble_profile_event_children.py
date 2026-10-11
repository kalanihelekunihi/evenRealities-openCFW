"""Actual ARM C/native OTA route, ATT write wrapper and device MMIO checks."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_profile_event_children.c'
SHIM='void audio_ble_ota_connection_route(){}\nvoid audio_ble_att_write_request(){}\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_profile_write_event',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,arg in (('route',5),('write',7),('reset',2),('reset',0),('reset',1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_R1,0x824);u.reg_write(UC_ARM_REG_R2,0x1122);u.reg_write(UC_ARM_REG_R3,0x33445566)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   entry=(syms['audio_ble_ota_connection_changed'] if kind=='route' else syms['audio_ble_profile_write_event'] if kind=='write' else syms['audio_ble_ota_reset_event']) if compiled else (0x4bb04a if kind=='route' else 0x533ed8 if kind=='write' else 0x4d3534)
   child=(syms['audio_ble_ota_connection_route']&~1 if kind=='route' else syms['audio_ble_att_write_request']&~1) if compiled else (0x4b6c82 if kind=='route' else 0x533c6c)
   calls=[];writes=[]
   def hook(uc,a,size,_):
    if kind=='reset' or a!=child:return
    sp=uc.reg_read(UC_ARM_REG_SP)
    calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))+
                 tuple(struct.unpack('<I',uc.mem_read(sp+4*i,4))[0] for i in range(3) if kind=='write'))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def write(uc,access,a,size,value,_):
    if 0x40000000<=a<0x40001000:writes.append((a,size,value))
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
   u.emu_start(entry|1,0x600000,count=100 if kind=='reset' else 300)
   rows.append((calls,writes,u.reg_read(UC_ARM_REG_R0) if kind=='reset' and arg==2 else None))
  assert rows[0]==rows[1],(kind,arg,rows)
  print('PASS',kind,arg,rows[0])
