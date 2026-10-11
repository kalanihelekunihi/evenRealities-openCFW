"""Actual compiled-C/native WSF handler registration state."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('#include <stdint.h>\nuint8_t audio_wsf_task_state[64];\n')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfOsSetNextHandler',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_handler_register.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for index in [0,1,7,14,15]:
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);state=syms['audio_wsf_task_state'] if c else 0x20073230
   u.mem_write(state,b'\0'*64);u.mem_write(state+0x3d,bytes([index]));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x536815)
   u.emu_start((syms['WsfOsSetNextHandler'] if c else 0x52b980)|1,0x600000,count=1000)
   out.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(state,64))))
  assert out[0]==out[1],(index,out)
  print('PASS WSF handler',index)
