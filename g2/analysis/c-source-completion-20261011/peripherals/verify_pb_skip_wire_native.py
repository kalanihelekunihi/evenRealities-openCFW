#!/usr/bin/env python3
"""Stock/compiled C unknown-wire dispatch with controlled real child ABI cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_skip_wire.c'
STUB='unsigned audio_pb_read_stream_48f3be(void*a,void*b,unsigned c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_skip_length_48f64c(void*a){(void)a;return 0;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_skip_wire_48f6a0',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,wire,child_ok):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;u.mem_write(s,struct.pack('<IIII',0,0,16,0));calls=[]
  lowers=([sy['audio_pb_read_stream_48f3be'],sy['audio_pb_skip_length_48f64c']] if is_c else [0x48f3be,0x48f64c])
  for ix,addr in enumerate(lowers):
   def hook(uc,pc,n,user,kind=ix):
    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
    calls.append((kind,regs[0],regs[2] if kind==0 else 0))
    if kind==0 and regs[1]!=0:uc.mem_write(regs[1],b'\x08')
    uc.reg_write(UC_ARM_REG_R0,child_ok);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,wire),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  target=sy['audio_pb_skip_wire_48f6a0'] if is_c else 0x48f6a0
  u.emu_start(target|1,0x600000,count=1000)
  error=struct.unpack('<I',bytes(u.mem_read(s+12,4)))[0]
  msg=bytes(u.mem_read(error,32)).split(b'\0')[0] if error else b''
  return u.reg_read(UC_ARM_REG_R0),calls,msg
 total=0
 for wire in (0,1,2,5,3,255):
  for child_ok in (0,1):
   a=run(False,wire,child_ok);b=run(True,wire,child_ok)
   assert a==b,(wire,child_ok,a,b)
   total+=1
print('PASS_PB_SKIP_WIRE_NATIVE',total)
