#!/usr/bin/env python3
"""Compare stock/C pending tracepoint reopen with controlled path/open providers."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_reopen_pending_file_47e144.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-reopen-pending-file-47e144';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_tracepoint_pull_pending_20074ad8[2];
void *audio_tracepoint_active_file_handle;
void audio_tracepoint_format_pull_path_47de0a(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_tracepoint_file_open_474550(const char*a,const char*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_reopen_pending_file_47e144',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,seq,open_ok):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  pending=syms['audio_tracepoint_pull_pending_20074ad8'] if compiled else 0x20074ad8
  active=syms['audio_tracepoint_active_file_handle'] if compiled else 0x20074ae0
  u.mem_write(pending,seq.to_bytes(4,'little')+(27).to_bytes(4,'little'))
  u.mem_write(active,(0).to_bytes(4,'little'))
  fmt=syms['audio_tracepoint_format_pull_path_47de0a']&~1 if compiled else 0x47de0a
  fopen=syms['audio_tracepoint_file_open_474550']&~1 if compiled else 0x474550
  calls=[];path_ptr=0
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   nonlocal path_ptr
   if pc not in (fmt,fopen):return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   value=0
   if pc==fmt:
    path_ptr=r0;calls.append(('format',r1,r2));cpu.mem_write(r0,b'/log/tp/file.bin\x00')
   else:
    calls.append(('open',cstr(cpu,r0),cstr(cpu,r1),r0==path_ptr))
    value=0x20078000 if open_ok else 0
   cpu.reg_write(A.UC_ARM_REG_R0,value)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_reopen_pending_file_47e144'] if compiled else 0x47e144
  u.emu_start(entry|1,0x600000,count=200)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,int.from_bytes(u.mem_read(active,4),'little'),calls
 cases=[]
 for seq in (0,1,17,0xffffffff):
  for open_ok in (False,True):
   n=run(False,seq,open_ok);c=run(True,seq,open_ok)
   if n!=c:raise AssertionError((seq,open_ok,n,c))
   cases.append((seq,open_ok))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_REOPEN_PENDING_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'64-byte path buffer, sequence forwarding, append mode, returned handle and failure status under controlled children.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
