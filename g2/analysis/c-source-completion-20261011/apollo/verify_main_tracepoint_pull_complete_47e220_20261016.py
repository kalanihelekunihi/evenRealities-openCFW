#!/usr/bin/env python3
"""Check the stock pull-completion close dispatch against its C body."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_complete_47e220.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-complete-47e220';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
void *audio_tracepoint_active_file_handle;
int32_t audio_tracepoint_file_close_474910(void *p){(void)p;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_pull_complete_47e220',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,handle):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  slot=syms['audio_tracepoint_active_file_handle'] if compiled else 0x20074ae0
  u.mem_write(slot,handle.to_bytes(4,'little'))
  calls=[];close=syms['audio_tracepoint_file_close_474910']&~1 if compiled else 0x474910
  def hook(cpu,pc,size,data):
   if pc!=close:return
   calls.append(cpu.reg_read(A.UC_ARM_REG_R0))
   cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_pull_complete_47e220'] if compiled else 0x47e220
  u.emu_start(entry|1,0x600000,count=100)
  return calls,int.from_bytes(u.mem_read(slot,4),'little')
 for h in (0,0x20078000,0x200043f8,0x20004440,0x200043b0):
  n=run(False,h);c=run(True,h)
  if n!=c:raise AssertionError((hex(h),n,c))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PULL_COMPLETE_NATIVE_C','source':str(SOURCE.relative_to(ROOT)),
      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,
      'native_c_cases':5,'scope':'zero/nonzero active handle and close dispatch; close implementation remains an import.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],row['native_c_cases'],hashlib.sha256(path.read_bytes()).hexdigest())
