#!/usr/bin/env python3
"""Compare stock/C tracepoint file inventory over controlled directory entries."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_list_files_47deb4.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-list-files-47deb4';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_tracepoint_dir_open_474b02(const char *p){(void)p;return 0;}
void *audio_tracepoint_dir_read_474bb8(void*p){(void)p;return 0;}
int32_t audio_tracepoint_dir_close_474c66(void*p){(void)p;return 0;}
int32_t audio_tracepoint_parse_file_entry_47de18(const void*p,uint32_t*q){(void)p;(void)q;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_list_files_47deb4',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'open':0x474b02,'read':0x474bb8,'close':0x474c66,'parse':0x47de18}
 source={'open':'audio_tracepoint_dir_open_474b02','read':'audio_tracepoint_dir_read_474bb8',
         'close':'audio_tracepoint_dir_close_474c66','parse':'audio_tracepoint_parse_file_entry_47de18'}
 def run(compiled,open_ok,entries):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  summary=0x2007e000;u.mem_write(summary,b'Z'*12)
  entry=0x2007d000;handle=0x20078000;u.mem_write(entry,b'\0'*0x101)
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()}
  calls=[];index=0;current=None
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   nonlocal index,current
   if not compiled and pc==0x43c0e4:
    dst=cpu.reg_read(A.UC_ARM_REG_R0);n=cpu.reg_read(A.UC_ARM_REG_R1)
    cpu.mem_write(dst,b'\0'*n);cpu.reg_write(A.UC_ARM_REG_R0,dst)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
   k=hooks.get(pc)
   if not k:return
   r0,r1=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1));value=0
   if k=='open':calls.append(('open',cstr(cpu,r0)));value=handle if open_ok else 0
   elif k=='read':
    calls.append(('read',r0==handle))
    if index<len(entries):
     current=entries[index];index+=1
     cpu.mem_write(entry+0x100,bytes((current[0],)))
     value=entry
   elif k=='parse':
    calls.append(('parse',r0==entry));value=current[1]
    if value:cpu.mem_write(r1,current[2].to_bytes(4,'little'))
   else:calls.append(('close',r0==handle))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,summary)
  entrypc=syms['audio_tracepoint_list_files_47deb4'] if compiled else 0x47deb4
  try:u.emu_start(entrypc|1,0x600000,count=10000)
  except Exception as exc:raise AssertionError((compiled,open_ok,entries,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,bytes(u.mem_read(summary,12)),calls
 cases=[]
 plans=[[],[(4,1,10)],[(8,0,10)],[(8,1,10)],[(8,1,10),(8,1,3),(8,1,17)],
        [(8,1,0xffffffff),(8,1,0)],[(4,1,20),(8,1,42),(8,0,5),(8,1,2)]]
 for open_ok in (False,True):
  for entries in plans:
   n=run(False,open_ok,entries);c=run(True,open_ok,entries)
   if n!=c:raise AssertionError((open_ok,entries,n,c))
   cases.append((open_ok,entries))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_LIST_FILES_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'directory open failure, file-type/parser filters, min/max sequences, close and empty listings with controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
