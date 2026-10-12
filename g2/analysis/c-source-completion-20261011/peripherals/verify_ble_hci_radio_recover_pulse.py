"""Actual ARM C/native reset and pulse child call-sequence comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_recover_pulse.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nuint32_t g2_codec_pin_function(uint32_t a,uint32_t b){return 0;}\nint32_t g2_gpio_hal_write(uint32_t a,uint32_t b){return 0;}\nvoid audio_ble_hci_radio_reset_4910f4(uint32_t a){}\nvoid audio_ble_hci_boot_delay_491102(uint32_t a){}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_reset_52e8a4',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 pairs={'config':('g2_codec_pin_function',0x480f0c),'write':('g2_gpio_hal_write',0x480fd6),'ms':('audio_ble_hci_radio_reset_4910f4',0x4910f4),'us':('audio_ble_hci_boot_delay_491102',0x491102)}
 for kind,arg in [('reset',0),('pulse',0),('pulse',1),('pulse',2)]:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cuts={(syms[c]&~1) if is_c else n:k for k,(c,n) in pairs.items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];calls.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if k in ('config','write') else None))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,arg)
   entry=('audio_ble_hci_radio_reset_52e8a4',0x52e8a4) if kind=='reset' else ('audio_ble_radio_wait_pulse_52e854',0x52e854)
   u.emu_start((syms[entry[0]] if is_c else entry[1])|1,0x600000,count=20000)
   results.append(calls)
  assert results[0]==results[1],(kind,arg,results)
  print('PASS',kind,arg,len(results[0]),results[0][:5])
