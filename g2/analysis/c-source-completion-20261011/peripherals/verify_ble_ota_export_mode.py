"""Actual compiled-C/native OTA bootloader flag no-change/write transitions with flash cut."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>\n#include <stdbool.h>
volatile uint32_t audio_ble_bootloader_flag;const uint8_t audio_ble_ota_flag_seed[16]={0};
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return a;}
void audio_dump_hex(const char*a,uint32_t b,const uint8_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
uint32_t g2_gpio_critical_save(void){return 0;}
int32_t audio_ble_nvm_write_words(uint32_t a,const uint8_t*b,uint8_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_export_mode_set',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_ota_export_mode.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names=[('audio_queue_copy_bytes',0x439c04),('audio_dump_hex',0x43dacc),('g2_gpio_critical_save',0x473940),('audio_ble_nvm_write_words',0x4d0a2c),('audio_log_level',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
 for requested,prior,status in ((7,7,0),(9,7,0),(9,7,5)):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   flag=syms['audio_ble_bootloader_flag'] if compiled else 0x7fe000;u.mem_write(flag,struct.pack('<I',prior));calls=[]
   cuts={(syms[n]&~1 if compiled else a):n for n,a in names}
   def hook(uc,a,size,_):
    if a==(syms['audio_ble_ota_export_mode_set']+0x120 if compiled else 0x47891e):
     uc.reg_write(UC_ARM_REG_PC,a+5);return
    n=cuts.get(a)
    if n is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
    if n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_dump_hex':calls.append(('dump',r1,r3))
    elif n=='audio_queue_copy_bytes':calls.append(('copy',r2))
    elif n=='g2_gpio_critical_save':calls.append(('save',));uc.reg_write(UC_ARM_REG_R0,1)
    elif n=='audio_ble_nvm_write_words':calls.append(('write',r0,struct.unpack('<I',uc.mem_read(r1,4))[0],r2==flag,r3));uc.reg_write(UC_ARM_REG_R0,status)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,requested);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);
   try:u.emu_start((syms['audio_ble_ota_export_mode_set'] if compiled else 0x478860)|1,0x600000,count=500)
   except Exception as e:print('FAULT',compiled,hex(u.reg_read(UC_ARM_REG_PC)),calls);raise
   obs.append(calls)
  assert obs[0]==obs[1],(requested,prior,status,obs)
  print('PASS OTA export',requested,prior,status)
