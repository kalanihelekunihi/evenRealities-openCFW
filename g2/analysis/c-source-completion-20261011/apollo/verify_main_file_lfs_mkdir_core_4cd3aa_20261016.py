#!/usr/bin/env python3
"""Compare stock/C LittleFS mkdir core through typed child cuts."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_lfs_mkdir_core_4cd3aa.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-mkdir-core-4cd3aa';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
native={'force':0x4cf9e0,'find':0x4cc04a,'last':0x4cad80,'nlen':0x4cad76,
        'checkpoint':0x4cb0e0,'alloc':0x4cc502,'fetch':0x4cbedc,'commit':0x4cd388,
        'orphan':0x4cf570}
source={'force':'audio_file_lfs_forceconsistency','find':'audio_file_lfs_dir_find',
        'last':'audio_file_lfs_path_islast','nlen':'audio_file_lfs_path_namelen',
        'checkpoint':'g2_lfs_alloc_checkpoint','alloc':'g2_lfs_dir_alloc',
        'fetch':'g2_lfs_dir_fetch','commit':'g2_lfs_dir_commit','orphan':'g2_lfs_fs_preporphans'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t audio_file_lfs_forceconsistency(void*a){(void)a;return 0;}
int32_t audio_file_lfs_dir_find(void*a,void*b,const char**c,uint16_t*d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_lfs_path_islast(const char*a){(void)a;return 0;}
uint32_t audio_file_lfs_path_namelen(const char*a){(void)a;return 0;}
void g2_lfs_alloc_checkpoint(void*a){(void)a;}
int32_t g2_lfs_dir_alloc(void*a,void*b){(void)a;(void)b;return 0;}
int32_t g2_lfs_dir_fetch(void*a,void*b,const uint32_t*c){(void)a;(void)b;(void)c;return 0;}
int32_t g2_lfs_dir_commit(void*a,void*b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t g2_lfs_fs_preporphans(void*a,int8_t b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_lfs_mkdir_core_4cd3aa',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,scenario):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  fs=0x20071000;path=0x2007e000
  u.mem_write(fs+0x28,struct.pack('<I',0x20075000))
  u.mem_write(fs+0x70,struct.pack('<I',16))
  u.mem_write(path,b'trace\0')
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  commits=0;orphans=0
  def read32(cpu,a):return struct.unpack('<I',bytes(cpu.mem_read(a,4)))[0]
  def write32(cpu,a,v):cpu.mem_write(a,struct.pack('<I',v&0xffffffff))
  def cstr(cpu,a):
   b=bytearray()
   for i in range(80):
    c=cpu.mem_read(a+i,1)[0]
    if c==0:break
    b.append(c)
   return bytes(b)
  def hook(cpu,pc,width,data):
   nonlocal commits,orphans
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   if k=='force':calls.append((k,r0));ret=scenario.get('force',0)
   elif k=='find':
    calls.append((k,r0,cstr(cpu,read32(cpu,r2))))
    cpu.mem_write(r1,struct.pack('<IIIIIHBBII',11,12,1,4,0xffff,1,0,scenario.get('split',0),21,22))
    write32(cpu,r2,path);cpu.mem_write(r3,struct.pack('<H',3))
    ret=scenario.get('find',-2)
   elif k=='last':calls.append((k,cstr(cpu,r0)));ret=scenario.get('last',1)
   elif k=='nlen':calls.append((k,cstr(cpu,r0)));ret=scenario.get('nlen',5)
   elif k=='checkpoint':calls.append((k,r0));ret=0
   elif k=='alloc':
    calls.append((k,r0))
    cpu.mem_write(r1,struct.pack('<IIIIIHBBII',31,32,2,4,0xffff,0,0,0,41,42))
    ret=scenario.get('alloc',0)
   elif k=='fetch':
    calls.append((k,r0,tuple(struct.unpack('<II',bytes(cpu.mem_read(r2,8))))))
    cpu.mem_write(r1+23,b'\0')
    ret=scenario.get('fetch',0)
   elif k=='orphan':
    orphans+=1;direction=r1 if r1<0x80000000 else r1-0x100000000
    calls.append((k,r0,direction));ret=scenario.get('orphan'+str(orphans),0)
   else:
    commits+=1;attrs=[]
    for i in range(r3):
     tag,ptr=struct.unpack('<II',bytes(cpu.mem_read(r2+8*i,8)))
     if ptr==0:payload=None
     elif (tag&0x7ff00000)==0x00200000:payload=cstr(cpu,ptr)
     else:payload=tuple(struct.unpack('<II',bytes(cpu.mem_read(ptr,8))))
     attrs.append((tag,payload))
    calls.append((k,r0,r3,tuple(attrs)))
    ret=scenario.get('commit'+str(commits),0)
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,fs);u.reg_write(A.UC_ARM_REG_R1,path);u.reg_write(A.UC_ARM_REG_R2,0)
  entry=syms['audio_file_lfs_mkdir_core_4cd3aa'] if compiled else 0x4cd3aa
  u.emu_start(entry|1,0x600000,count=2500)
  return u.reg_read(A.UC_ARM_REG_R0),calls,read32(u,fs+0x28)
 scenarios=[{'force':-5},{'find':-21},{'find':0},{'last':0},{'nlen':17},
            {'alloc':-28},{'split':0,'commit1':-5},{'split':0,'commit2':-5},
            {'split':0},{'split':1,'fetch':-5},{'split':1,'orphan1':-5},
            {'split':1,'commit1':-5},{'split':1,'commit2':-5},
            {'split':1,'orphan2':-5},{'split':1,'commit3':-5},{'split':1}]
 cases=[]
 for scenario in scenarios:
  n=run(False,scenario);c=run(True,scenario)
  if n!=c:raise AssertionError((scenario,n,c))
  cases.append(scenario)
 row={'status':'PASS_BOUNDED_MAIN_FILE_LFS_MKDIR_CORE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'force, find, path, allocation, split-list, directory commits, orphans and return paths.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
