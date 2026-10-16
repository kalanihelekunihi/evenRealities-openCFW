#!/usr/bin/env python3
"""Check stock tracepoint path formatter's bounded printf call against C."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_format_file_path_5edba2.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';OUT=G2/'build/c-firmware/20261015/main-tracepoint-format-file-path-5edba2';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t g2_audio_dump_snprintf(char*a,uint32_t b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_format_file_path_5edba2',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,capacity,sequence):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);output=0x20073000;calls=[]
  target=syms['g2_audio_dump_snprintf']&~1 if compiled else 0x44b728
  def hook(cpu,pc,size,data):
   if pc!=target:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   fmt=bytes(u.mem_read(r2,80)).split(b'\0')[0].decode('ascii')
   calls.append((r0==output,r1,fmt,r3));cpu.reg_write(A.UC_ARM_REG_R0,9);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,output);u.reg_write(A.UC_ARM_REG_R1,capacity);u.reg_write(A.UC_ARM_REG_R2,sequence);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_format_file_path_5edba2'] if compiled else 0x5edba2
  u.emu_start(entry|1,0x600000,count=10000)
  return calls
 cases=[]
 for capacity in (0,1,8,80,255):
  for sequence in (0,1,17,0x12345678,0xffffffff):
   n=run(False,capacity,sequence);c=run(True,capacity,sequence)
   if n!=c:raise AssertionError((capacity,sequence,n,c))
   cases.append((capacity,sequence))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_PATH_FORMAT_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Bounded formatter call arguments compared; formatter body is a separate provider.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
