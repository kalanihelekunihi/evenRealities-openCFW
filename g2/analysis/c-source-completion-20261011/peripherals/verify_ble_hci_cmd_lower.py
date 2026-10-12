"""ARM C/native HCI command failure and completion child effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_cmd_lower.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[0x40],audio_ble_hci_cmd_state_20073a90[0x40];
void *audio_wsf_buffer_alloc(uint16_t n){(void)n;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t a){(void)a;}
void WsfTimerStop(void *p){(void)p;}
void audio_ble_hci_cmd_send(uint32_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_cmd_status_failure',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,status,opcode,alloc_ok in (('status_other',3,0x2026,True),('opcode_other',0x12,0x2018,True),('alloc_fail',0x12,0x2026,False),('status_fail',0x12,0x2026,True),('recv',0,0,False)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   stack=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   cmd=syms['audio_ble_hci_cmd_state_20073a90'] if is_c else 0x20073a90
   u.mem_write(stack,b'\x00'*0x40);u.mem_write(stack+0xc,struct.pack('<I',0x100701));u.mem_write(cmd,b'\x00'*0x40)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_R1,opcode)
   native={0x530446:'alloc',0x5304d4:'free',0x52a4d2:'timer',0x52ae5e:'send'}
   compiled={syms['audio_wsf_buffer_alloc']&~1:'alloc',syms['g2_wsf_candidate_buffer_free_word']&~1:'free',syms['WsfTimerStop']&~1:'timer',syms['audio_ble_hci_cmd_send']&~1:'send'}
   cuts=compiled if is_c else native;calls=[]
   def hook(uc,a,size,_):
    if a==0x100700:
     calls.append(('callback',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a not in cuts:return
    name=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0);calls.append((name,0 if name=='timer' else r0))
    uc.reg_write(UC_ARM_REG_R0,0x20006000 if name=='alloc' and alloc_ok else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_hci_cmd_receive_complete'] if is_c else 0x52aef8) if label=='recv' else (syms['audio_ble_hci_cmd_status_failure'] if is_c else 0x56b100)
   u.emu_start(entry|1,0x600000,count=250)
   results.append((calls,bytes(u.mem_read(0x20006000,4)),bytes(u.mem_read(cmd+0x1a,1))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0])
