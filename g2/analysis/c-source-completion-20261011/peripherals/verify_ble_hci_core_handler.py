"""Actual ARM compiled-C/native HCI core event dispatcher at child cuts."""
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_core_handler',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for scenario in ('no_events','empty','event','event_reset','acl_drop','acl_emit','other_free','other_callback','timeout','other_event'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x300000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_stack_state_20073870'] if compiled else 0x20073870
   u.mem_write(state,b'\0'*128)
   if scenario=='event_reset':u.mem_write(state+0x21,b'\x01')
   if scenario in ('acl_emit','other_callback'):u.mem_write(state+(0x10 if scenario=='acl_emit' else 0x18),struct.pack('<I',0x300001))
   u.mem_write(0x20004000,b'Q'*24);u.mem_write(0x20005000,b'\x00\x00'+(b'\x01' if scenario=='timeout' else b'\x02')+b'X'*9)
   event=0x20005000 if scenario in ('timeout','other_event') else 0
   u.reg_write(UC_ARM_REG_R0,0 if scenario=='no_events' else 1)
   u.reg_write(UC_ARM_REG_R1,event);u.reg_write(UC_ARM_REG_R2,0)
   u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   native={'deq':0x4bf9ec,'free':0x4bf9b0,'evt':0x56b390,'reset':0x569b56,'acl':0x52a962,'timeout':0x52aee6}
   compiled_names={'deq':'audio_wsf_queue_dequeue','free':'g2_wsf_candidate_buffer_free_word','evt':'audio_ble_hci_event_process','reset':'audio_ble_hci_reset_sequence','acl':'audio_ble_hci_acl_reassemble','timeout':'audio_ble_hci_command_timeout'}
   cuts={(syms[compiled_names[k]]&~1 if compiled else addr):k for k,addr in native.items()}
   calls=[];deqs=[0]
   def hook(uc,a,size,_):
    if a==0x300000:
     calls.append(('callback',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='deq':
     deqs[0]+=1
     if deqs[0]==1 and scenario not in ('empty','no_events'):
      handler=4 if scenario.startswith('event') else 2 if scenario.startswith('acl') else 5
      if compiled:
       uc.mem_write(0x20003ffc,bytes([handler]));res=0x20003ff8
      else:
       uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes([handler]));res=0x20004000
     else:res=0
    elif k=='acl':calls.append((k,r0));res=0 if scenario=='acl_drop' else 0x20004000
    else:calls.append((k,r0+8 if compiled and k=='free' else r0));res=0
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_core_handler'] if compiled else 0x530cb2)|1,0x600000,count=1200)
   rows.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert rows[0]==rows[1],(scenario,rows)
  print('PASS',scenario,len(rows[0][0]),hex(rows[0][1]))
