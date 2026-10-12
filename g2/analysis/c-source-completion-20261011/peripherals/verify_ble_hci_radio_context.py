"""Actual ARM C/native radio platform, context, dispatch effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_context.c'
SHIM='''#include <stdint.h>
volatile uint32_t audio_ble_hci_radio_platform_pin_200001b0;
volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f51;
uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
int32_t g2_gpio_hal_write(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
void audio_ble_hci_radio_stack_stop_55c430(uint32_t a){(void)a;}
int32_t audio_ble_radio_stack_option_55c7e8(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_platform_init_52dc40',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 funcs={'platform':(0x52dc40,'audio_ble_radio_platform_init_52dc40'),'context':(0x52e0a2,'audio_ble_radio_context_init_52e0a2'),'dispatch':(0x52edd8,'audio_ble_radio_dispatch_set_52edd8')}
 for label,fn,active,pending in [('platform','platform',0,0),('invalid','context',0,0),('no_pending','context',1,0),('stop','context',1,1),('dispatch','dispatch',0,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   pin=syms['audio_ble_hci_radio_platform_pin_200001b0'] if is_c else 0x200001b0
   dispatch=syms['audio_ble_hci_radio_dispatch_cell_20074f51'] if is_c else 0x20074f51
   u.mem_write(pin,struct.pack('<I',0x333));u.mem_write(dispatch,b'\x00')
   record=0x20006000;u.mem_write(record,struct.pack('<II',0,0x12345678)+bytes([active,pending])+bytes(10))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,record if fn=='context' else 0x55);u.reg_write(UC_ARM_REG_R3,0x87654321)
   native={'pin':0x480f0c,'gpio':0x480fd6,'stop':0x55c430,'option':0x55c7e8};compiled={'pin':syms['g2_codec_pin_function']&~1,'gpio':syms['g2_gpio_hal_write']&~1,'stop':syms['audio_ble_hci_radio_stack_stop_55c430']&~1,'option':syms['audio_ble_radio_stack_option_55c7e8']&~1}
   cuts={v:k for k,v in (compiled if is_c else native).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name in ('pin','gpio','option') else 0,uc.reg_read(UC_ARM_REG_R2) if name=='option' else 0))
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[funcs[fn][1]] if is_c else funcs[fn][0])|1,0x600000,count=300)
   rows.append((u.reg_read(UC_ARM_REG_R0) if fn!='dispatch' else None,calls,bytes(u.mem_read(record,10)),bytes(u.mem_read(dispatch,1))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][:2])
