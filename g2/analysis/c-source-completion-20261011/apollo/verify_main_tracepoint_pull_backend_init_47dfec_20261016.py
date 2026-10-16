#!/usr/bin/env python3
"""Compare stock/C tracepoint backend initialization over controlled storage state."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_backend_init_47dfec.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-backend-init-47dfec';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_pull_enabled_20075038;
volatile uint32_t audio_tracepoint_session_generation_20074ad4;
volatile uint32_t audio_tracepoint_next_sequence_20004188;
uint32_t audio_tracepoint_pull_pending_20074ad8[2];
int32_t audio_tracepoint_storage_mkdir_474a76(const char*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_tracepoint_read_state_47df8a(void){}
int32_t audio_tracepoint_list_files_47deb4(uint32_t*a){(void)a;return 0;}
void audio_tracepoint_format_pull_path_47de0a(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_tracepoint_file_size_47de7a(const char*a){(void)a;return 0;}
int32_t audio_tracepoint_write_state_47df28(void){return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_pull_backend_init_47dfec',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'mkdir':0x474a76,'read_state':0x47df8a,'list':0x47deb4,'format':0x47de0a,
         'size':0x47de7a,'write_state':0x47df28}
 source={'mkdir':'audio_tracepoint_storage_mkdir_474a76','read_state':'audio_tracepoint_read_state_47df8a',
         'list':'audio_tracepoint_list_files_47deb4','format':'audio_tracepoint_format_pull_path_47de0a',
         'size':'audio_tracepoint_file_size_47de7a','write_state':'audio_tracepoint_write_state_47df28'}
 def run(compiled,enabled,next_seq,generation,count,highest,size_value,list_ret,write_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  state={'enabled':syms['audio_tracepoint_pull_enabled_20075038'] if compiled else 0x20075038,
         'next':syms['audio_tracepoint_next_sequence_20004188'] if compiled else 0x20004188,
         'generation':syms['audio_tracepoint_session_generation_20074ad4'] if compiled else 0x20074ad4,
         'pending':syms['audio_tracepoint_pull_pending_20074ad8'] if compiled else 0x20074ad8}
  u.mem_write(state['enabled'],bytes((enabled,)))
  u.mem_write(state['next'],next_seq.to_bytes(4,'little'))
  u.mem_write(state['generation'],generation.to_bytes(4,'little'))
  u.mem_write(state['pending'],(13).to_bytes(4,'little')+(29).to_bytes(4,'little'))
  hooks={(syms[source[k]]&~1 if compiled else a):k for k,a in native.items()};calls=[]
  def cstr(cpu,addr):
   b=bytearray()
   for i in range(64):
    x=cpu.mem_read(addr+i,1)[0]
    if x==0:break
    b.append(x)
   return bytes(b)
  def hook(cpu,pc,length,data):
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   value=0
   if k=='mkdir':calls.append(('mkdir',cstr(cpu,r[0]),r[1]))
   elif k=='read_state':calls.append(('read_state',))
   elif k=='list':
    calls.append(('list',));value=list_ret
    cpu.mem_write(r[0],count.to_bytes(4,'little',signed=True)+(1).to_bytes(4,'little')+highest.to_bytes(4,'little'))
   elif k=='format':calls.append(('format',r[1],r[2]));cpu.mem_write(r[0],b'/log/tp/tp.bin\0')
   elif k=='size':calls.append(('size',cstr(cpu,r[0])));value=size_value
   else:calls.append(('write_state',));value=write_ret
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_pull_backend_init_47dfec'] if compiled else 0x47dfec
  try:u.emu_start(entry|1,0x600000,count=1000)
  except Exception as exc:raise AssertionError((compiled,enabled,next_seq,generation,count,highest,size_value,list_ret,write_ret,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  data=tuple((k,bytes(u.mem_read(v,8 if k=='pending' else 1 if k=='enabled' else 4)).hex()) for k,v in state.items())
  return result,data,calls
 cases=[]
 for enabled in (0,1):
  for next_seq in (0,20):
   for generation in (0,0xffffffff):
    for count,highest in ((0,0),(1,5),(3,25)):
     for size_value in (31,32,0x8000):
      for list_ret,write_ret in ((-7,0),(0,-6),(0,0)):
       args=(enabled,next_seq,generation,count,highest,size_value,list_ret,write_ret)
       n=run(False,*args);c=run(True,*args)
       if n!=c:raise AssertionError((args,n,c))
       cases.append(args)
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PULL_BACKEND_INIT_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'enabled bypass, generation, list/max sequence, resumable size, state write and failure propagation under controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
