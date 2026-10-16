#!/usr/bin/env python3
"""Compare native/C list-name formatter argument flow and null gating."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_format_list_name_5eddc8.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-format-list-name-5eddc8';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
int32_t g2_audio_dump_snprintf(char*a,uint32_t b,const char*c,...){(void)a;(void)b;(void)c;return 17;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_format_list_name_5eddc8',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,seq,role,present,cap):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  dst=0x20071000 if present else 0;calls=[]
  addr=syms['g2_audio_dump_snprintf']&~1 if compiled else 0x44b728
  def hook(cpu,pc,size,data):
   if pc!=addr:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   arg4=int.from_bytes(cpu.mem_read(sp,4),'little')
   arg5=int.from_bytes(cpu.mem_read(sp+4,4),'little')
   fmt=bytes(cpu.mem_read(r2,8)).split(b'\0')[0]
   calls.append((r0==dst,r1,fmt.decode(),r3,arg4,arg5))
   cpu.reg_write(A.UC_ARM_REG_R0,17)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,seq);u.reg_write(A.UC_ARM_REG_R1,role)
  u.reg_write(A.UC_ARM_REG_R2,dst);u.reg_write(A.UC_ARM_REG_R3,cap)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_format_list_name_5eddc8'] if compiled else 0x5eddc8
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for seq in (0,1,42,0xffffffff):
  for role in (0,ord('L'),ord('R'),0x1234):
   for present,cap in ((False,0),(True,0),(True,1),(True,32)):
    n=run(False,seq,role,present,cap);c=run(True,seq,role,present,cap)
    if n!=c:raise AssertionError((seq,role,present,cap,n,c))
    cases.append((seq,role,present,cap))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_LIST_NAME_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Null/capacity/zero-sequence gating and exact snprintf arguments at a controlled formatting boundary.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
