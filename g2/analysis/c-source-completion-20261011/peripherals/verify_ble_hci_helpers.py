"""Actual ARM compiled-C/native HCI registration and WSF message wrappers."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_core_handler.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[128];
void *audio_wsf_queue_dequeue(void*a){(void)a;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t a){(void)a;}
void audio_ble_hci_event_process(void*a){(void)a;}
void audio_ble_hci_reset_sequence(void*a){(void)a;}
void *audio_ble_hci_acl_reassemble(void*a){return a;}
void audio_ble_hci_command_timeout(void*a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_hci_register',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind in ('register','deq','free','handler'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_stack_state_20073870'] if compiled else 0x20073870
   u.mem_write(state,b'X'*128);u.mem_write(0x20004000,b'Y'*24);u.mem_write(0x20004004,b'\x23')
   u.reg_write(UC_ARM_REG_R0,0x12345679 if kind=='register' else 0x20005000 if kind=='deq' else 0x20004008 if kind=='free' else 0x101)
   u.reg_write(UC_ARM_REG_R1,0x87654321 if kind=='register' else 0x20005010 if kind=='deq' else 0x20006000)
   u.reg_write(UC_ARM_REG_R2,0x3456);u.reg_write(UC_ARM_REG_R3,0x789a)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   calls=[]
   cuts={(syms['audio_wsf_queue_dequeue']&~1 if compiled else 0x538c4a):'deq',
         (syms['g2_wsf_candidate_buffer_free_word']&~1 if compiled else 0x5304d4):'free',
         (syms['audio_ble_hci_core_handler']&~1 if compiled else 0x530cb2):'core'}
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='deq':res=0x20004000
    elif k=='core':calls.append((k,r0,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)));res=0
    else:calls.append((k,r0));res=0
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   name={'register':'audio_ble_l2c_hci_register','deq':'audio_ble_wsf_message_dequeue','free':'audio_ble_wsf_message_free','handler':'audio_ble_handler_536814'}[kind]
   native={'register':0x5367f0,'deq':0x4bf9ec,'free':0x4bf9b0,'handler':0x536814}[kind]
   u.emu_start((syms[name] if compiled else native)|1,0x600000,count=500)
   result=(bytes(u.mem_read(state+0x10,8)) if kind=='register' else (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20005010,1))) if kind=='deq' else None)
   rows.append((calls,result))
  assert rows[0]==rows[1],(kind,rows)
  print('PASS',kind,rows[0])
