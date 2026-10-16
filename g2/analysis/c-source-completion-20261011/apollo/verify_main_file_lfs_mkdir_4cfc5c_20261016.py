#!/usr/bin/env python3
"""Compare stock/C LittleFS mkdir wrapper argument and return forwarding."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_lfs_mkdir_4cfc5c.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-mkdir-4cfc5c';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t audio_file_lfs_mkdir_core_4cd3aa(void*a,const char*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_lfs_mkdir_4cfc5c',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,ctx,path,ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(0x2007e000,b'/log/tp\0')
  core=syms['audio_file_lfs_mkdir_core_4cd3aa']&~1 if compiled else 0x4cd3aa;calls=[]
  def hook(cpu,pc,size,data):
   if pc!=core:return
   calls.append(tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)))
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,ctx);u.reg_write(A.UC_ARM_REG_R1,path)
  entry=syms['audio_file_lfs_mkdir_4cfc5c'] if compiled else 0x4cfc5c
  u.emu_start(entry|1,0x600000,count=100)
  value=u.reg_read(A.UC_ARM_REG_R0)
  if value&0x80000000:value-=0x100000000
  return value,calls
 cases=[]
 for ctx in (0,0x20071ac8):
  for path in (0,0x2007e000):
   for ret in (-17,-2,-5,0,1):
    n=run(False,ctx,path,ret);c=run(True,ctx,path,ret)
    if n!=c:raise AssertionError((ctx,path,ret,n,c))
    cases.append((ctx,path,ret))
 row={'status':'PASS_BOUNDED_MAIN_FILE_LFS_MKDIR_WRAPPER_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'filesystem/path pointers, zero flags and core return forwarding.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
