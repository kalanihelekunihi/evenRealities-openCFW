#!/usr/bin/env python3
"""Actual ARM C/native SMP L2C data valid Pairing Failed and invalid opcode."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_l2c_data.c'
STUB='''#include <stdint.h>
uint8_t *test_ccb;uint8_t test_event[8];volatile uint8_t audio_ble_trace_level_cell;
const uint8_t audio_ble_smp_packet_lengths[16]={0,7,7,17,17,2,17,11,17,8,17,2,65,17,2,0};
uint8_t *smpCcbByHandle(uint16_t h){(void)h;return test_ccb;}
void smpSmExecute(uint8_t*a,const uint8_t*b){(void)a;for(int i=0;i<8;i++)test_event[i]=b[i];}
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_l2c_data_callback_537278',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case in ('failed','normal','invalid'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ccb=0x20080000;packet=0x20080100;event=sym['test_event'] if compiled else 0x20090000
   c=bytearray(0x4c);c[0x3d]=3;c[0x3f]=1;u.mem_write(ccb,bytes(c));u.mem_write(event,bytes(8))
   p=bytearray(16);p[8]=5 if case=='failed' else (1 if case=='normal' else 0);p[9]=0x7f;u.mem_write(packet,bytes(p))
   if case=='normal':c[0x3f]=1;u.mem_write(ccb,bytes(c))
   u.mem_write(0x200ff000-48,bytes([0xa5]*48))
   if compiled:u.mem_write(sym['test_ccb'],ccb.to_bytes(4,'little'))
   else:
    def hook(uc,pc,n,user):
     if pc==0x5375c8:uc.reg_write(UC_ARM_REG_R0,ccb)
     elif pc==0x56ee62:uc.mem_write(event,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8)))
     elif pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x5375c8,0x56ee62,0x4c9c50,0x52a63c):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,0x1234);u.reg_write(UC_ARM_REG_R1,7 if case=='normal' else 2)
   u.reg_write(UC_ARM_REG_R2,packet);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_smp_l2c_data_callback_537278'] if compiled else 0x537278)|1,0x600000,count=7000)
   pair.append((bytes(u.mem_read(ccb,0x4c)),bytes(u.mem_read(event,8))))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_SMP_L2C_DATA_NATIVE 3')
