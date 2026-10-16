#!/usr/bin/env python3
"""Compare stock/C TPS1 state-record persistence with controlled file providers."""
import hashlib,json,subprocess,tempfile,zlib
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_write_state_47df28.c'
CRC_SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_build_header_48ed00.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-write-state-47df28';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
assert blob[0x789c10-0x438000:0x789c20-0x438000]==b'TPS1'+b'\0'*12
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
volatile uint32_t audio_tracepoint_session_generation_20074ad4;
volatile uint32_t audio_tracepoint_next_sequence_20004188;
void *audio_tracepoint_file_open_474550(const char*a,const char*b){(void)a;(void)b;return 0;}
int32_t audio_tracepoint_file_write_474682(const void*a,uint32_t b,uint32_t c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_close(void*p){(void)p;return 0;}
uint32_t audio_tracepoint_version_47dd08(void){return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_write_state_47df28',str(SOURCE),str(CRC_SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'open':0x474550,'write':0x474682,'close':0x4745f4}
 source={'open':'audio_tracepoint_file_open_474550','write':'audio_tracepoint_file_write_474682','close':'audio_file_close'}
 def run(compiled,generation,sequence,open_ok,write_mode):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(syms['audio_tracepoint_session_generation_20074ad4'] if compiled else 0x20074ad4,generation.to_bytes(4,'little'))
  u.mem_write(syms['audio_tracepoint_next_sequence_20004188'] if compiled else 0x20004188,sequence.to_bytes(4,'little'))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   if not compiled and pc==0x439c04:
    dst,src,n=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
    cpu.mem_write(dst,bytes(cpu.mem_read(src,n)));cpu.reg_write(A.UC_ARM_REG_R0,dst)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
   if not compiled and pc==0x47ddfe:
    ptr=cpu.reg_read(A.UC_ARM_REG_R0)
    cpu.reg_write(A.UC_ARM_REG_R0,zlib.crc32(bytes(cpu.mem_read(ptr,12)))&0xffffffff)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   value=0
   if k=='open':calls.append(('open',cstr(cpu,r[0]),cstr(cpu,r[1])));value=0x20078000 if open_ok else 0
   elif k=='write':
    calls.append(('write',r[1],r[2],r[3],bytes(cpu.mem_read(r[0],16))))
    value=16 if write_mode=='full' else 15 if write_mode=='short' else -5
   else:calls.append(('close',r[0]))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_write_state_47df28'] if compiled else 0x47df28
  try:u.emu_start(entry|1,0x600000,count=10000)
  except Exception as exc:raise AssertionError((compiled,generation,sequence,open_ok,write_mode,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,calls
 cases=[]
 for generation in (0,5,0xffffffff):
  for sequence in (0,23,0xffffffff):
   for open_ok in (False,True):
    for write_mode in ('full','short','error'):
     n=run(False,generation,sequence,open_ok,write_mode)
     c=run(True,generation,sequence,open_ok,write_mode)
     if n!=c:raise AssertionError((generation,sequence,open_ok,write_mode,n,c))
     cases.append((generation,sequence,open_ok,write_mode))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_WRITE_STATE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'crc_source_sha256':hashlib.sha256(CRC_SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'TPS1 record bytes/CRC and wb open, exact 16-byte write, close and failure returns with controlled file providers.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
