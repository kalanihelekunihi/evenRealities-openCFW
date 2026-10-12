#!/usr/bin/env python3
"""Compiled C/native RPC_SystemBleStatusSync payload and argument order."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_comm_proc_children.c'
raw=B[0x78c9a4-0x438000:0x78c9a4-0x438000+16]
stub='''
#include <stdint.h>
uint8_t audio_ble_atts_connection_rows[256];
const uint8_t audio_ble_comm_profile_table[16]={'''+','.join(str(x) for x in raw)+'''};
__attribute__((noinline)) uint32_t audio_log_flags(void){asm volatile("");return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
__attribute__((noinline)) uint8_t audio_uart_device_role_get(void){asm volatile("");return 0;}
__attribute__((noinline)) int32_t audio_ble_send_status_message(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){asm volatile(""::"r"(a),"r"(b),"r"(c),"r"(d));return 0;}
'''
with tempfile.TemporaryDirectory() as td:
    mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_security_state',str(S),str(mock),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
        sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for state in (0,1,0xff):
      for role in (0,1,2):
        pair=[]
        for is_c in (False,True):
          u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
          u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
          u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
          for a,d in seg:u.mem_write(a,d)
          u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,state)
          seen=[]
          def hook(uc,a,size,_):
            if a in (0x43d0ce,sym['audio_log_flags']&~1):
              uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            elif a in (0x45a568,sym['audio_uart_device_role_get']&~1):
              seen.append(('role',));uc.reg_write(UC_ARM_REG_R0,role)
              uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            elif a in (0x464d1c,sym['audio_ble_send_status_message']&~1):
              seen.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2),
                uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8))))
              uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
          u.hook_add(UC_HOOK_CODE,hook)
          u.emu_start((sym['audio_ble_slave_security_state'] if is_c else 0x4b82e8)|1,0x600000,count=500)
          pair.append(seen)
        assert pair[0]==pair[1],(state,role,pair)
        cases+=1
    print('PASS_BLE_COMM_SECURITY_NATIVE',cases)
