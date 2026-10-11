"""Actual compiled-C/native connected BLE link-state setup."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_subsystem_state_20071670[0xa0],audio_ble_subsystem_rows_200733fc[0x30],audio_ble_subsystem_link_state_200719c8[0x80];
void (*audio_ble_subsystem_callback_slot)(void),(*audio_ble_subsystem_primary_callback_slot)(void);
void audio_ble_subsystem_handler_503936(void){} void audio_ble_subsystem_primary_handler_4b3bec(void){}
void audio_ble_atts_csf_callback_53482c(void){} void audio_ble_atts_csf_register(void (*f)(void)){(void)f;}
void audio_ble_subsystem_child_479418(void){}
void __aeabi_memclr(void *p,unsigned n){volatile unsigned char *b=p;for(unsigned i=0;i<n;i++)b[i]=0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_subsystem_child_4b3c02',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_subsystem_children.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 obs=[]
 for c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  base=syms['audio_ble_subsystem_link_state_200719c8'] if c else 0x200719c8
  slot=syms['audio_ble_subsystem_primary_callback_slot'] if c else 0x200740fc
  u.mem_write(base,b'\xaa'*0x80)
  calls=[];cut=(syms['audio_ble_subsystem_child_479418']&~1) if c else 0x479418
  def hook(uc,a,size,_):
   if a==cut:calls.append(a);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['audio_ble_subsystem_child_4b3c02'] if c else 0x4b3c02)|1,0x600000,count=30000)
  ptr=struct.unpack('<I',u.mem_read(slot,4))[0]
  if c and ptr==(syms['audio_ble_subsystem_primary_handler_4b3bec']|1):ptr=0x4b3bed
  obs.append((bytes(u.mem_read(base,0x80)),ptr,len(calls)))
 assert obs[0]==obs[1],(obs[0][1:],obs[1][1:])
 print('PASS connected BLE link-state init and callback',len(obs[0][0]),'bytes')
