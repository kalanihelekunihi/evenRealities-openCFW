#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo display channel set 0x465d7c."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_channel_set.c'
stubs='''#include <stdint.h>
void *g2_uart_send_queue;void *audio_uart_master_schedule_queue;
void *audio_uart_alloc_retry(uint32_t n){(void)n;return 0;}
void audio_file_heap_free(void*p){(void)p;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t x){(void)p;(void)n;(void)x;}
uint8_t audio_uart_device_role_get(void){return 0;}
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_delay_scheduler_assert(void){}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
base_cases=[(2,True,0,0),(1,False,0,0),(1,True,1,0),
            (1,True,2,0),(1,True,0,0),(1,True,0,1)]
base_cases=[(*case,None) for case in base_cases]+[(1,True,0,0,2)]
cases=[(*case,level,channel) for case in base_cases for level in (0,1,2,4,7) for channel in (0,0x1234,0xffff5678)]
with tempfile.TemporaryDirectory() as d:
 tmp=Path(d);stub=tmp/'stub.c';stub.write_text(stubs);elf=tmp/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_channel_set',str(src),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for role,queue_present,alloc_fail,queue_status,second_role,level,channel in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for addr,data in segments:u.mem_write(addr,data)
   cells=(syms['g2_uart_send_queue'],syms['audio_uart_master_schedule_queue']) if compiled else (0x200749cc,0x200749d0)
   for cell,value in zip(cells,(0x20071000 if queue_present else 0,0x20071004)):
    u.mem_write(cell,struct.pack('<I',value))
   node=0x20080000;packet=0x20081000
   u.mem_write(node,b'\xa5'*32);u.mem_write(packet,b'\xa5'*32)
   trace=[];allocation=[0];roles=[0]
   hooks=[('alloc','audio_uart_alloc_retry',0x4646f0),('free','audio_file_heap_free',0x474d16),
          ('zero','audio_uart_buffer_zero',0x43c0e4),('role','audio_uart_device_role_get',0x45a568),
          ('queue','audio_cmsis_queue_put',0x449abe),('level','audio_log_level',0x43d0ce),
          ('extended','audio_log_extended',0x43d574),('compact','compressed_log_output',0x43ce9e),
          ('assert','audio_delay_scheduler_assert',0x5fa0a4)]
   for kind,symbol,native in hooks:
    addr=syms[symbol] if compiled else native
    def hook(uc,pc,width,user,kind=kind):
     regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
     if kind=='alloc':
      allocation[0]+=1;trace.append(('alloc',regs[0]))
      uc.reg_write(UC_ARM_REG_R0,0 if allocation[0]==alloc_fail else (node if allocation[0]==1 else packet))
     elif kind=='free':trace.append(('free',regs[0]))
     elif kind=='zero':uc.mem_write(regs[0],bytes([regs[2]&255])*regs[1])
     elif kind=='role':
      roles[0]+=1;trace.append(('role',))
      uc.reg_write(UC_ARM_REG_R0,second_role if roles[0]>1 and second_role is not None else role)
     elif kind=='queue':
      address=struct.unpack('<I',uc.mem_read(regs[1],4))[0]
      trace.append(('queue',regs[0],bytes(uc.mem_read(address,12)),bytes(uc.mem_read(packet,8)),regs[2],regs[3]))
      uc.reg_write(UC_ARM_REG_R0,queue_status)
     elif kind=='level':uc.reg_write(UC_ARM_REG_R0,level)
     elif kind=='extended':
      strings=[bytes(uc.mem_read(a,100)).split(b'\0')[0] for a in regs[1:4]]
      line,fmt_ptr=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8))
      trace.append(('extended',regs[0],*strings,line,bytes(uc.mem_read(fmt_ptr,130)).split(b'\0')[0]))
     elif kind=='compact':
      strings=[bytes(uc.mem_read(a,140)).split(b'\0')[0] for a in regs[1:3]]
      trace.append(('compact',regs[0],*strings))
     elif kind=='assert':trace.append(('assert',));uc.reg_write(UC_ARM_REG_PC,0x600000);return
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(channel,0x5678,0,0)):
    u.reg_write(reg,value)
   try:u.emu_start((syms['audio_uart_display_channel_set'] if compiled else 0x465d7c)|1,0x600000,count=20000)
   except Exception as error:raise AssertionError((role,queue_present,alloc_fail,queue_status,second_role,level,channel,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from error
   terminal=role==1 and queue_present and not alloc_fail and queue_status and second_role in (None,1)
   pair.append((None if terminal else u.reg_read(UC_ARM_REG_R0),trace,
                bytes(u.mem_read(node,12)),bytes(u.mem_read(packet,8))))
  assert pair[0]==pair[1],(role,queue_present,alloc_fail,queue_status,second_role,level,channel,pair)
print('PASS_DISPLAY_CHANNEL_SET_NATIVE',len(cases))
