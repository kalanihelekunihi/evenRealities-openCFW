"""Actual compiled-C/native HCI driver handler state comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('unsigned char audio_ble_hci_driver_handler_id; unsigned char audio_ble_hci_driver_rows[0x20];')
 elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_driver_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_handler.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for val in (0,1,0x81,0xff):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   idaddr=syms['audio_ble_hci_driver_handler_id'] if compiled else 0x20074fcb
   rows=syms['audio_ble_hci_driver_rows'] if compiled else 0x20073e64
   u.mem_write(idaddr,b'\xaa');u.mem_write(rows,b'\xaa'*0x20)
   u.reg_write(UC_ARM_REG_R0,val);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_hci_driver_handler_init'] if compiled else 0x4b4a7c)|1,0x600000,count=500)
   obs.append((u.mem_read(idaddr,1),u.mem_read(rows,0x20)))
  assert obs[0]==obs[1],(val,obs)
  print('PASS HCI handler',val)
