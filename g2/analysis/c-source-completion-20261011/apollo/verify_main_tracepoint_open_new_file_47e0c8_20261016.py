#!/usr/bin/env python3
"""Compare stock/C new tracepoint file allocation with controlled descendants."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_open_new_file_47e0c8.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-open-new-file-47e0c8';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_tracepoint_pull_pending_20074ad8[2];
void *audio_tracepoint_active_file_handle;
int32_t audio_tracepoint_trim_old_files_47e090(void){return 0;}
int32_t audio_tracepoint_write_state_47df28(void){return 0;}
void audio_tracepoint_format_pull_path_47de0a(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_tracepoint_file_open_474550(const char*a,const char*b){(void)a;(void)b;return 0;}
void audio_tracepoint_build_header_48ed00(uint8_t*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_tracepoint_file_write_474682(const void*a,uint32_t b,uint32_t c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_tracepoint_close_active_file_47e06a(void){}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_open_new_file_47e0c8',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'trim':0x47e090,'state':0x47df28,'format':0x47de0a,'open':0x474550,
         'header':0x48ed00,'write':0x474682,'close':0x47e06a}
 source={'trim':'audio_tracepoint_trim_old_files_47e090','state':'audio_tracepoint_write_state_47df28',
         'format':'audio_tracepoint_format_pull_path_47de0a','open':'audio_tracepoint_file_open_474550',
         'header':'audio_tracepoint_build_header_48ed00','write':'audio_tracepoint_file_write_474682',
         'close':'audio_tracepoint_close_active_file_47e06a'}
 def run(compiled,sequence,generation,trim_ret,state_ret,open_ok,write_mode):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  state={'sequence':syms['audio_tracepoint_next_sequence_20004188'] if compiled else 0x20004188,
         'generation':syms['audio_tracepoint_session_generation_20074ad4'] if compiled else 0x20074ad4,
         'pending':syms['audio_tracepoint_pull_pending_20074ad8'] if compiled else 0x20074ad8,
         'active':syms['audio_tracepoint_active_file_handle'] if compiled else 0x20074ae0}
  u.mem_write(state['sequence'],sequence.to_bytes(4,'little'))
  u.mem_write(state['generation'],generation.to_bytes(4,'little'))
  u.mem_write(state['pending'],(17).to_bytes(4,'little')+(23).to_bytes(4,'little'))
  u.mem_write(state['active'],(0).to_bytes(4,'little'))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   value=0
   if k=='trim':calls.append(('trim',));value=trim_ret
   elif k=='state':calls.append(('state',));value=state_ret
   elif k=='format':calls.append(('format',r[1],r[2]));cpu.mem_write(r[0],b'/log/tp/tp.bin\x00')
   elif k=='open':calls.append(('open',cstr(cpu,r[0]),cstr(cpu,r[1])));value=0x20078000 if open_ok else 0
   elif k=='header':calls.append(('header',r[1],r[2]));cpu.mem_write(r[0],bytes(range(32)))
   elif k=='write':calls.append(('write',r[1],r[2],r[3],bytes(cpu.mem_read(r[0],32))));value=32 if write_mode=='full' else 31 if write_mode=='short' else -5
   else:calls.append(('close',));cpu.mem_write(state['active'],(0).to_bytes(4,'little'))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_open_new_file_47e0c8'] if compiled else 0x47e0c8
  try:u.emu_start(entry|1,0x600000,count=1000)
  except Exception as exc:raise AssertionError((compiled,sequence,generation,trim_ret,state_ret,open_ok,write_mode,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  data=tuple((k,bytes(u.mem_read(v,8 if k=='pending' else 4)).hex()) for k,v in state.items())
  return result,data,calls
 cases=[]
 for sequence in (0,3,0xffffffff):
  for generation in (0,5):
   for trim_ret in (-7,0):
    for state_ret in (-6,0):
     for open_ok in (False,True):
      for write_mode in ('full','short','error'):
       n=run(False,sequence,generation,trim_ret,state_ret,open_ok,write_mode)
       c=run(True,sequence,generation,trim_ret,state_ret,open_ok,write_mode)
       if n!=c:raise AssertionError((sequence,generation,trim_ret,state_ret,open_ok,write_mode,n,c))
       cases.append((sequence,generation,trim_ret,state_ret,open_ok,write_mode))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_OPEN_NEW_FILE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'sequence reservation, state save, wb open, 32-byte header and exact write under controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
