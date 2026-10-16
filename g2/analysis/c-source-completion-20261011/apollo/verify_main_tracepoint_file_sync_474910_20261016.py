#!/usr/bin/env python3
"""Compare stock 0x474910 stream sync facade with compiled C."""
import hashlib, json, struct, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_sync_474910.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-sync-474910';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
native={'acquire':0x4497b6,'release':0x44981c,'sync':0x4cfb08,'errno':0x439cc4}
source={'acquire':'audio_file_mutex_acquire','release':'audio_file_mutex_release',
        'sync':'audio_file_lfs_sync_4cfb08','errno':'audio_file_errno_location_439cc4'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_file_api_mutex;
int32_t audio_file_mutex_acquire(void *a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void *a){(void)a;return 0;}
int32_t audio_file_lfs_sync_4cfb08(void *a,void *b){(void)a;(void)b;return 0;}
int32_t *audio_file_errno_location_439cc4(void){return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_file_close_474910',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,handle,acquire,sync):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(0x20070000,struct.pack('<I',0x20071ac8)+b'\0'*92)
  u.mem_write(0x20075000,struct.pack('<I',0x12345678))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1))
   if k=='acquire':calls.append((k,r1));ret=acquire
   elif k=='release':calls.append((k,));ret=0
   elif k=='sync':calls.append((k,r0,r1));ret=sync
   else:calls.append((k,));ret=0x20075000
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,handle)
  entry=syms['audio_tracepoint_file_close_474910'] if compiled else 0x474910
  u.emu_start(entry|1,0x600000,count=400)
  return u.reg_read(A.UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20075000,4))
 cases=[]
 for handle in (0,0x200043f8,0x20004440,0x200043b0,0x20070000):
  for acquire in (0,1):
   for sync in (-5,0,1):
    n=run(False,handle,acquire,sync);c=run(True,handle,acquire,sync)
    if n!=c:raise AssertionError((handle,acquire,sync,n,c))
    cases.append((handle,acquire,sync))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FILE_SYNC_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'special/null stream, mutex, LittleFS sync, errno and return paths; legacy caller name says close.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
