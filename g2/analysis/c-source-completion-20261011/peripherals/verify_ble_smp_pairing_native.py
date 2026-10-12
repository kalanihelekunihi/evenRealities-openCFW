#!/usr/bin/env python3
"""Actual ARM C/native smpProcPairing comparisons on no-dispatch domains."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_pairing.c'
STUB='''#include <stdint.h>
const uint8_t *audio_ble_comm_registration_slot;
void smpSmExecute(uint8_t *a,const uint8_t *b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_pairing_callback_56e6e0',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 c=bytearray(0x4c);c[0x22]=c[0x29]=1;cases.append(('justworks',c))
 c=bytearray(0x4c);c[0x21]=4;c[0x28]=2;c[0x23]=4;cases.append(('iocap',c))
 cases.append(('plain',bytearray(0x4c)))
 for label,init in cases:
  values=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cfg=0x20080000;ccb=0x20080100;out=0x20080200
   u.mem_write(cfg,bytes(16));u.mem_write(ccb,bytes(init));u.mem_write(out,b'\xff\xff')
   cell=sym['audio_ble_comm_registration_slot'] if compiled else 0x200004b8
   u.mem_write(cell,cfg.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,out)
   u.reg_write(UC_ARM_REG_R2,out+1);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_smp_pairing_callback_56e6e0'] if compiled else 0x56e6e0)|1,0x600000,count=3000)
   values.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,2)),u.mem_read(ccb+0x40,1)))
  assert values[0]==values[1],(label,values)
print('PASS_BLE_SMP_PAIRING_NATIVE 3')
