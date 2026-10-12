#!/usr/bin/env python3
"""Actual compiled-C/native pair auth byte and connected ring policy reset."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_auth_flag.c'
S2=R/'components/audio/uart_thread_source_candidate/display_ble_ring_policy_children.c'
stub='''
#include <stdint.h>
uint8_t audio_ble_pair_auth_flag_20074ffc;
uint32_t audio_ble_ring_policy_deadline_200748fc;
uint8_t audio_ble_ring_policy_pending_2007500b;
uint8_t audio_ble_ring_policy_state_2007408c[16];
__attribute__((noinline)) uint32_t audio_log_flags(void){asm volatile("");return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){asm volatile(""::"r"(a),"r"(b),"r"(c),"r"(d),"r"(e),"r"(f));}
__attribute__((noinline)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){asm volatile(""::"r"(a),"r"(b),"r"(c));return 0;}
__attribute__((naked)) void audio_event_loop_remove_delayed(void (*f)(void)){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t g2_flashdb_candidate_tick(void){__asm volatile("bx lr");}
__attribute__((naked)) void PB_TxEncodeNotifyRingConnectInfo(uint8_t x){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,PB_LastTxEncodeRingConnectInfoTimeSet',str(S),str(S2),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  def run(native,cname,arg,flags):
    pair=[]
    for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for a,d in seg:u.mem_write(a,d)
      cells=[(0x20074ffc,'audio_ble_pair_auth_flag_20074ffc',b'\x55'),
             (0x200748fc,'audio_ble_ring_policy_deadline_200748fc',struct.pack('<I',0x12345678)),
             (0x2007500b,'audio_ble_ring_policy_pending_2007500b',b'\x66'),
             (0x2007408c,'audio_ble_ring_policy_state_2007408c',b'\x02\0\0\0'+struct.pack('<I',0x12345678)+b'\x07')]
      for original,symbol,data in cells:u.mem_write(sym[symbol] if is_c else original,data)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,arg)
      seen=[]
      def string(uc,p):return bytes(uc.mem_read(p,180)).split(b'\0')[0]
      def hook(uc,a,size,_):
        if a in (0x43d0ce,sym['audio_log_flags']&~1):
          uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x43ce9e,sym['compressed_log_output']&~1):
          seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))))
          uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x43d574,sym['audio_log_extended']&~1):
          line,p=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))
          seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,p)))
          uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x476ace,sym['audio_event_loop_remove_delayed']&~1):
          seen.append(('remove',))
          uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x4490cc,sym['g2_flashdb_candidate_tick']&~1):
          seen.append(('tick',))
          uc.reg_write(UC_ARM_REG_R0,0x89abcdef)
          uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a in (0x4bc418,sym['PB_TxEncodeNotifyRingConnectInfo']&~1):
          seen.append(('notify',uc.reg_read(UC_ARM_REG_R0)&255))
          uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,hook)
      u.emu_start((sym[cname] if is_c else native)|1,0x600000,count=350)
      state=tuple(bytes(u.mem_read(sym[symbol] if is_c else original,len(data))) for original,symbol,data in cells)
      pair.append((seen,state,u.reg_read(UC_ARM_REG_R0)&255 if cname=='pairMgrSecAuthFlagGet' else None))
    assert pair[0]==pair[1],(cname,arg,flags,pair)
  for value in (0,1,255):
    run(0x4bb9b4,'pairMgrSecAuthFlagSet',value,0);cases+=1
  run(0x4bb9bc,'pairMgrSecAuthFlagGet',0,0);cases+=1
  for value in (0,1,0x1234):
    for flags in (0,1,2):
      run(0x4bbf44,'PB_LastTxEncodeRingConnectInfoTimeSet',value,flags);cases+=1
  for state in (0,1,2):
    for flags in (0,1,2):
      run(0x49f0da,'audio_ble_ring_policy_enter_state',state,flags);cases+=1
  for flags in (0,1,2):
    run(0x49f500,'audio_ble_ring_policy_delayed',0,flags);cases+=1
  print('PASS_BLE_PAIR_AUTH_POLICY_NATIVE',cases)
