#!/usr/bin/env python3
"""Compare tracepoint tp_<decimal>.bin parser with stock provider-call behavior."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_parse_sequence_5edaf0.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-parse-sequence-5edaf0';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t g2_log_candidate_module_length(const char*a){(void)a;return 0;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
int32_t audio_uart_font_path_compare(const char*a,const char*b){(void)a;(void)b;return 0;}
uint32_t audio_uart_ring_parse_uint_48d874(const char*a,const char**b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_parse_sequence_5edaf0',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'length':0x44a43c,'prefix':0x44b610,'suffix':0x46cacc,'decimal':0x48d874}
 source={'length':'g2_log_candidate_module_length','prefix':'audio_ble_hci_vendor_compare_44b610','suffix':'audio_uart_font_path_compare','decimal':'audio_uart_ring_parse_uint_48d874'}
 def run(compiled,value,present,out_present):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);name=0x20073000 if present else 0;out=0x20073100 if out_present else 0
  if name:u.mem_write(name,value.encode()+b'\0')
  if out:u.mem_write(out,b'\xaa'*4)
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
  def string(a):return bytes(u.mem_read(a,128)).split(b'\0')[0].decode('ascii')
  def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   if k=='length':calls.append((k,r0==name,string(r0)));cpu.reg_write(A.UC_ARM_REG_R0,len(string(r0)))
   elif k=='prefix':
    lhs=bytes(u.mem_read(r0,r2));rhs=bytes(u.mem_read(r1,r2));calls.append((k,r0==name,rhs.decode(),r2));cpu.reg_write(A.UC_ARM_REG_R0,0 if lhs==rhs else 1)
   elif k=='suffix':calls.append((k,r0==name+len(value)-4,string(r0),string(r1)));cpu.reg_write(A.UC_ARM_REG_R0,0 if string(r0)==string(r1) else 1)
   else:
    s=string(r0);m=re.match(r'[0-9]+',s);digits=m.group(0) if m else '';put(r1,r0+len(digits));calls.append((k,r0==name+3,s,r2,digits));cpu.reg_write(A.UC_ARM_REG_R0,int(digits or '0')&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,name);u.reg_write(A.UC_ARM_REG_R1,out);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_parse_sequence_5edaf0'] if compiled else 0x5edaf0
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,4)).hex() if out else None,calls
 cases=[]
 values=('','tp_','tp_.bin','tp_0.bin','tp_1.bin','tp_42.bin','tp_0042.bin','tp_12x.bin','tp_-1.bin','tp_+1.bin','TP_1.bin','tp_1.BIN','tp_1.bin.extra','xx_1.bin','tp_123456789.bin')
 for value in values:
  for present,out_present in ((False,True),(True,False),(True,True)):
   n=run(False,value,present,out_present);c=run(True,value,present,out_present)
   if n!=c:raise AssertionError((value,present,out_present,n,c))
   cases.append((value,present,out_present))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_SEQUENCE_PARSER_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['String length, comparison and numeric parse providers are simulated at call boundaries; full provider behavior not claimed.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
