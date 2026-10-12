"""Controlled compiled ARM C/native ring, WSF event, and error callback effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_driver_children.c'
SHIM='''#include <stdint.h>
uint8_t audio_wsf_task_state[0x80];
volatile uint32_t audio_ble_hci_error_value_20074648;
uint32_t audio_ble_hci_error_callback_20074644;
void audio_wsf_cs_enter(void){}
void audio_wsf_cs_exit(void){}
void audio_wsf_set_os_event(void){}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_ring_commit_530084',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 funcs={'ring':(0x530084,'audio_ble_hci_ring_commit_530084'),'event':(0x52b91e,'audio_ble_wsf_set_event'),'error':(0x4b47ae,'audio_ble_hci_error_check_4b47ae')}
 for label,fn in [('ring_empty','ring'),('ring_data','ring'),('ring_full','ring'),('event','event'),('error_zero','error'),('error_set','error')]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_wsf_task_state'] if is_c else 0x20073230
   error=syms['audio_ble_hci_error_value_20074648'] if is_c else 0x20074648
   callback=syms['audio_ble_hci_error_callback_20074644'] if is_c else 0x20074644
   u.mem_write(state,b'\x00'*0x80);u.mem_write(error,struct.pack('<I',0));u.mem_write(callback,struct.pack('<I',0x20005001));
   ring=0x20006000;payload=0x20007000;storage=0x20008000
   u.mem_write(ring,struct.pack('<IIIIII',0,0,0,1 if label=='ring_full' else 8,3,storage));u.mem_write(payload,b'ABC');u.mem_write(storage,b'\xdd'*20)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R7,0x12345678);u.reg_write(UC_ARM_REG_R3,0x87654321)
   if fn=='ring':u.reg_write(UC_ARM_REG_R0,ring);u.reg_write(UC_ARM_REG_R1,0 if label=='ring_empty' else payload);u.reg_write(UC_ARM_REG_R2,1)
   elif fn=='event':u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,0x41)
   else:u.reg_write(UC_ARM_REG_R0,0 if label=='error_zero' else 0x09000001)
   cuts={0x52b8a4:'enter',0x52b8b6:'exit',0x52b8d8:'os',0x20005000:'callback',0x473940:'save',0x5300d8:'restore_inline'} if not is_c else {syms['audio_wsf_cs_enter']&~1:'enter',syms['audio_wsf_cs_exit']&~1:'exit',syms['audio_wsf_set_os_event']&~1:'os',0x20005000:'callback',syms['g2_power_critical_save']&~1:'save',syms['g2_power_critical_restore']&~1:'restore'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a]
    if name=='restore_inline':uc.reg_write(UC_ARM_REG_PC,0x5300dd);return
    if name=='save':uc.reg_write(UC_ARM_REG_R0,0)
    if name not in ('save','restore'):calls.append((name,uc.reg_read(UC_ARM_REG_R0) if name=='callback' else 0))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   
   try:u.emu_start((syms[funcs[fn][1]] if is_c else funcs[fn][0])|1,0x600000,count=600)
   except Exception:print('FAIL_AT',label,is_c,hex(u.reg_read(UC_ARM_REG_PC)));raise
   rows.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if fn=='ring' else 0,calls,bytes(u.mem_read(state+0x28,0x15)),bytes(u.mem_read(error,4)),bytes(u.mem_read(ring,24)),bytes(u.mem_read(storage,12))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][:3])
