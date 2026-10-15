#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo Cordio AppDbHandleResolvedAddr."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_resolution_check.c'
stub='''#include <stdint.h>
uint8_t audio_ble_dm_conn_state_table_20067a30[10*200];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as directory:
 temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_resolution_check_47ab6c',str(src),str(st),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  obj=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
 def string(u,p):return bytes(u.mem_read(p,200)).split(b'\0')[0]
 cases=0
 for index in (0,3,9,10,65535):
  for valid in (0,1):
   for inuse in (0,1):
    for ltk in (0,1):
     for mask in (0,1,2,4,7):
      pair=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
       for addr,data in segments:u.mem_write(addr,data)
       base=symbols['audio_ble_dm_conn_state_table_20067a30'] if compiled else 0x20067a30
       if index<10:
        row=base+index*200;u.mem_write(row+0x2e,bytes([ltk,valid,inuse]))
       address=0x20071000;u.mem_write(address,bytes([1,2,3,4,5,6]));trace=[]
       hooks=[('flags','audio_log_flags',0x43d0ce),('extended','audio_log_extended',0x43d574),('compressed','compressed_log_output',0x43ce9e)]
       for kind,symbol,native in hooks:
        addr=symbols[symbol] if compiled else native
        def hook(uc,pc,width,user,kind=kind):
         r0,r1,r2,r3=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3));sp=uc.reg_read(UC_ARM_REG_SP)
         if kind=='flags':trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,mask)
         elif kind=='extended':
          line,fmt=struct.unpack('<II',uc.mem_read(sp,8));n=7 if b'address of record' in string(uc,fmt) else 0
          args=struct.unpack('<'+'I'*n,uc.mem_read(sp+8,n*4)) if n else ()
          trace.append((kind,r0,string(uc,r1),string(uc,r2),string(uc,r3),line,string(uc,fmt),*args))
         else:
          n=7 if b'address of record' in string(uc,r1) else 0
          args=(r3,*struct.unpack('<'+'I'*(n-1),uc.mem_read(sp,(n-1)*4))) if n else ()
          trace.append((kind,r0,string(uc,r1),string(uc,r2),*args))
         uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,address);u.reg_write(UC_ARM_REG_R1,index)
       try:u.emu_start((symbols['audio_ble_master_resolution_check_47ab6c'] if compiled else 0x47ab6c)|1,0x600000,count=15000)
       except Exception as err:raise AssertionError((index,valid,inuse,ltk,mask,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
       pair.append((u.reg_read(UC_ARM_REG_R0),trace))
      assert pair[0]==pair[1],(index,valid,inuse,ltk,mask,pair)
      cases+=1
print('PASS_DISPLAY_BLE_MASTER_RESOLUTION_NATIVE',cases)
