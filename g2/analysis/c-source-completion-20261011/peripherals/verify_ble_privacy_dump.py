"""Compiled-C/native diagnostic row sequence under four log policies."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_nvm_records[2560];
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void audio_dump_hex(const char*a,uint32_t b,const uint8_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_dump_row',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_dump.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for level in (0,1,2,4):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   base=syms['audio_ble_privacy_nvm_records'] if compiled else 0x7ff000
   row=bytearray(256);row[:6]=b'ABCDEF';row[6]=1;row[0x2e]=0xa;row[0x2f]=1;row[0x30]=1;row[0x31]=1;row[0x32]=1;row[0x4f]=1;row[0x6c:0x6e]=b'\x34\x12';row[0x98:0x9a]=b'\x78\x56';row[0xc3]=1
   u.mem_write(base+2*256,bytes(row))
   cuts={syms['audio_log_level']&~1:'level',syms['audio_log_extended']&~1:'ext',syms['compressed_log_output']&~1:'compact',syms['audio_dump_hex']&~1:'dump'} if compiled else {0x43d0ce:'level',0x43d574:'ext',0x43ce9e:'compact',0x43dacc:'dump'}
   events=[]
   def s(addr):
    return bytes(u.mem_read(addr,256)).split(b'\0')[0].decode('latin1')
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if not kind:return
    if kind=='level':uc.reg_write(UC_ARM_REG_R0,level)
    elif kind=='ext':
     sp=uc.reg_read(UC_ARM_REG_SP);line,msg=struct.unpack('<II',uc.mem_read(sp,8));events.append(('ext',uc.reg_read(UC_ARM_REG_R0),line,s(msg)))
    elif kind=='compact':events.append(('compact',uc.reg_read(UC_ARM_REG_R0),s(uc.reg_read(UC_ARM_REG_R1))))
    elif kind=='dump':events.append(('dump',s(uc.reg_read(UC_ARM_REG_R0)),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,0x20090000);u.reg_write(UC_ARM_REG_R1,2);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_privacy_dump_row'] if compiled else 0x4789b0)|1,0x600000,count=100000)
   observations.append(events)
  assert observations[0]==observations[1],(level,observations)
  print('PASS privacy dump log policy',level,len(observations[0]))
