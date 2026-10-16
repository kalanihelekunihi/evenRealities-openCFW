#!/usr/bin/env python3
"""Compare stock/C tracepoint batch-write control flow with controlled children."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_write_batch_47e178.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-write-batch-47e178';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_pull_enabled_20075038;
uint32_t audio_tracepoint_pull_pending_20074ad8[2];
void *audio_tracepoint_active_file_handle;
void audio_tracepoint_close_active_file_47e06a(void){}
int32_t audio_tracepoint_open_new_file_47e0c8(void){return 0;}
int32_t audio_tracepoint_reopen_pending_file_47e144(void){return 0;}
int32_t audio_tracepoint_file_write_474682(const void *a,uint32_t b,uint32_t c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_pull_write_batch_47e178',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'close':0x47e06a,'open_new':0x47e0c8,'reopen':0x47e144,'write':0x474682}
 source={'close':'audio_tracepoint_close_active_file_47e06a','open_new':'audio_tracepoint_open_new_file_47e0c8',
         'reopen':'audio_tracepoint_reopen_pending_file_47e144','write':'audio_tracepoint_file_write_474682'}
 def run(compiled,enabled,pending,offset,active,open_ret,write_mode):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  state={'enabled':syms['audio_tracepoint_pull_enabled_20075038'] if compiled else 0x20075038,
         'pending':syms['audio_tracepoint_pull_pending_20074ad8'] if compiled else 0x20074ad8,
         'active':syms['audio_tracepoint_active_file_handle'] if compiled else 0x20074ae0}
  u.mem_write(state['enabled'],bytes((enabled,)))
  u.mem_write(state['pending'],pending.to_bytes(4,'little')+offset.to_bytes(4,'little'))
  u.mem_write(state['active'],(0x20078000 if active else 0).to_bytes(4,'little'))
  u.mem_write(0x2007e000,b'X'*64)
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   value=0
   if k=='close':
    calls.append(('close',));cpu.mem_write(state['active'],(0).to_bytes(4,'little'))
   elif k in ('open_new','reopen'):
    calls.append((k,));value=open_ret
    if value==0:cpu.mem_write(state['active'],(0x20078000).to_bytes(4,'little'))
   else:
    calls.append(('write',r[0],r[1],r[2],r[3]))
    value=r[2] if write_mode=='full' else r[2]-1 if write_mode=='short' else -5
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.reg_write(A.UC_ARM_REG_R0,0x2007e000);u.reg_write(A.UC_ARM_REG_R1,32)
  entry=syms['audio_tracepoint_pull_write_batch_47e178'] if compiled else 0x47e178
  try:u.emu_start(entry|1,0x600000,count=1000)
  except Exception as exc:raise AssertionError((compiled,enabled,pending,offset,active,open_ret,write_mode,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  data=tuple((k,bytes(u.mem_read(v,8 if k=='pending' else 4 if k=='active' else 1)).hex()) for k,v in state.items())
  return result,data,calls
 cases=[]
 for enabled in (0,1):
  for pending in (0,4):
   for offset in (0,0x7fe0,0x8000):
    for active in (0,1):
     for open_ret in (-6,0):
      for write_mode in ('full','short','error'):
       n=run(False,enabled,pending,offset,active,open_ret,write_mode)
       c=run(True,enabled,pending,offset,active,open_ret,write_mode)
       if n!=c:raise AssertionError((enabled,pending,offset,active,open_ret,write_mode,n,c))
       cases.append((enabled,pending,offset,active,open_ret,write_mode))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PULL_WRITE_BATCH_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'enable, 0x8000 rollover, new/reopen selection, full/short/error writes and pending length with controlled children.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
