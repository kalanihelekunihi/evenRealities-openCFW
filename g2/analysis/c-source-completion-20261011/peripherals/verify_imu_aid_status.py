"""Actual native/C IMU AID byte-load cases."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('volatile unsigned char g2_imu_aid_enabled_cell;\n')
 elf=Path(td)/'aid.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,semantic_get_aid_enabled',str(ROOT/'components/audio/uart_thread_source_candidate/imu_aid_status.c'),str(shim),'-o',str(elf)],check=True)
 symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for value in [0,1,2,127,255]:
  results=[]
  for candidate in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000)
   for address,data in segments:u.mem_write(address,data)
   u.mem_map(0x20000000,0x100000)
   u.mem_write(0x20074fd8,bytes([value]))
   u.mem_write(symbols['g2_imu_aid_enabled_cell'],bytes([value]))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((symbols['semantic_get_aid_enabled'] if candidate else 0x4a4822)|1,0x600000,count=100)
   results.append(u.reg_read(UC_ARM_REG_R0))
  assert results[0]==results[1]==value,(value,results)
  print('PASS IMU AID byte',value)
