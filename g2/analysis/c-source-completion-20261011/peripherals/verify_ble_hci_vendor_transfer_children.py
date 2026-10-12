"""Actual ARM C/native vendor transfer guard and encoder fixtures."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_transfer_children.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_transfer_guard_55c1e0',str(S),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 def run(kind,inputs):
  values=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   sp=0x200ff000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   if kind=='guard':
    row=0x20001000;desc=0x20002000;u.mem_write(row,b'\x00'*0x900);u.mem_write(desc,b'\x00'*48)
    for k,v in inputs.items():
     if k=='state':u.mem_write(row+8,bytes([v]))
     elif k=='strict':pass
     else:W(u,desc+k,v)
    u.reg_write(UC_ARM_REG_R0,row);u.reg_write(UC_ARM_REG_R1,desc);u.reg_write(UC_ARM_REG_R2,inputs.get('strict',1))
    entry=syms['audio_ble_vendor_transfer_guard_55c1e0'] if is_c else 0x55c1e0
   else:
    for i,v in enumerate(inputs):
     if i<4:u.reg_write([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3][i],v)
     else:W(u,sp+(i-4)*4,v)
    entry=syms['audio_ble_vendor_transfer_encode_55bce8'] if is_c else 0x55bce8
   u.emu_start(entry|1,0x600000,count=400)
   values.append(u.reg_read(UC_ARM_REG_R0))
  assert values[0]==values[1],(kind,inputs,values)
  return values[0]
 cases=[{4:4,'state':1},{4:6,'state':1},{4:4,16:2,20:2,24:0x20004000,28:0x20005000,'state':1},{4:4,8:0x100,16:2,20:2,24:0x20004000,28:0x20005000,'state':1},{4:4,16:0x1000,'state':1},{4:4,16:2,20:2,24:0x20004000,28:0,'state':1},{4:4,16:2,20:1,24:0,28:0x20005000,'state':1},{4:4,16:0,0:5,'state':0},{4:4,16:0,'state':0,'strict':0,36:0xe0},{4:4,16:0,'state':0,'strict':0,40:0xe0e0e0}]
 for c in cases:print('PASS guard',c,run('guard',c))
 for i in range(24):
  a=[i&7,i%3,(i>>1)&1,0,i*3,0,i&7,i*17]
  print('PASS encode',i,hex(run('encode',a)))
