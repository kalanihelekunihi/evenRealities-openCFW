#!/usr/bin/env python3
"""Compare stock file-size helper to existing C size facade through a wrapper."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_size_47de7a.c'
PROVIDER=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_size_5edb68.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-size-47de7a';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_file_open(const char*a,const char*b){(void)a;(void)b;return 0;}
int32_t audio_file_seek(void*a,int32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_file_tell(void*a){(void)a;return 0;}
int32_t audio_file_close(void*a){(void)a;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_file_size_47de7a',str(SOURCE),str(PROVIDER),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'open':0x474550,'seek':0x474814,'tell':0x474870,'close':0x4745f4}
 source={'open':'audio_file_open','seek':'audio_file_seek','tell':'audio_file_tell','close':'audio_file_close'}
 def run(compiled,open_ok,seek_ret,tell_ret,path):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  paddr=0x2007e000;u.mem_write(paddr,path.encode()+b'\0')
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
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   value=0
   if k=='open':calls.append(('open',cstr(cpu,r[0]),cstr(cpu,r[1])));value=0x20078000 if open_ok else 0
   elif k=='seek':calls.append(('seek',r[0],r[1],r[2]));value=seek_ret
   elif k=='tell':calls.append(('tell',r[0]));value=tell_ret
   else:calls.append(('close',r[0]))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,paddr)
  entry=syms['audio_tracepoint_file_size_47de7a'] if compiled else 0x47de7a
  u.emu_start(entry|1,0x600000,count=1000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for path in ('/log/tp/tp_1.bin','/log/tp/state.bin'):
  for open_ok in (False,True):
   for seek_ret in (-1,0):
    for tell_ret in (-1,0,1,12345):
     n=run(False,open_ok,seek_ret,tell_ret,path)
     c=run(True,open_ok,seek_ret,tell_ret,path)
     if n!=c:raise AssertionError((path,open_ok,seek_ret,tell_ret,n,c))
     cases.append((path,open_ok,seek_ret,tell_ret))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FILE_SIZE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'provider':str(PROVIDER.relative_to(ROOT)),'provider_sha256':hashlib.sha256(PROVIDER.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'read-only open, seek-to-end, tell, close and positive-size result through existing C file-size facade.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
