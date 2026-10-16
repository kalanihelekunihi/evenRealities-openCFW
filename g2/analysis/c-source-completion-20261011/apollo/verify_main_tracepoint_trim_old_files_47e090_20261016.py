#!/usr/bin/env python3
"""Compare stock/C tracepoint retention loop with controlled listing and removal."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_trim_old_files_47e090.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-trim-old-files-47e090';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t audio_tracepoint_list_files_47deb4(void*p){(void)p;return 0;}
void audio_tracepoint_format_pull_path_47de0a(char*p,uint32_t n,uint32_t s){(void)p;(void)n;(void)s;}
int32_t audio_tracepoint_storage_unlink_47498c(const char*p){(void)p;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_trim_old_files_47e090',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'list':0x47deb4,'format':0x47de0a,'remove':0x47498c}
 source={'list':'audio_tracepoint_list_files_47deb4','format':'audio_tracepoint_format_pull_path_47de0a','remove':'audio_tracepoint_storage_unlink_47498c'}
 def run(compiled,plan,sequence,remove_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[];index=0
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   nonlocal index
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   value=0
   if k=='list':
    if index>=len(plan):raise AssertionError(('list overrun',compiled,plan))
    count,status=plan[index];index+=1;calls.append(('list',count,status))
    cpu.mem_write(r[0],count.to_bytes(4,'little',signed=True)+sequence.to_bytes(4,'little'));value=status
   elif k=='format':
    calls.append(('format',r[1],r[2]));cpu.mem_write(r[0],b'/log/tp/tp_42.bin\0')
   else:calls.append(('remove',cstr(cpu,r[0])));value=remove_ret
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_trim_old_files_47e090'] if compiled else 0x47e090
  u.emu_start(entry|1,0x600000,count=1000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,calls,index
 cases=[]
 plans=[([(0,-8)],0), ([(0,0)],0), ([(3,0)],0), ([(4,0)],-6),
        ([(4,0),(3,0)],0), ([(5,0),(4,0),(3,0)],0), ([(4,0),(0,-9)],0)]
 for plan,remove_ret in plans:
  for sequence in (0,1,42):
   n=run(False,plan,sequence,remove_ret);c=run(True,plan,sequence,remove_ret)
   if n!=c:raise AssertionError((plan,remove_ret,sequence,n,c))
   cases.append((plan,remove_ret,sequence))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_TRIM_OLD_FILES_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'listing error, below-four exit, deletion failure, repeated removal and next-list failure under controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
