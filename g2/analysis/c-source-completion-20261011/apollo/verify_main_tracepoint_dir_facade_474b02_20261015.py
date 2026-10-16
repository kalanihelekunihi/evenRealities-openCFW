#!/usr/bin/env python3
"""Compare stock/C file-directory open, read and close facades."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_dir_facade_474b02.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-dir-facade-474b02';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_file_ready_200746a8;uint8_t audio_file_lfs_context[128];void *audio_file_api_mutex;
int32_t *audio_file_errno_location_439cc4(void){return 0;}
void *codec_allocate(uint32_t a){(void)a;return 0;}
void audio_file_heap_free(void*a){(void)a;}
void *audio_settings_copy_text(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
int32_t audio_file_lfs_dir_open_4cfc66(void*a,void*b,const char*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_file_lfs_dir_read_4cfd02(void*a,void*b,void*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_file_lfs_dir_close_4cfcf8(void*a,void*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_dir_open_474b02',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'errno':0x439cc4,'alloc':0x474cd2,'free':0x474d16,'copy':0x44b5a0,
         'acquire':0x4497b6,'release':0x44981c,'open':0x4cfc66,'read':0x4cfd02,'close':0x4cfcf8}
 source={'errno':'audio_file_errno_location_439cc4','alloc':'codec_allocate','free':'audio_file_heap_free',
         'copy':'audio_settings_copy_text','acquire':'audio_file_mutex_acquire','release':'audio_file_mutex_release',
         'open':'audio_file_lfs_dir_open_4cfc66','read':'audio_file_lfs_dir_read_4cfd02','close':'audio_file_lfs_dir_close_4cfcf8'}
 def run(compiled,which,ready,present=True,allocated=True,locked=True,lfs_result=0,entry_type=1):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  dir=0x20071000;path=0x20072000 if present else 0;mutex=0x20073000;errno=0x20074000
  context=syms['audio_file_lfs_context'] if compiled else 0x20071ac8
  ready_addr=syms['audio_file_ready_200746a8'] if compiled else 0x200746a8
  mutex_addr=syms['audio_file_api_mutex'] if compiled else 0x200748f4
  result_addr=syms['audio_tracepoint_dir_result_200701e8'] if compiled else 0x200701e8
  u.mem_write(ready_addr,ready.to_bytes(4,'little'));u.mem_write(mutex_addr,mutex.to_bytes(4,'little'))
  u.mem_write(errno,(99).to_bytes(4,'little'));u.mem_write(dir,b'\xa5'*0x240);u.mem_write(result_addr,b'\xa5'*0x101)
  u.mem_write(dir,context.to_bytes(4,'little'))
  if path:u.mem_write(path,b'/log/tp\0')
  calls=[];hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()}
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   value=0
   if k=='errno':value=errno
   elif k=='alloc':calls.append(('alloc',r0));value=dir if allocated else 0
   elif k=='free':calls.append(('free',r0==dir))
   elif k=='copy':
    calls.append(('copy',r2));data=bytes(cpu.mem_read(r1,r2)).split(b'\0')[0]
    cpu.mem_write(r0,data[:r2]+b'\0'*(r2-len(data[:r2])));value=r0
   elif k=='acquire':calls.append(('acquire',r0==mutex,r1));value=0 if locked else 1
   elif k=='release':calls.append(('release',r0==mutex));value=0
   elif k=='open':calls.append(('open',r0==context,r1==dir+4,r2==path));value=lfs_result
   elif k=='read':
    calls.append(('read',r0==context,r1==dir+4,r2==dir+0x38));value=lfs_result
    cpu.mem_write(dir+0x38,bytes((entry_type,)))
    cpu.mem_write(dir+0x40,b'tp_1.bin\0')
   elif k=='close':calls.append(('close',r0==context,r1==dir+4));value=lfs_result
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,path if which=='open' else (dir if present else 0))
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=(syms['audio_tracepoint_dir_'+which+'_474'+{'open':'b02','read':'bb8','close':'c66'}[which]] if compiled else {'open':0x474b02,'read':0x474bb8,'close':0x474c66}[which])
  u.emu_start(entry|1,0x600000,count=20000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if which=='open':result=(result==dir)
  elif which=='read':result=(result==result_addr)
  elif result&0x80000000:result-=0x100000000
  memory=bytes(u.mem_read(result_addr,0x101)).hex() if which=='read' else ''
  dir_memory=bytes(u.mem_read(dir+4,0x23c)).hex() if which=='open' and result else ''
  return result,int.from_bytes(u.mem_read(errno,4),'little'),memory,dir_memory,calls
 cases=[]
 for which in ('open','read','close'):
  for ready in (0,1):
   for present in (False,True):
    for locked in (False,True):
     for lfs_result in (-5,-2,0,1):
      for entry_type in ((1,2,3) if which=='read' else (1,)):
       n=run(False,which,ready,present,True,locked,lfs_result,entry_type)
       c=run(True,which,ready,present,True,locked,lfs_result,entry_type)
       if n!=c:raise AssertionError((which,ready,present,locked,lfs_result,entry_type,n,c))
       cases.append((which,ready,present,locked,lfs_result,entry_type))
 for allocated in (False,True):
  n=run(False,'open',1,True,allocated);c=run(True,'open',1,True,allocated)
  if n!=c:raise AssertionError(('alloc',allocated,n,c))
  cases.append(('alloc',allocated))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_DIR_FACADE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Directory open/read/close readiness, arguments, mutex, LittleFS status, errno and shared result at controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
