#!/usr/bin/env python3
"""Compare stock/C tracepoint path formatter argument forwarding."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_format_pull_path_47de0a.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-format-pull-path-47de0a';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t g2_audio_dump_snprintf(char*a,uint32_t b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_format_pull_path_47de0a',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,capacity,seq):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);dst=0x2007e000;u.mem_write(dst,b'Z'*64)
  snprintf=syms['g2_audio_dump_snprintf']&~1 if compiled else 0x44b728;calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   if pc!=snprintf:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   calls.append((r[0]==dst,r[1],cstr(cpu,r[2]),r[3]))
   value=b'/log/tp/tp_'+str(r[3]).encode()+b'.bin'
   if r[1]:cpu.mem_write(dst,(value[:r[1]-1]+b'\x00')[:r[1]])
   cpu.reg_write(A.UC_ARM_REG_R0,len(value))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,val in [(A.UC_ARM_REG_R0,dst),(A.UC_ARM_REG_R1,capacity),(A.UC_ARM_REG_R2,seq)]:u.reg_write(reg,val)
  entry=syms['audio_tracepoint_format_pull_path_47de0a'] if compiled else 0x47de0a
  u.emu_start(entry|1,0x600000,count=100)
  return calls,bytes(u.mem_read(dst,64))
 cases=[]
 for capacity in (0,1,8,64):
  for seq in (0,1,17,0xffffffff):
   n=run(False,capacity,seq);c=run(True,capacity,seq)
   if n!=c:raise AssertionError((capacity,seq,n,c))
   cases.append((capacity,seq))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FORMAT_PULL_PATH_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'snprintf destination, capacity, literal, sequence forwarding and bounded buffer under controlled formatter.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
