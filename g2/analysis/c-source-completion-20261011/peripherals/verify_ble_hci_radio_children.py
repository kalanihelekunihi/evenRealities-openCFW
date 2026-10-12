"""Bounded actual ARM C/native comparison of 0x52df12 radio context reset."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_children.c'
SHIM='''#include <stdint.h>
volatile uint32_t audio_ble_hci_radio_pin_mode;
uint32_t audio_ble_hci_radio_pin_mask_4810b0(uint32_t a,uint32_t b,uint32_t *p){(void)a;(void)b;(void)p;return 0;}
int32_t g2_gpio_hal_write(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
void audio_ble_hci_radio_mask_4c2e30(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_ble_hci_radio_stack_stop_55c430(uint32_t a){(void)a;}
void audio_ble_hci_radio_stack_option_55c7e8(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ble_hci_radio_stack_reset_55c286(uint32_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_reset_52df12',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={0x4c2e30:'mask',0x55c430:'stop',0x55c7e8:'option',0x55c286:'reset'}
 compiled={syms['audio_ble_hci_radio_'+n+'_x']:'?' for n in ()}
 compiled={syms['audio_ble_hci_radio_mask_4c2e30']&~1:'mask',syms['audio_ble_hci_radio_stack_stop_55c430']&~1:'stop',syms['audio_ble_hci_radio_stack_option_55c7e8']&~1:'option',syms['audio_ble_hci_radio_stack_reset_55c286']&~1:'reset'}
 for selector,flag in ((0,0),(4,1),(8,255),(9,1),(0xffffffff,1)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   base=0x20005000;initial=bytearray(16);struct.pack_into('<II',initial,0,selector,0x20006000);initial[8]=0x77;initial[9]=flag;u.mem_write(base,bytes(initial))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,base)
   calls=[];cuts=compiled if is_c else native
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name in ('mask','option') else 0,uc.reg_read(UC_ARM_REG_R2) if name=='option' else 0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_radio_reset_52df12'] if is_c else 0x52df12)|1,0x600000,count=300)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(base,16))))
  assert results[0]==results[1],(selector,flag,results)
  print('PASS',selector,flag,results[0][0],len(results[0][1]))
 for replacement in (0x75,0x39):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   calls=[];child=(syms['audio_ble_hci_radio_pin_mask_4810b0']&~1) if is_c else 0x4810b0
   def hook(uc,a,size,_):
    if a!=child:return
    ptr=uc.reg_read(UC_ARM_REG_R2);calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),struct.unpack('<I',uc.mem_read(ptr,4))[0]));uc.mem_write(ptr,struct.pack('<I',replacement));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_radio_disable_52dd6a'] if is_c else 0x52dd6a)|1,0x600000,count=100)
   results.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert results[0]==results[1],(replacement,results)
  print('PASS disable',replacement,results[0])
