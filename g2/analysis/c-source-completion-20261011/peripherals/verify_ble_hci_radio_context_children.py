"""Actual ARM C/native context pin and reset-delay argument effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_context_children.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nuint32_t g2_codec_pin_function(uint32_t a,uint32_t b){return 0;}\nvoid audio_ble_vendor_yield_4807a0(uint32_t n){}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_context_setup_52e49a',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 for kind,value in [('setup',0),('setup',1),('setup',0x100),('reset',0),('reset',1),('reset',0xffffffff)]:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cuts={((syms['g2_codec_pin_function']&~1) if is_c else 0x480f0c):'pin',((syms['audio_ble_vendor_yield_4807a0']&~1) if is_c else 0x4807a0):'delay'};calls=[]
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if key=='pin' else 0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value)
   entry=(syms['audio_ble_radio_context_setup_52e49a'] if kind=='setup' else syms['audio_ble_hci_radio_reset_4910f4']) if is_c else (0x52e49a if kind=='setup' else 0x4910f4)
   u.emu_start(entry|1,0x600000,count=200)
   results.append(calls)
  assert results[0]==results[1],(kind,value,results)
  print('PASS',kind,value,results[0])
