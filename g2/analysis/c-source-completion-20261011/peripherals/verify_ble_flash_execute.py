"""Compiled-C/native resident flash shim with callback and MMIO ordering."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_flash_execute',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_flash_execute.c'),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 observations=[]
 for compiled in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40014000,0x1000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(0x75d634,struct.pack('<I',0x700101))
  events=[]
  def callback(uc,a,size,_):
   if a==0x700100:
    sp=uc.reg_read(UC_ARM_REG_SP)
    events.append(('callback',tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)),struct.unpack('<I',uc.mem_read(sp,4))[0]))
    uc.reg_write(UC_ARM_REG_R0,0x5a)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,a,size,value,_):
   if a in (0x40014008,0x40014024):events.append(('write',a,value))
  u.hook_add(UC_HOOK_CODE,callback);u.hook_add(UC_HOOK_MEM_WRITE,write)
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x12344321,1,0x20081000,0xff000)):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<I',32));u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['audio_ble_flash_execute'] if compiled else 0x541b7c)|1,0x600000,count=100)
  observations.append((u.reg_read(UC_ARM_REG_R0),events))
 assert observations[0]==observations[1],observations
 print('PASS resident flash execute callback/MMIO')
