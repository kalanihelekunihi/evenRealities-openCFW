#!/usr/bin/env python3
"""Actual C/native LE connectionless IQ report buffer and diagnostic effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_iq_conless.c'
N=['audio_wsf_buffer_alloc','audio_ble_hci_vendor_log_enabled_4c9c50','audio_ble_hci_vendor_compare_44b610','audio_log_flags','audio_log_extended','audio_ble_hci_wsf_trace','audio_queue_copy_bytes','g2_wsf_candidate_buffer_free_word']
A=[0x530446,0x4c9c50,0x44b610,0x43d0ce,0x43d574,0x52a63c,0x439be4,0x5304d4]
STUB='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[16];
void *audio_wsf_buffer_alloc(uint16_t n){(void)n;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t p){(void)p;}
void *audio_queue_copy_bytes(void *d,const void *s,uint32_t n){(void)s;(void)n;return d;}
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
uint32_t audio_ble_hci_vendor_compare_44b610(const void *a,const void *b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint32_t a,const void *b,const void *c,const void *d,...){(void)a;(void)b;(void)c;(void)d;}
void audio_ble_hci_wsf_trace(const void *a,const void *b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_le_conless_iq_report',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(False,False,0,0),(True,False,0,0),(True,True,2,0),(True,True,0,2),(True,False,0,3)]
 for alloc,enabled,flags,count in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   out=0x20080000;src=0x20081000;cb=0x20084000;u.mem_write(out,b'\xcc'*0xc0);u.mem_write(src,bytes([0x34,0x12,1,0x78,0x56,2,3,4,5,0xbc,0x9a,count])+bytes(range(1,2*count+1))+bytes(32))
   cell=(sy['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870);u.mem_write(cell+8,struct.pack('<I',cb+1))
   addr=[sy[n]&~1 for n in N] if is_c else A;calls=[]
   def s(uc,p):return bytes(uc.mem_read(p,120)).split(b'\0')[0]
   def hook(uc,pc,n,user):
    if pc==cb:
     packet=uc.reg_read(UC_ARM_REG_R0);calls.append(('deliver',packet==out,bytes(uc.mem_read(packet,28+2*count))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    if ix==0:calls.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,out if alloc else 0)
    elif ix==1:calls.append(('enabled',));uc.reg_write(UC_ARM_REG_R0,int(enabled))
    elif ix==2:
     x=s(uc,r0);y=s(uc,r1);calls.append(('cmp',x,y,r2));uc.reg_write(UC_ARM_REG_R0,0 if x[:r2]==y[:r2] else 1)
    elif ix==3:calls.append(('flags',));uc.reg_write(UC_ARM_REG_R0,flags)
    elif ix==4:calls.append(('log',r0,s(uc,r1),s(uc,r2),s(uc,uc.reg_read(UC_ARM_REG_R3))))
    elif ix==5:calls.append(('trace',s(uc,r0),s(uc,r1)))
    elif ix==6:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));calls.append(('copy',r0-out,r1-src,r2))
    elif ix==7:calls.append(('free',r0==out))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr+[cb]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,src);u.reg_write(UC_ARM_REG_R1,12+2*count);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_ble_hci_le_conless_iq_report'] if is_c else 0x56a908)|1,0x600000,count=6000)
   pair.append(calls)
  assert pair[0]==pair[1],(alloc,enabled,flags,count,pair)
print('PASS_HCI_IQ_CONLESS_NATIVE',len(cases))
