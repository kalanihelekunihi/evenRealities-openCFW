#!/usr/bin/env python3
"""Compare stock and source tracepoint response encoder at nanopb call boundaries."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_encode_response_5eded0.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-encode-response-5eded0';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
const uint8_t audio_tracepoint_message_descriptor[4]={0};
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_encode_response_5eded0',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,encode_ok,written,mask,command,which,fault):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x400000);record=0x20073000;length=0x20073100
  u.mem_write(record,bytes((command,0x47,which&255,which>>8,7,0xaa)));u.mem_write(length,b'\x55\x55')
  buffer=syms['audio_tracepoint_encoded_buffer'] if compiled else 0x2037b6c0
  desc=syms['audio_tracepoint_message_descriptor'] if compiled else 0x77cd84
  u.mem_write(buffer,b'\xa5'*0x300)
  native={'zero':0x43c0e4,'ostream':0x4905f4,'copy':0x439c04,'encode':0x490c32,'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e}
  source={'zero':'audio_uart_buffer_zero','ostream':'audio_pb_ostream_from_buffer','copy':'audio_uart_checksum_copy','encode':'audio_pb_encode','flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
  hooks={(syms[source[n]]&~1 if compiled else a):n for n,a in native.items()};calls=[]
  def word(a):return int.from_bytes(u.mem_read(a,4),'little')
  def put(a,x):u.mem_write(a,(x&0xffffffff).to_bytes(4,'little'))
  def string(a):return bytes(u.mem_read(a,256)).split(b'\0')[0].decode('ascii')
  def hook(cpu,pc,size,data):
   n=hooks.get(pc)
   if not n:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3));sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if n=='zero':
    calls.append((n,r0==buffer,r1,r2));cpu.mem_write(r0,bytes([r2&255])*r1)
   elif n=='ostream':
    calls.append((n,r1==buffer,r2));put(r0,0x100001);put(r0+4,r1);put(r0+8,r2);put(r0+12,0);put(r0+16,0)
   elif n=='copy':
    calls.append((n,r2,word(r1)!=0,word(r1+4)==buffer,word(r1+8),word(r1+12),word(r1+16)));cpu.mem_write(r0,bytes(cpu.mem_read(r1,r2)))
   elif n=='encode':
    calls.append((n,r1==desc,r2==record,word(r0+8),word(r0+12),word(r0+16)))
    put(r0+12,written);put(r0+16,0x78ec24 if fault else 0)
    cpu.reg_write(A.UC_ARM_REG_R0,1 if encode_ok else 0)
   elif n=='flags':cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif n=='extended':
    args=(word(sp+8),word(sp+12),word(sp+16)) if encode_ok else (string(word(sp+8)),)
    calls.append((n,r0,string(r1),string(r2),string(r3),word(sp),string(word(sp+4)),args))
   else:
    args=(r3,word(sp),word(sp+4)) if encode_ok else (string(r3),)
    calls.append((n,r0,string(r1),string(r2),args))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,record);u.reg_write(A.UC_ARM_REG_R1,length);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_encode_response_5eded0'] if compiled else 0x5eded0
  u.emu_start(entry|1,0x600000,count=20000)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(length,2)).hex(),bytes(u.mem_read(buffer,0x300)).hex(),calls
 cases=[]
 for encode_ok in (0,1):
  for written in (0,17,766):
   for mask in (0,1,2,4,7):
    for command,which in ((0,0),(3,5),(255,65535)):
     for fault in (0,1):
      n=run(False,encode_ok,written,mask,command,which,fault)
      c=run(True,encode_ok,written,mask,command,which,fault)
      if n!=c:raise AssertionError((encode_ok,written,mask,command,which,fault,n[:2],c[:2],n[3],c[3]))
      cases.append((encode_ok,written,mask,command,which,fault))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_ENCODER_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Nanopb and memory provider effects are compared at call boundaries; output buffer extent is bounded by native clear length.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
