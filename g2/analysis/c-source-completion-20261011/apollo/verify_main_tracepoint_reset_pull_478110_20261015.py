#!/usr/bin/env python3
"""Compare stock/C tracepoint pull reset and delayed callback schedule."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_reset_pull_478110.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-reset-pull-478110';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
volatile uint8_t audio_ble_current_conn_mode;
void audio_ble_connect_param_request(uint8_t a){(void)a;}
uint32_t audio_event_loop_remove_delayed(void (*a)(void)){(void)a;return 7;}
void audio_event_loop_push_delayed(void (*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_reset_pull_478110',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,delayed,connected):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  flag=syms['audio_tracepoint_pull_connection_flag_20074f8f'] if compiled else 0x20074f8f
  mode=syms['audio_ble_current_conn_mode'] if compiled else 0x20004542
  callback=(syms['audio_ble_connect_param_request']|1) if compiled else 0x47761d
  u.mem_write(flag,bytes((connected,)));u.mem_write(mode,b'\x5a');calls=[]
  hooks={(syms['audio_event_loop_remove_delayed']&~1 if compiled else 0x476ace):'remove',
         (syms['audio_event_loop_push_delayed']&~1 if compiled else 0x47697e):'push'}
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   calls.append((k,r0==callback,r1,r2) if k=='push' else (k,r0==callback))
   cpu.reg_write(A.UC_ARM_REG_R0,7)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,delayed);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_reset_pull_478110'] if compiled else 0x478110
  u.emu_start(entry|1,0x600000,count=10000)
  return bytes(u.mem_read(mode,1)).hex(),calls
 cases=[]
 for delayed in (0,1,2,255):
  for connected in (0,1,2):
   n=run(False,delayed,connected);c=run(True,delayed,connected)
   if n!=c:raise AssertionError((delayed,connected,n,c))
   cases.append((delayed,connected))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_RESET_PULL_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Connection-mode byte and delayed callback scheduling at controlled event-loop boundaries.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
