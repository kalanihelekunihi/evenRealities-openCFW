#!/usr/bin/env python3
"""Compare stock/C guarded directory creation over controlled LittleFS results."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_storage_mkdir_474a76.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-storage-mkdir-474a76';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_file_ready_200746a8;
int32_t errno_cell;
int32_t *audio_file_errno_location_439cc4(void){return &errno_cell;}
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
int32_t audio_file_lfs_mkdir_4cfc5c(void*a,const char*b){(void)a;(void)b;return 0;}
void *audio_file_api_mutex;
uint8_t audio_file_lfs_context[16];
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_storage_mkdir_474a76',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'errno':0x439cc4,'acquire':0x4497b6,'release':0x44981c,'mkdir':0x4cfc5c}
 source={'errno':'audio_file_errno_location_439cc4','acquire':'audio_file_mutex_acquire',
         'release':'audio_file_mutex_release','mkdir':'audio_file_lfs_mkdir_4cfc5c'}
 def run(compiled,ready,path_present,acquire_ret,lfs_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  ready_cell=syms['audio_file_ready_200746a8'] if compiled else 0x200746a8
  mutex_cell=syms['audio_file_api_mutex'] if compiled else 0x200748f4
  context=syms['audio_file_lfs_context'] if compiled else 0x20071ac8
  errno=syms['errno_cell'] if compiled else 0x2007e000
  u.mem_write(ready_cell,ready.to_bytes(4,'little'))
  u.mem_write(mutex_cell,(0x20079000).to_bytes(4,'little'))
  u.mem_write(errno,(99).to_bytes(4,'little'))
  path=0x2007d000;u.mem_write(path,b'/log/tp\0')
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1))
   value=0
   if k=='errno':calls.append(('errno',));value=errno
   elif k=='acquire':calls.append(('acquire',r0==0x20079000,r1));value=acquire_ret
   elif k=='release':calls.append(('release',r0==0x20079000))
   else:calls.append(('mkdir',r0==context,cstr(cpu,r1)));value=lfs_ret
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,path if path_present else 0);u.reg_write(A.UC_ARM_REG_R1,0)
  entry=syms['audio_tracepoint_storage_mkdir_474a76'] if compiled else 0x474a76
  u.emu_start(entry|1,0x600000,count=1000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,int.from_bytes(u.mem_read(errno,4),'little'),calls
 cases=[]
 for ready in (0,1,2):
  for path_present in (False,True):
   for acquire_ret in (-1,0):
    for lfs_ret in (-17,-2,-5,0,1):
     args=(ready,path_present,acquire_ret,lfs_ret)
     n=run(False,*args);c=run(True,*args)
     if n!=c:raise AssertionError((args,n,c))
     cases.append(args)
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_STORAGE_MKDIR_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'file-ready gate, null path, mutex, LittleFS result and errno mapping under controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
