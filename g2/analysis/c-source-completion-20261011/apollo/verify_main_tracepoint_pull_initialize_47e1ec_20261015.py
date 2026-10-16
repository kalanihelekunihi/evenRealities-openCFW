#!/usr/bin/env python3
"""Compare stock/C pull initialization and pending-file close threshold."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_initialize_47e1ec.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-initialize-47e1ec';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void audio_tracepoint_close_active_file_47e06a(void){}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_pull_initialize_47e1ec',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,enabled,pending,length):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  flag=syms['audio_tracepoint_pull_enabled_20075038'] if compiled else 0x20075038
  slots=syms['audio_tracepoint_pull_pending_20074ad8'] if compiled else 0x20074ad8
  u.mem_write(flag,bytes((enabled,)));u.mem_write(slots,pending.to_bytes(4,'little')+length.to_bytes(4,'little'))
  close=syms['audio_tracepoint_close_active_file_47e06a']&~1 if compiled else 0x47e06a;calls=[]
  def hook(cpu,pc,size,data):
   if pc!=close:return
   calls.append('close');cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_pull_initialize_47e1ec'] if compiled else 0x47e1ec
  u.emu_start(entry|1,0x600000,count=10000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  if result&0x80000000:result-=0x100000000
  return result,bytes(u.mem_read(slots,8)).hex(),calls
 cases=[]
 for enabled in (0,1,2):
  for pending in (0,1,0x12345678):
   for length in (0,32,33,100):
    n=run(False,enabled,pending,length);c=run(True,enabled,pending,length)
    if n!=c:raise AssertionError((enabled,pending,length,n,c))
    cases.append((enabled,pending,length))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PULL_INITIALIZE_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Enabled check, pending length threshold, close call and two state clears at controlled file-close boundary.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
