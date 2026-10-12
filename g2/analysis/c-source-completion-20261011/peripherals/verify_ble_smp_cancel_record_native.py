#!/usr/bin/env python3
"""Connected native/C SMP CCB, failure and cancellation effects, logging enabled."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_cancel_record.c'
T=R/'components/audio/uart_thread_source_candidate/display_ble_comm_registration_slot_storage.c'
stub='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xfc];volatile uint8_t audio_ble_trace_level_cell;
__attribute__((naked)) uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t n){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t l,const char*m,const char*p,const char*n,uint32_t x,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_wsf_trace(const char*a,const char*b,...){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t *smpDbGetRecord(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) void __aeabi_memcpy(void*d,const void*s,unsigned n){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpScGetCancelMsgWithReattempt',str(S),str(T),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('lookup','failure','cancel'):
  for conn in ((0,1,2,3) if mode=='lookup' else (1,2,3)):
   for counter in ((0,2,4) if mode=='cancel' else (0,)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     ccb=sym['audio_ble_smp_handler_state'] if is_c else 0x20070aec
     cfgslot=sym['audio_ble_comm_registration_slot'] if is_c else 0x200004b8
     trace=sym['audio_ble_trace_level_cell'] if is_c else 0x2007502f
     cfg=0x2007f500;rec=0x2007f400;msg=0x2007f200
     u.mem_write(ccb,bytes([0]*0xfc));u.mem_write(ccb+(conn-1)*0x4c+0x42,bytes([counter])) if conn else None
     u.mem_write(cfg,bytes([0xaa]*7+[3]+[0xcc]*8+[1,2,3,4]+[0xdd]*64))
     u.mem_write(cfgslot,struct.pack('<I',cfg));u.mem_write(trace,b'\x01');u.mem_write(rec,bytes([0x77]*64));u.mem_write(msg,bytes([0xa5]*64))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,conn)
     if mode=='cancel':u.reg_write(UC_ARM_REG_R1,msg);u.reg_write(UC_ARM_REG_R2,12)
     seen=[]
     def cstr(p):
      if not p:return ''
      return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('latin1')
     def hook(uc,a,size,_):
      if a in (0x4c9c50,):uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a==(sym['g2_smp_candidate_compare']&~1):
       x=uc.reg_read(UC_ARM_REG_R1);y=uc.reg_read(UC_ARM_REG_R2);n=uc.reg_read(UC_ARM_REG_R3);bx=bytes(uc.mem_read(x,n));by=bytes(uc.mem_read(y,n));v=(bx>by)-(bx<by);uc.reg_write(UC_ARM_REG_R0,v&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,2);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43d574,sym['audio_log_extended']&~1):
       sp=uc.reg_read(UC_ARM_REG_SP);line,fmt,val=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
       seen.append(('log',uc.reg_read(UC_ARM_REG_R0),cstr(uc.reg_read(UC_ARM_REG_R1)),cstr(uc.reg_read(UC_ARM_REG_R2)),cstr(uc.reg_read(UC_ARM_REG_R3)),line,cstr(fmt),val))
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x541fb8,sym['smpDbGetRecord']&~1):seen.append(('record',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,rec);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x439be4,sym['__aeabi_memcpy']&~1):
       dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);uc.mem_write(dst,bytes(uc.mem_read(src,n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     entry=sym[{'lookup':'smpCcbByConnId','failure':'SmpDbPairingFailed','cancel':'SmpScGetCancelMsgWithReattempt'}[mode]] if is_c else {'lookup':0x5375fc,'failure':0x542838,'cancel':0x56d188}[mode]
     u.emu_start(entry|1,0x600000,count=1000)
     rv=u.reg_read(UC_ARM_REG_R0)-ccb if mode=='lookup' and conn else (u.reg_read(UC_ARM_REG_R0) if mode=='lookup' else None)
     pair.append((seen,rv,bytes(u.mem_read(rec+0x10,4)) if mode!='lookup' else None,bytes(u.mem_read(msg,4)) if mode=='cancel' else None,bytes(u.mem_read(ccb+(conn-1)*0x4c+0x42,1)) if mode=='cancel' else None))
    assert pair[0]==pair[1],(mode,conn,counter,pair)
    cases+=1
 print('PASS_BLE_SMP_CANCEL_RECORD_NATIVE',cases)
