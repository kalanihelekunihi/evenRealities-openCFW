#!/usr/bin/env python3
"""Compare stock/C tracepoint filename acceptance with controlled C string helpers."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_parse_file_entry_47de18.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-parse-file-entry-47de18';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t g2_log_module_length(const char*p){(void)p;return 0;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
int32_t audio_uart_font_path_compare(const char*a,const char*b){(void)a;(void)b;return 0;}
uint32_t audio_uart_ring_parse_uint_48d874(const char*a,const char**b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_parse_file_entry_47de18',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'length':0x44a43c,'prefix':0x44b610,'suffix':0x46cacc,'parse':0x48d874}
 source={'length':'g2_log_module_length','prefix':'audio_ble_hci_vendor_compare_44b610',
         'suffix':'audio_uart_font_path_compare','parse':'audio_uart_ring_parse_uint_48d874'}
 def run(compiled,name):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  src=0x2007d000;dst=0x2007e000
  u.mem_write(src,name.encode()+b'\0');u.mem_write(dst,b'ZZZZ')
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(128):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   value=0
   if k=='length':calls.append(('length',cstr(cpu,r[0])));value=len(cstr(cpu,r[0]))
   elif k=='prefix':
    a=bytes(cpu.mem_read(r[0],r[2]));b=bytes(cpu.mem_read(r[1],r[2]));calls.append(('prefix',a,b,r[2]));value=0 if a==b else 1
   elif k=='suffix':
    a=cstr(cpu,r[0]);b=cstr(cpu,r[1]);calls.append(('suffix',a,b));value=0 if a==b else 1
   else:
    text=cstr(cpu,r[0]);m=re.match(rb'[+-]?\d+',text)
    consumed=len(m.group()) if m else 0
    value=int(m.group())&0xffffffff if m else 0
    cpu.mem_write(r[1],(r[0]+consumed).to_bytes(4,'little'))
    calls.append(('parse',text,r[2],consumed))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,src);u.reg_write(A.UC_ARM_REG_R1,dst)
  entry=syms['audio_tracepoint_parse_file_entry_47de18'] if compiled else 0x47de18
  u.emu_start(entry|1,0x600000,count=1000)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(dst,4)),calls
 cases=[]
 for name in ('','tp_1','tp_.bin','tp_0.bin','tp_1.bin','tp_42.bin','tp_+3.bin',
              'tp_-1.bin','tp_01.bin','tp_1.txt','tx_1.bin','a_tp_1.bin','tp_1.bin.old',
              'tp_1x.bin','tp_99999.bin','tp_4294967295.bin'):
  n=run(False,name);c=run(True,name)
  if n!=c:raise AssertionError((name,n,c))
  cases.append(name)
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PARSE_FILE_ENTRY_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'minimum length, tp_ prefix, .bin suffix, exact decimal end pointer and output write with controlled string helpers.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
