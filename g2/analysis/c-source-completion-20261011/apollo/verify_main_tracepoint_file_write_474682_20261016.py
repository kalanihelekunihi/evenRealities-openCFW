#!/usr/bin/env python3
"""Compare stock/C redirect fwrite with native logging and LittleFS cuts."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_write_474682.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-write-474682';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
native={'flags':0x43d0ce,'extended':0x43d574,'compressed':0x43ce9e,
        'acquire':0x4497b6,'release':0x44981c,'write':0x4cfb7c}
source={'flags':'audio_log_flags','extended':'audio_log_extended','compressed':'compressed_log_output',
        'acquire':'audio_file_mutex_acquire','release':'audio_file_mutex_release','write':'audio_file_lfs_write_4cfb7c'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_file_api_mutex;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
int32_t audio_file_lfs_write_4cfb7c(void*a,void*b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_file_write_474682',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,mask,size,count,stream,acquire,written):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(0x20070000,struct.pack('<I',0x20071ac8)+b'\0'*92)
  u.mem_write(0x20071000,bytes(range(64)))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(160):
    c=cpu.mem_read(addr+i,1)[0]
    if c==0:break
    b.append(c)
   return bytes(b)
  def hook(cpu,pc,width,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   stack=struct.unpack('<IIII',bytes(cpu.mem_read(sp,16)))
   if k=='flags':calls.append((k,));ret=mask
   elif k=='extended':
    args=stack[2:4] if stack[0] in (0x24a,0x24e) else stack[2:3] if stack[0]==0x23c else ()
    calls.append((k,r0,cstr(cpu,r1),cstr(cpu,r2),cstr(cpu,r3),stack[0],cstr(cpu,stack[1]),args))
    ret=0
   elif k=='compressed':
    args=(r3,stack[0]) if r0 in (0x04800000,0x08800000) else (r3,) if r0==0x04400000 else ()
    calls.append((k,r0,cstr(cpu,r1),cstr(cpu,r2),args));ret=0
   elif k=='acquire':calls.append((k,r1));ret=acquire
   elif k=='release':calls.append((k,));ret=0
   else:calls.append((k,r0,r1,r2,r3));ret=written
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,val in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),
                     (0x20071000,size,count,stream)):u.reg_write(reg,val)
  entry=syms['audio_tracepoint_file_write_474682'] if compiled else 0x474682
  u.emu_start(entry|1,0x600000,count=2000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for mask in (0,1,2,4,7):
  for size,count in ((1,8),(2,4),(4,3)):
   bytes_=size*count
   for stream,acquire,written in ((0,0,0),(0x20070000,1,0),
                                   (0x20070000,0,-5),(0x20070000,0,bytes_-1),
                                   (0x20070000,0,bytes_)):
    n=run(False,mask,size,count,stream,acquire,written)
    c=run(True,mask,size,count,stream,acquire,written)
    if n!=c:raise AssertionError((mask,size,count,stream,acquire,written,n,c))
    cases.append((mask,size,count,stream,acquire,written))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FILE_WRITE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'redirect fwrite null, mutex, error, short/full write and all logging masks 0,1,2,4,7.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
