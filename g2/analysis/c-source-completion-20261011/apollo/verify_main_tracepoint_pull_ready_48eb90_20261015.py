#!/usr/bin/env python3
"""Compare stock/C pull readiness over controlled persistence-ring cases."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_ready_48eb90.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-ready-48eb90';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
volatile uint8_t audio_uart_ring_persist_initialized;
volatile uint8_t audio_uart_ring_persist_wake_blocked;
volatile uint8_t audio_uart_ring_persist_wake_pending;
uint8_t audio_uart_ring_persist_queue_state[24];
void audio_uart_ring_persist_initialize_48eac8(void){}
uint32_t audio_uart_ring_persist_record_size_48e8f0(uint32_t a){(void)a;return 8;}
uint32_t audio_uart_ring_persist_read_word_48e8e2(uint32_t a){return a;}
void audio_uart_ring_persist_submit_48ea66(uint32_t a,uint32_t b,const void*c){(void)a;(void)b;(void)c;}
int32_t audio_tracepoint_pull_backend_init_47dfec(void){return 0;}
int32_t audio_tracepoint_pull_write_batch_47e178(const void*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_tracepoint_pull_complete_47e220(void){}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_pull_ready_48eb90',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'initialize':0x48eac8,'irq_lock':0x47dce4,'backend':0x47dfec,'submit':0x48ea66,'record_size':0x48e8f0,
         'read_word':0x48e8e2,'write':0x47e178,'complete':0x47e220}
 source={'initialize':'audio_uart_ring_persist_initialize_48eac8','backend':'audio_tracepoint_pull_backend_init_47dfec',
         'submit':'audio_uart_ring_persist_submit_48ea66','record_size':'audio_uart_ring_persist_record_size_48e8f0',
         'read_word':'audio_uart_ring_persist_read_word_48e8e2','write':'audio_tracepoint_pull_write_batch_47e178',
         'complete':'audio_tracepoint_pull_complete_47e220'}
 def run(compiled,initialized,blocked,backend_ready,backend_ret,pending,records,write_ret):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  state={'initialized':(syms['audio_uart_ring_persist_initialized'] if compiled else 0x20075032),
         'blocked':(syms['audio_uart_ring_persist_wake_blocked'] if compiled else 0x20075036),
         'wake':(syms['audio_uart_ring_persist_wake_pending'] if compiled else 0x20075037),
         'backend_ready':(syms['audio_tracepoint_pull_backend_ready_20075035'] if compiled else 0x20075035),
         'failures':(syms['audio_tracepoint_pull_failure_count_20074ac0'] if compiled else 0x20074ac0),
         'queue':(syms['audio_uart_ring_persist_queue_state'] if compiled else 0x200771f4)}
  for k,v in (('initialized',initialized),('blocked',blocked),('wake',1),('backend_ready',backend_ready)):
   u.mem_write(state[k],bytes((v,)))
  u.mem_write(state['failures'],(3).to_bytes(4,'little'))
  q=bytearray(24);q[8:12]=(records*8).to_bytes(4,'little');q[20:24]=pending.to_bytes(4,'little')
  u.mem_write(state['queue'],bytes(q));calls=[]
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items() if not(compiled and k=='irq_lock')}
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   value=0
   if k=='initialize':calls.append(('initialize',));cpu.mem_write(state['initialized'],b'\x01')
   elif k=='irq_lock':value=0
   elif k=='backend':calls.append(('backend',));value=backend_ret
   elif k=='submit':calls.append(('submit',r0,r1,int.from_bytes(cpu.mem_read(r2,4),'little')))
   elif k=='record_size':calls.append(('record_size',r0));value=8
   elif k=='read_word':calls.append(('read_word',r0));value=0xa0000000+r0
   elif k=='write':
    payload=tuple(int.from_bytes(cpu.mem_read(r0+i,4),'little') for i in range(0,r1,4))
    calls.append(('write',r1,payload));value=write_ret
   elif k=='complete':calls.append(('complete',))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_pull_ready_48eb90'] if compiled else 0x48eb90
  try:u.emu_start(entry|1,0x600000,count=100000)
  except Exception as exc:raise AssertionError((compiled,initialized,blocked,backend_ready,backend_ret,pending,records,write_ret,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,tuple((k,bytes(u.mem_read(state[k],4 if k=='failures' else 24 if k=='queue' else 1)).hex()) for k in state),calls
 cases=[]
 for initialized in (0,1):
  for blocked in (0,1):
   for backend_ready in (0,1):
    for backend_ret in (-5,0):
     for pending in (0,2):
      for records in (0,1,2,9):
       for write_ret in (-7,0):
        n=run(False,initialized,blocked,backend_ready,backend_ret,pending,records,write_ret)
        c=run(True,initialized,blocked,backend_ready,backend_ret,pending,records,write_ret)
        if n!=c:raise AssertionError((initialized,blocked,backend_ready,backend_ret,pending,records,write_ret,n,c))
        cases.append((initialized,blocked,backend_ready,backend_ret,pending,records,write_ret))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PULL_READY_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'PRIMASK guarded state, backend initialization, pending submit, bounded ring record batches and completion at controlled descendants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
