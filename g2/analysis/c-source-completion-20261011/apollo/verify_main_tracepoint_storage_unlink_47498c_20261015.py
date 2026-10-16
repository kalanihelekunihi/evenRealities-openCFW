#!/usr/bin/env python3
"""Compare stock file unlink facade branches against bounded C source."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_storage_unlink_47498c.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-storage-unlink-47498c';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_file_api_mutex;
uint8_t audio_file_lfs_context[128];
int32_t *audio_file_errno_location_439cc4(void){return 0;}
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
int32_t audio_file_lfs_remove_4cfa76(void*a,const char*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_storage_unlink_47498c',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'errno':0x439cc4,'acquire':0x4497b6,'release':0x44981c,'remove':0x4cfa76}
 source={'errno':'audio_file_errno_location_439cc4','acquire':'audio_file_mutex_acquire','release':'audio_file_mutex_release','remove':'audio_file_lfs_remove_4cfa76'}
 def run(compiled,ready,present,acquire_ret,remove_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  readyaddr=syms['audio_file_ready_200746a8'] if compiled else 0x200746a8
  mutexaddr=syms['audio_file_api_mutex'] if compiled else 0x200748f4
  context=syms['audio_file_lfs_context'] if compiled else 0x20071ac8
  mutex=0x20072000;errno=0x20072100;path=0x20073000 if present else 0
  u.mem_write(readyaddr,ready.to_bytes(4,'little'));u.mem_write(mutexaddr,mutex.to_bytes(4,'little'));u.mem_write(errno,(99).to_bytes(4,'little'))
  if path:u.mem_write(path,b'/log/tp/tp_1.bin\0')
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
  def string(a):return bytes(u.mem_read(a,80)).split(b'\0')[0].decode('ascii')
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1))
   if k=='errno':calls.append(('errno',));cpu.reg_write(A.UC_ARM_REG_R0,errno)
   elif k=='acquire':calls.append(('acquire',r0==mutex,r1));cpu.reg_write(A.UC_ARM_REG_R0,acquire_ret)
   elif k=='release':calls.append(('release',r0==mutex));cpu.reg_write(A.UC_ARM_REG_R0,7)
   else:calls.append(('remove',r0==context,string(r1)));cpu.reg_write(A.UC_ARM_REG_R0,remove_ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,path);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_storage_unlink_47498c'] if compiled else 0x47498c
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),int.from_bytes(u.mem_read(errno,4),'little'),calls
 cases=[]
 for ready in (0,1,2):
  for present in (False,True):
   for acquire_ret in (0,1,-1):
    for remove_ret in (0,-2,-5,1):
     n=run(False,ready,present,acquire_ret,remove_ret)
     c=run(True,ready,present,acquire_ret,remove_ret)
     if n!=c:raise AssertionError((ready,present,acquire_ret,remove_ret,n,c))
     cases.append((ready,present,acquire_ret,remove_ret))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_UNLINK_FACADE_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Mutex and LittleFS remove providers are simulated at call boundaries; actual NOR filesystem behavior unproved.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
