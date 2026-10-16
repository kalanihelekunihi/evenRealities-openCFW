#!/usr/bin/env python3
"""Compare native/C tracepoint file-size facade with controlled file API."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_size_5edb68.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-size-5edb68';OUT.mkdir(parents=True,exist_ok=True)
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_file_size_5edb68',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'open':0x474550,'seek':0x474814,'tell':0x474870,'close':0x4745f4}
 source={k:{'open':'audio_file_open','seek':'audio_file_seek','tell':'audio_file_tell','close':'audio_file_close'}[k] for k in native}
 def run(compiled,opened,seek_ret,tell_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  path=0x20071000;file=0x20072000;u.mem_write(path,b'/log/tp/tp_1.bin\0');calls=[]
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()}
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   if k=='open':calls.append(('open',r0==path,bytes(cpu.mem_read(r1,3)).split(b'\0')[0].decode()));value=file if opened else 0
   elif k=='seek':calls.append(('seek',r0==file,r1,r2));value=seek_ret
   elif k=='tell':calls.append(('tell',r0==file));value=tell_ret
   else:calls.append(('close',r0==file));value=0
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,path);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_file_size_5edb68'] if compiled else 0x5edb68
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for opened in (False,True):
  for seek_ret in (-1,0,1):
   for tell_ret in (-1,0,1,42,0x7fffffff):
    n=run(False,opened,seek_ret,tell_ret);c=run(True,opened,seek_ret,tell_ret)
    if n!=c:raise AssertionError((opened,seek_ret,tell_ret,n,c))
    cases.append((opened,seek_ret,tell_ret))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FILE_SIZE_NATIVE_C','source':str(SOURCE.relative_to(ROOT)),
      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,
      'native_c_cases':len(cases),'scope':'Open/seek/tell/close arguments and positive-size clamp with controlled file API.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
