#!/usr/bin/env python3
"""Compare stock/C tracepoint delete-all traversal and logging paths."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_delete_all_files_5ee650.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-delete-all-files-5ee650';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
native={'open':0x474b02,'read':0x474bb8,'close':0x474c66,'lock':0x47e088,
        'parse':0x5edaf0,'format':0x5edba2,'unlink':0x47498c,'flags':0x43d0ce,
        'extended':0x43d574,'compressed':0x43ce9e}
source={'open':'audio_tracepoint_dir_open_474b02','read':'audio_tracepoint_dir_read_474bb8',
        'close':'audio_tracepoint_dir_close_474c66','lock':'audio_tracepoint_storage_lock_47e088',
        'parse':'audio_tracepoint_parse_sequence_5edaf0','format':'audio_tracepoint_format_file_path_5edba2',
        'unlink':'audio_tracepoint_storage_unlink_47498c','flags':'audio_log_flags',
        'extended':'audio_log_extended','compressed':'compressed_log_output'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_tracepoint_dir_open_474b02(const char*a){(void)a;return 0;}
void *audio_tracepoint_dir_read_474bb8(void*a){(void)a;return 0;}
int32_t audio_tracepoint_dir_close_474c66(void*a){(void)a;return 0;}
void audio_tracepoint_storage_lock_47e088(void){}
int32_t audio_tracepoint_parse_sequence_5edaf0(const char*a,uint32_t*b){(void)a;(void)b;return 0;}
void audio_tracepoint_format_file_path_5edba2(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_tracepoint_storage_unlink_47498c(const char*a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_delete_all_files_5ee650',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,mask,open_ok,entries):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  for i,(name,kind,parse_ok,unlink_ok) in enumerate(entries):
   a=0x20070000+0x200*i
   u.mem_write(a,name.encode()+b'\0')
   u.mem_write(a+0x100,bytes([kind]))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[];read_index=0;active=-1
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(160):
    c=cpu.mem_read(addr+i,1)[0]
    if c==0:break
    b.append(c)
   return bytes(b)
  def hook(cpu,pc,width,data):
   nonlocal read_index,active
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   sp=cpu.reg_read(A.UC_ARM_REG_SP);stack=struct.unpack('<IIII',bytes(cpu.mem_read(sp,16)))
   if k=='open':calls.append((k,cstr(cpu,r0)));ret=0x20078000 if open_ok else 0
   elif k=='lock':calls.append((k,));ret=0
   elif k=='read':
    calls.append((k,r0));active=read_index;read_index+=1
    ret=0x20070000+0x200*active if active<len(entries) else 0
   elif k=='parse':
    calls.append((k,cstr(cpu,r0)))
    ret=1 if entries[active][2] else 0
    if ret:cpu.mem_write(r1,struct.pack('<I',17+active))
   elif k=='format':
    calls.append((k,r1,r2));cpu.mem_write(r0,f'/log/tp/tp_{r2}.bin'.encode()+b'\0');ret=0
   elif k=='unlink':calls.append((k,cstr(cpu,r0)));ret=0 if entries[active][3] else -1
   elif k=='close':calls.append((k,r0));ret=0
   elif k=='flags':calls.append((k,));ret=mask
   elif k=='extended':
    calls.append((k,r0,cstr(cpu,r1),cstr(cpu,r2),cstr(cpu,r3),stack[0],cstr(cpu,stack[1]),cstr(cpu,stack[2])));ret=0
   else:calls.append((k,r0,cstr(cpu,r1),cstr(cpu,r2),cstr(cpu,r3)));ret=0
   cpu.reg_write(A.UC_ARM_REG_R0,ret&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_delete_all_files_5ee650'] if compiled else 0x5ee650
  u.emu_start(entry|1,0x600000,count=5000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 scenarios=[[],[('x',4,False,False)],[('tp_17.bin',8,False,False)],
            [('tp_17.bin',8,True,True)],[('tp_17.bin',8,True,False)],
            [('tp_17.bin',8,True,True),('tp_18.bin',8,True,False)],
            [('x',4,False,False),('tp_17.bin',8,True,True),('bad.bin',8,False,False)]]
 cases=[]
 for mask in (0,1,2,4,7):
  for open_ok in (False,True):
   for entries in scenarios:
    n=run(False,mask,open_ok,entries);c=run(True,mask,open_ok,entries)
    if n!=c:raise AssertionError((mask,open_ok,entries,n,c))
    cases.append((mask,open_ok,len(entries)))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_DELETE_ALL_FILES_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'directory-open failure, filtering, parse, unlink success/failure, close and five logging masks.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
