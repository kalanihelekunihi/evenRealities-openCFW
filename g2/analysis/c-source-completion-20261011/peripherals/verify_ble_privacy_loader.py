"""Compiled-C/native NVM privacy row loader: empty, invalid and valid records."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_nvm_records[2560];uint32_t audio_log_level(void){return 0;}
void audio_log_extended(void){}uint32_t compressed_log_output(void){return 0;}
void audio_ble_privacy_cache_maintenance(const void *p,uint8_t v){(void)p;(void)v;}
void *audio_queue_copy_bytes(void *d,const void*s,uint32_t n){(void)s;(void)n;return d;}
uint32_t audio_ble_privacy_rewrite_record(uint8_t *p){(void)p;return 0;}
void audio_dump_hex(const char *s,uint32_t w,const uint8_t*d,uint32_t n){(void)s;(void)w;(void)d;(void)n;}
void __aeabi_memclr(void *p,unsigned n){volatile unsigned char *b=p;for(unsigned i=0;i<n;i++)b[i]=0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_load_rows',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_loader.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for case,policy in (('empty',0),('invalid',0),('valid',0),('two',0),('valid',1),('valid',2),('valid',4)):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);nvm=syms['audio_ble_privacy_nvm_records'] if c else 0x7ff000
   dest=0x20080000;u.mem_write(dest,b'\xaa'*2000)
   u.mem_write(nvm,b'\x00'*2560)
   rows=2 if case=='two' else (0 if case=='empty' else 1)
   for idx in range(rows):
    row=nvm+idx*256;u.mem_write(row,struct.pack('<I',idx+1))
    u.mem_write(row+0x30,b'\x01' if case!='invalid' else b'\x00')
    u.mem_write(row+7,b'\x03'+b'\x00'*15)
   if not c:u.mem_write(0x20004543,bytes([policy]))
   cuts={syms['audio_ble_privacy_cache_maintenance']&~1:'cache',syms['audio_queue_copy_bytes']&~1:'copy',syms['audio_ble_privacy_rewrite_record']&~1:'rewrite',syms['audio_dump_hex']&~1:'dump',syms['audio_log_level']&~1:'policy',syms['audio_log_extended']&~1:'extended',syms['compressed_log_output']&~1:'compact'} if c else {0x475014:'cache',0x439be4:'copy',0x479b74:'rewrite',0x43dacc:'dump',0x43d574:'extended',0x43ce9e:'compact'}
   calls=[]
   def cstr(uc,a):
    out=bytearray()
    for _ in range(256):
     ch=uc.mem_read(a,1)[0]
     if ch==0:break
     out.append(ch);a+=1
    return bytes(out)
   def hook(uc,a,size,_):
    if a in cuts:
     kind=cuts[a]
     if kind=='copy':
      dst,src,n=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
      uc.mem_write(dst,bytes(uc.mem_read(src,n)))
      calls.append((kind,src-nvm if nvm<=src<nvm+2560 else 'stack',n))
      uc.reg_write(UC_ARM_REG_R0,dst)
     elif kind=='rewrite':calls.append((kind,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),200))[0x2e]))
     elif kind=='dump':calls.append((kind,uc.reg_read(UC_ARM_REG_R2)-dest,uc.reg_read(UC_ARM_REG_R3)))
     elif kind=='policy':uc.reg_write(UC_ARM_REG_R0,policy)
     elif kind=='extended':
      sp=uc.reg_read(UC_ARM_REG_SP);line,msg=struct.unpack('<II',uc.mem_read(sp,8))
      calls.append((kind,uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),cstr(uc,uc.reg_read(UC_ARM_REG_R2)),cstr(uc,uc.reg_read(UC_ARM_REG_R3)),line,cstr(uc,msg)))
     elif kind=='compact':calls.append((kind,uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),cstr(uc,uc.reg_read(UC_ARM_REG_R2))))
     else:calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,dest);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_privacy_load_rows'] if c else 0x4795dc)|1,0x600000,count=50000)
   obs.append((bytes(u.mem_read(dest,2000)),calls))
  assert obs[0]==obs[1],(case,policy,[(x[1],x[0][:64]) for x in obs])
  print('PASS privacy loader',case,'policy',policy)
