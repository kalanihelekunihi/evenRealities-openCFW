#!/usr/bin/env python3
"""Compare stock/C public LittleFS sync wrapper with controlled children."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_lfs_sync_4cfb08.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-sync-4cfb08';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
native={'isopen':0x4cb082,'assert':0x4d09b4,'sync':0x4cdf74}
source={'isopen':'g2_lfs_mlist_isopen','assert':'g2_file_close_error','sync':'g2_lfs_file_sync'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t g2_lfs_mlist_isopen(void*a,void*b){(void)a;(void)b;return 0;}
void g2_file_close_error(const char*a,const char*b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t g2_lfs_file_sync(void*a,void*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_lfs_sync_4cfb08',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,filesystem,file,isopen,sync):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(filesystem+0x28,struct.pack('<I',0x20070040))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(160):
    c=cpu.mem_read(addr+i,1)[0]
    if c==0:break
    b.append(c)
   return bytes(b)
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   if k=='isopen':calls.append((k,r0,r1));ret=isopen
   elif k=='assert':calls.append((k,cstr(cpu,r0),cstr(cpu,r1),r2));ret=0
   else:calls.append((k,r0,r1));ret=sync
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,filesystem);u.reg_write(A.UC_ARM_REG_R1,file)
  entry=syms['audio_file_lfs_sync_4cfb08'] if compiled else 0x4cfb08
  u.emu_start(entry|1,0x600000,count=300)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for filesystem in (0x20071ac8,0x20072000):
  for file in (0x20070000,0x20073000):
   for isopen in (0,1):
    for sync in (-5,0,1,257):
     n=run(False,filesystem,file,isopen,sync);c=run(True,filesystem,file,isopen,sync)
     if n!=c:raise AssertionError((filesystem,file,isopen,sync,n,c))
     cases.append((filesystem,file,isopen,sync))
 row={'status':'PASS_BOUNDED_MAIN_FILE_LFS_SYNC_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'LittleFS open-list guard, diagnostic literal/line, core dispatch and return forwarding.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
