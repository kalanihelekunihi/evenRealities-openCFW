#!/usr/bin/env python3
"""Compare native/C tracepoint inventory insertion and 16-entry cap."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_insert_file_sorted_5edbb0.c'
STORAGE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_inventory_2037cd24.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-insert-file-sorted-5edbb0';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_insert_file_sorted_5edbb0',str(SOURCE),str(STORAGE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,initial,sequence,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x20300000,0x100000)
  base=syms['audio_tracepoint_file_inventory'] if compiled else 0x2037cd24
  state=bytearray(0x88)
  for i in range(initial):
   state[i*8:i*8+4]=(i*2+1).to_bytes(4,'little')
   state[i*8+4:i*8+8]=(10+i).to_bytes(4,'little')
  state[0x80:0x84]=initial.to_bytes(4,'little')
  state[0x84:0x88]=sum(10+i for i in range(initial)).to_bytes(4,'little')
  u.mem_write(base,bytes(state));flags=[]
  hookaddr=syms['audio_log_flags']&~1 if compiled else 0x43d0ce
  def hook(cpu,pc,insn,data):
   if pc!=hookaddr:return
   flags.append(1);cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,sequence);u.reg_write(A.UC_ARM_REG_R1,size)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_insert_file_sorted_5edbb0'] if compiled else 0x5edbb0
  u.emu_start(entry|1,0x600000,count=10000)
  return bytes(u.mem_read(base,0x88)).hex(),len(flags)
 cases=[]
 for initial in (0,1,4,15,16):
  for sequence in (0,1,5,50,0xffffffff):
   for size in (0,17):
    n=run(False,initial,sequence,size);c=run(True,initial,sequence,size)
    if n!=c:raise AssertionError((initial,sequence,size,n,c))
    cases.append((initial,sequence,size))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_SORTED_INSERT_NATIVE_C','source':str(SOURCE.relative_to(ROOT)),
      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'storage':str(STORAGE.relative_to(ROOT)),'storage_sha256':hashlib.sha256(STORAGE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Sorted insertion, duplicate sequence, total-size accumulation, and full-list drop with logging disabled.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
