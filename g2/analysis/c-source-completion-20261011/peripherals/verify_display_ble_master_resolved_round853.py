#!/usr/bin/env python3
"""Controlled Apollo appMasterResolvedAddrInd native/C comparison."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_resolved_addr.c'
stub='''#include <stdint.h>
volatile uint8_t audio_ble_subsystem_state_20071670[0xa0];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_ble_master_resolution_check_47ab6c(const uint8_t*a,uint16_t b){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as directory:
 temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_event_50393e',str(src),str(st),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  obj=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
 def string(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0]
 cases=0
 for pending in (0,1):
  for status in (0,1,7):
   for mask in (0,1,2,4,7):
    for checked in (0,1):
     for index in (0,3):
      pair=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
       for addr,data in segments:u.mem_write(addr,data)
       base=symbols['audio_ble_subsystem_state_20071670'] if compiled else 0x20071670
       u.mem_write(base+0x9c,bytes([pending]));u.mem_write(base+0x97,bytes([index]))
       event=0x20071000;u.mem_write(event,bytes([0x34,0x12,0x37,status]))
       trace=[]
       hooks=[('flags','audio_log_flags',0x43d0ce),('extended','audio_log_extended',0x43d574),('compressed','compressed_log_output',0x43ce9e),('check','audio_ble_master_resolution_check_47ab6c',0x47ab6c)]
       for kind,symbol,native in hooks:
        addr=symbols[symbol] if compiled else native
        def hook(uc,pc,width,user,kind=kind):
         r0,r1,r2,r3=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
         if kind=='flags':trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,mask)
         elif kind=='extended':
          sp=uc.reg_read(UC_ARM_REG_SP);line,fmt=struct.unpack('<II',uc.mem_read(sp,8));args=(struct.unpack('<I',uc.mem_read(sp+8,4))[0],) if b'%' in string(uc,fmt) else ()
          trace.append((kind,r0,string(uc,r1),string(uc,r2),string(uc,r3),line,string(uc,fmt),*args))
         elif kind=='compressed':
          args=(r3,) if b'%' in string(uc,r1) else ()
          trace.append((kind,r0,string(uc,r1),string(uc,r2),*args))
         else:trace.append((kind,r0-base,r1));uc.reg_write(UC_ARM_REG_R0,checked)
         uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,0x20072000)
       try:u.emu_start((symbols['audio_ble_master_event_50393e'] if compiled else 0x50393e)|1,0x600000,count=15000)
       except Exception as err:raise AssertionError((pending,status,mask,checked,index,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
       pair.append((trace,bytes(u.mem_read(base+0x97,6))))
      assert pair[0]==pair[1],(pending,status,mask,checked,index,pair)
      cases+=1
print('PASS_DISPLAY_BLE_MASTER_RESOLVED_NATIVE',cases)
