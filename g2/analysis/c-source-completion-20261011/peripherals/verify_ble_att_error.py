"""Actual ARM C/native ATT error callback packet defined-byte comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_att_error.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\nuint8_t audio_ble_att_runtime[128];\n');elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_att_send_error',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for enabled in (False,True):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cell=(syms['audio_ble_att_runtime']&~1) if compiled else 0x200610ac
   u.mem_write(cell+0x58,struct.pack('<I',0x1f0001 if enabled else 0))
   for r,v in [(UC_ARM_REG_R0,7),(UC_ARM_REG_R1,0x824),(UC_ARM_REG_R2,0x71),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(r,v)
   calls=[]
   def hook(uc,a,size,_):
    if a!=0x1f0000:return
    p=uc.reg_read(UC_ARM_REG_R0);b=bytes(uc.mem_read(p,16))
    calls.append(tuple(b[i] for i in (0,1,2,3,8,9,10,11,12,14,15)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_att_send_error'] if compiled else 0x533934)|1,0x600000,count=500)
   rows.append(calls)
  assert rows[0]==rows[1],(enabled,rows)
  print('PASS',enabled,rows[0])
