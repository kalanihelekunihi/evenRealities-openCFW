"""Actual compiled ARM C/native radio detect/revision/enable effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_simple.c'
SHIM='''#include <stdint.h>
volatile uint32_t audio_ble_hci_radio_revision_word_20074224;
volatile uint32_t audio_ble_hci_radio_detect_word_20074228;
const uint8_t audio_ble_hci_radio_detect_log_768ac8[]={0};
void audio_ble_hci_boot_log_4733ee(const void*p,...){(void)p;}
void audio_ble_hci_radio_pin_mask_4810b0(uint32_t a,uint32_t b,uint32_t*p){(void)a;(void)b;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_detect_52deee',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 funcs={'detect':(0x52deee,'audio_ble_hci_radio_detect_52deee'),'revision':(0x52dee6,'audio_ble_hci_radio_revision_52dee6'),'enable':(0x52dd58,'audio_ble_hci_radio_enable_52dd58')}
 for label,fn,value in [('detect_yes','detect',0x0301ff04),('detect_no','detect',0x77777777),('revision','revision',0x12345678),('enable','enable',0)]:
  out=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   revision=syms['audio_ble_hci_radio_revision_word_20074224'] if is_c else 0x20074224
   detect=syms['audio_ble_hci_radio_detect_word_20074228'] if is_c else 0x20074228
   u.mem_write(revision,struct.pack('<I',value));u.mem_write(detect,struct.pack('<I',value))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={0x4733ee:'log',0x4810b0:'pin'} if not is_c else {syms['audio_ble_hci_boot_log_4733ee']&~1:'log',syms['audio_ble_hci_radio_pin_mask_4810b0']&~1:'pin'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a]
    if name=='pin':
     calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_R2),4))[0]))
     uc.mem_write(uc.reg_read(UC_ARM_REG_R2),struct.pack('<I',0xabc))
    else:calls.append((name,uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[funcs[fn][1]] if is_c else funcs[fn][0])|1,0x600000,count=120)
   out.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert out[0]==out[1],(label,out)
  print('PASS',label,out[0])
