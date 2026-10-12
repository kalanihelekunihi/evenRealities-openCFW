"""Actual compiled ARM C/native HCI radio scheduler/IRQ and prepare branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_scheduler.c'
SHIM='''#include <stdint.h>
uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t n){(void)n;return 0;}
void audio_ble_hci_radio_state_prepare_5118e0(void){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_scheduler_53006c',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 fun={'scheduler':(0x53006c,'audio_ble_hci_radio_scheduler_53006c'),'prepare':(0x52f38c,'audio_ble_hci_radio_prepare_52f38c'),'priority':(0x4b4786,'audio_ble_hci_radio_mux_on_4b4786'),'enable':(0x4b4768,'audio_ble_hci_radio_mux_request_4b4768')}
 for label,fn,arg,state_value in [('scheduler','scheduler',0,0),('prepare_no','prepare',0,0),('prepare_yes','prepare',0,1),('priority_pos','priority',0x3b,0),('priority_neg','priority',0xfffffffe,0),('enable_pos','enable',0x3b,0),('enable_neg','enable',0xfffffffe,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20006000,bytes(range(24)));u.mem_write(0x20005000,bytes([state_value]))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R7,0x12345678)
   u.reg_write(UC_ARM_REG_R0,0x20006000 if fn=='scheduler' else arg);u.reg_write(UC_ARM_REG_R1,0x20007000 if fn=='scheduler' else 4)
   u.reg_write(UC_ARM_REG_R2,0x104);u.reg_write(UC_ARM_REG_R3,0x820)
   cuts={0x50938e:'mode',0x5118e0:'state'} if not is_c else {syms['audio_ble_hci_radio_mode_state_50938e']&~1:'mode',syms['audio_ble_hci_radio_state_prepare_5118e0']&~1:'state'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    if name=='mode':uc.reg_write(UC_ARM_REG_R0,0x20005000)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.hook_add(UC_HOOK_MEM_INVALID,lambda uc,access,address,size,value,user: (print("MEMFAIL",label,is_c,hex(address)),False)[1])
   
   try:u.emu_start((syms[fun[fn][1]] if is_c else fun[fn][0])|1,0x600000,count=150)
   except Exception:print('FAIL_AT',label,is_c,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_R0)),hex(u.reg_read(UC_ARM_REG_R1)));raise
   rows.append((u.reg_read(UC_ARM_REG_R0) if fn=='prepare' else None,calls,bytes(u.mem_read(0x20006000,24)),bytes(u.mem_read(0xe000e000,0x1000))))
  assert rows[0]==rows[1],(label,rows[0][:2],rows[1][:2])
  print('PASS',label,rows[0][:2])
