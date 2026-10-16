#!/usr/bin/env python3
"""Compare stock/C tracepoint scan across controlled directory entries."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_scan_files_5edc5a.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-scan-files-5edc5a';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_file_inventory[0x88];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_tracepoint_dir_open_474b02(const char*a){(void)a;return 0;}
void *audio_tracepoint_dir_read_474bb8(void*a){(void)a;return 0;}
void audio_tracepoint_dir_close_474c66(void*a){(void)a;}
int32_t audio_tracepoint_parse_sequence_5edaf0(const char*a,uint32_t*b){(void)a;(void)b;return 0;}
void audio_tracepoint_format_file_path_5edba2(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_tracepoint_file_size_5edb68(const char*a){(void)a;return 0;}
void audio_tracepoint_insert_file_sorted_5edbb0(uint32_t a,uint32_t b){(void)a;(void)b;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_scan_files_5edc5a',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'zero':0x43c0e4,'open':0x474b02,'read':0x474bb8,'close':0x474c66,
         'parse':0x5edaf0,'format':0x5edba2,'size':0x5edb68,'insert':0x5edbb0,'flags':0x43d0ce}
 source={'zero':'audio_uart_buffer_zero','open':'audio_tracepoint_dir_open_474b02',
         'read':'audio_tracepoint_dir_read_474bb8','close':'audio_tracepoint_dir_close_474c66',
         'parse':'audio_tracepoint_parse_sequence_5edaf0','format':'audio_tracepoint_format_file_path_5edba2',
         'size':'audio_tracepoint_file_size_5edb68','insert':'audio_tracepoint_insert_file_sorted_5edbb0','flags':'audio_log_flags'}
 def run(compiled,opened,types,parse_mask):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x20300000,0x100000)
  inv=syms['audio_tracepoint_file_inventory'] if compiled else 0x2037cd24
  u.mem_write(inv,b'\xa5'*0x88)
  directory=0x20071000;entries=[0x20072000+i*0x200 for i in range(len(types))]
  for i,t in enumerate(types):u.mem_write(entries[i],('tp_%d.bin'%i).encode()+b'\0');u.mem_write(entries[i]+0x100,bytes((t,)))
  index=0;calls=[]
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()}
  def hook(cpu,pc,size,data):
   nonlocal index
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   value=0
   if k=='zero':calls.append(('zero',r0==inv,r1,r2));cpu.mem_write(r0,b'\0'*r1)
   elif k=='open':calls.append(('open',bytes(cpu.mem_read(r0,8)).split(b'\0')[0].decode()));value=directory if opened else 0
   elif k=='read':calls.append(('read',r0==directory));value=entries[index] if index<len(entries) else 0;index+=1
   elif k=='close':calls.append(('close',r0==directory))
   elif k=='parse':
    j=entries.index(r0);calls.append(('parse',j));valid=(parse_mask>>j)&1
    if valid:cpu.mem_write(r1,(j+1).to_bytes(4,'little'))
    value=valid
   elif k=='format':calls.append(('format',r1,r2));cpu.mem_write(r0,b'/log/tp/tp_1.bin\0')
   elif k=='size':calls.append(('size',bytes(cpu.mem_read(r0,20)).split(b'\0')[0].decode()));value=100
   elif k=='insert':calls.append(('insert',r0,r1))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_scan_files_5edc5a'] if compiled else 0x5edc5a
  u.emu_start(entry|1,0x600000,count=100000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,bytes(u.mem_read(inv,0x88)).hex(),calls
 cases=[]
 for opened in (False,True):
  for types in ((),(8,),(4,),(8,4,8)):
   for mask in (0,1,5,7):
    n=run(False,opened,types,mask);c=run(True,opened,types,mask)
    if n!=c:raise AssertionError((opened,types,mask,n,c))
    cases.append((opened,types,mask))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_SCAN_FILES_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Inventory clear, open failure, entry filtering, parser/path/size/insert and close at controlled descendants with logging disabled.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
