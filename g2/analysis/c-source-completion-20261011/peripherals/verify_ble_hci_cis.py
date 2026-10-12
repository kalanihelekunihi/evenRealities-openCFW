"""Actual compiled ARM C/native six-slot CIS allocation/lookup/free effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_cis.c'
SHIM='#include <stdint.h>\nuint8_t audio_ble_hci_controller_state_20071478[0xb0];\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_cis_alloc',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 fun={'alloc':(0x52ad9c,'audio_ble_hci_cis_alloc'),'free':(0x52adc2,'audio_ble_hci_cis_free'),'lookup':(0x52adec,'audio_ble_hci_cis_by_handle'),'open':(0x52ae24,'audio_ble_hci_cis_open'),'close':(0x52ae2e,'audio_ble_hci_cis_close')}
 for label,fn,rows in [('alloc_first','alloc',[0xffff]*6),('alloc_full','alloc',[1,2,3,4,5,6]),('free_middle','free',[1,2,0x1234,4,5,6]),('lookup_found','lookup',[1,2,0x1234,4,5,6]),('lookup_missing','lookup',[1,2,3,4,5,6]),('open','open',[0xffff]*6),('close','close',[1,2,0x1234,4,5,6])]:
  out=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   u.mem_write(state,b'\x00'*0xb0);u.mem_write(state+0x54,struct.pack('<6H',*rows))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R7,0x12345678);u.reg_write(UC_ARM_REG_R0,0x1234)
   u.emu_start((syms[fun[fn][1]] if is_c else fun[fn][0])|1,0x600000,count=150)
   value=u.reg_read(UC_ARM_REG_R0)
   if fn=='lookup':value=(value-state)&0xffffffff if value else 0
   out.append((value if fn in ('lookup','open','close') else None,bytes(u.mem_read(state+0x54,12))))
  assert out[0]==out[1],(label,out)
  print('PASS',label,out[0][0])
