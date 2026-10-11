"""Actual compiled-C/native bounded advertising-format and scan-response children."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t audio_ble_adv_name_buffer[96];
int32_t audio_ble_format_to_buffer(char*a,const char*b,...){(void)a;(void)b;return 0;}
uint32_t g2_log_module_length(const char*a){(void)a;return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
uint32_t audio_uart_command_pending(void){return 0;}
int32_t audio_ble_parse_version(const char*a,const char*b,uint32_t*c,uint32_t*d,uint32_t*e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_adv_format_data',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_adv_name_children.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names=[('audio_ble_format_to_buffer',0x4b4728),('g2_log_module_length',0x44a43c),('audio_queue_copy_bytes',0x439be4),('audio_uart_command_pending',0x4abe60),('audio_ble_parse_version',0x475fc0),('audio_log_level',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
 for name,native,arg,output in [('audio_ble_adv_format_data',0x46dc74,7,b'07'),('audio_ble_adv_set_scan_response',0x46dca4,0x20004000,b'665544')]:
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   base=syms['audio_ble_adv_name_buffer'] if compiled else 0x200003ec;u.mem_write(0x20004000,b'\x44\x55\x66\x77');calls=[];cuts={(syms[n]&~1 if compiled else a):n for n,a in names}
   def hook(uc,a,size,_):
    n=cuts.get(a)
    if n is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    if n=='audio_ble_format_to_buffer':uc.mem_write(r0,output+b'\0');calls.append(('format',))
    elif n=='g2_log_module_length':uc.reg_write(UC_ARM_REG_R0,len(output));calls.append(('length',))
    elif n=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));calls.append(('copy',r2))
    elif n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms[name] if compiled else native)|1,0x600000,count=250)
   obs.append((calls,bytes(u.mem_read(base+8,6)),bytes(u.mem_read(base+13,7)),bytes(u.mem_read(base+49,6)),u.reg_read(UC_ARM_REG_R0)))
  assert obs[0][:4]==obs[1][:4],(name,obs)
  print('PASS adv child',name)
