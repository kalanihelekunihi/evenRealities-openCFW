"""Actual ARM C/native LE report allocation, delivered event bytes, and frees."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_le_reports.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[0x80];
void *audio_wsf_buffer_alloc(uint16_t n){(void)n;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t p){(void)p;}
'''
DATA={
 'adv':bytes([1,2,3,1,2,3,4,5,6,3,0xa1,0xa2,0xa3,0xb0]),
 'direct':bytes([1,2,3,1,2,3,4,5,6,4,7,8,9,10,11,12,0xb0]),
 'ext':bytes([1,0x34,0x12,2,1,2,3,4,5,6,3,4,5,6,7,0x45,0x23,8,1,2,3,4,5,6,3,0xa1,0xa2,0xa3]),
 'per':bytes([0x34,0x12,2,3,4,5,3,0xa1,0xa2,0xa3])}
FUN={'adv':(0x56a398,'audio_ble_hci_le_adv_report'),'direct':(0x56ab50,'audio_ble_hci_le_direct_adv_report'),'ext':(0x56a430,'audio_ble_hci_le_ext_adv_report'),'per':(0x56a5be,'audio_ble_hci_le_per_adv_report')}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_le_adv_report',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label in DATA:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   u.mem_write(state,b'\x00'*0x80);u.mem_write(state+8,struct.pack('<I',0x20005001))
   u.mem_write(0x20008000,DATA[label]+bytes(100));u.mem_write(0x20009000,b'\xdd'*0x100)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20008000);u.reg_write(UC_ARM_REG_R3,0x12345678)
   cuts={0x530446:'alloc',0x5304d4:'free',0x20005000:'callback'} if not is_c else {syms['audio_wsf_buffer_alloc']&~1:'alloc',syms['g2_wsf_candidate_buffer_free_word']&~1:'free',0x20005000:'callback'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0)))
    if name=='alloc':uc.reg_write(UC_ARM_REG_R0,0x20009000)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[FUN[label][1]] if is_c else FUN[label][0])|1,0x600000,count=3000)
   rows.append((u.reg_read(UC_ARM_REG_R0) if label!='direct' else None,calls,bytes(u.mem_read(0x20009000,0x60))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,[x[0] for x in rows[0][1]])
