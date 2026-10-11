"""Bounded native/compiled-C privacy record update with genuine children cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_nvm_records[2560];
void audio_ble_privacy_cache_maintenance(const void*a,uint8_t b){(void)a;(void)b;}
void audio_ble_privacy_nvm_write_record(const uint8_t*a,uint8_t b){(void)a;(void)b;}
void audio_ble_privacy_dump_row(uint8_t*a,uint8_t b){(void)a;(void)b;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_rewrite_record',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_rewrite.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_compare.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for case,policy in ([(x,0) for x in ('existing','empty','invalid_unused','invalid_used','role_lru','no_candidate')]+[('existing',2),('empty',1),('role_lru',4)]):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   base=syms['audio_ble_privacy_nvm_records'] if compiled else 0x7ff000
   record=bytearray(256);record[:6]=b'NEWORD';record[0xc3]=1;record[0xc4:0xc8]=struct.pack('<I',99)
   u.mem_write(0x20090000,bytes(record))
   for i in range(10):
    row=bytearray(256);row[:6]=b'OLD%03d'%i;row[0x2f]=1;row[0x30]=1;row[0xc3]=i&1;row[0xc4:0xc8]=struct.pack('<I',i+5)
    if case=='existing' and i==2:row[:6]=record[:6]
    if case=='empty' and i==3:row[:6]=b'\0'*6
    if case=='invalid_unused' and i==4:row[0x2f]=0;row[0x30]=0
    if case=='invalid_used' and i==5:row[0x30]=0
    if case=='no_candidate':row[0x2f]=0;row[0x30]=1
    u.mem_write(base+i*256,bytes(row))
   cuts={syms['audio_log_level']&~1:'level',syms['audio_log_extended']&~1:'ext',syms['compressed_log_output']&~1:'compact',syms['audio_ble_privacy_cache_maintenance']&~1:'cache',syms['audio_ble_privacy_compare_address']&~1:'compare',syms['audio_ble_privacy_nvm_write_record']&~1:'write',syms['audio_ble_privacy_dump_row']&~1:'dump'} if compiled else {0x43d0ce:'level',0x43d574:'ext',0x43ce9e:'compact',0x475014:'cache',0x4d294a:'compare',0x4799a8:'write',0x4789b0:'dump'}
   calls=[]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if not kind:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if kind=='level':uc.reg_write(UC_ARM_REG_R0,policy)
    elif kind=='ext':
     sp=uc.reg_read(UC_ARM_REG_SP);line,msg=struct.unpack('<II',uc.mem_read(sp,8));calls.append(('ext',r0,line,bytes(uc.mem_read(msg,200)).split(b'\0')[0]))
    elif kind=='compact':calls.append(('compact',r0,bytes(uc.mem_read(r1,200)).split(b'\0')[0]))
    elif kind=='cache':calls.append(('cache',))
    elif kind=='compare':
     uc.reg_write(UC_ARM_REG_R0,int(uc.mem_read(r0,6)==uc.mem_read(r1,6)))
    elif kind=='write':
     calls.append(('write',r1&0xff))
     uc.mem_write(base+(r1&0xff)*256,bytes(uc.mem_read(r0,200)))
    elif kind=='dump':calls.append(('dump',r1&0xff))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,0x20090000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_privacy_rewrite_record'] if compiled else 0x479b74)|1,0x600000,count=120000)
   observations.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert observations[0]==observations[1],(case,policy,observations)
  print('PASS privacy rewrite',case,policy)
