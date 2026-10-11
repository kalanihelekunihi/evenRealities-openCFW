"""Actual compiled-C/native HCI custom BD address null/zero/nonzero cases."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t audio_ble_custom_bd_address[6];
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_set_custom_bdaddr',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_custom_bd_address.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for payload in (None,b'\0'*6,b'ABCDEF'):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cell=syms['audio_ble_custom_bd_address'] if compiled else 0x20074148;u.mem_write(cell,b'XXXXXX');calls=[]
   if payload:u.mem_write(0x20004000,payload)
   cuts={(syms['audio_queue_copy_bytes']&~1 if compiled else 0x439be4):'copy'}
   def hook(uc,a,size,_):
    if a not in cuts:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);calls.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,0x20004000 if payload is not None else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['audio_ble_hci_set_custom_bdaddr'] if compiled else 0x4b4cd2)|1,0x600000,count=300)
   obs.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(cell,6))))
  assert obs[0]==obs[1],(payload,obs);print('PASS custom BD',payload)
