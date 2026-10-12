#!/usr/bin/env python3
"""Native/compiled-C nanopb field storage dispatch with ABI-matched child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_field_dispatch.c'
STUB='unsigned audio_pb_decode_static_field_48f968(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_decode_callback_field_48fb30(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_decode_pointer_field_48fb1c(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_field_48fbe4',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,field_type,child_result,existing_error):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;field=0x20080100;u.mem_write(stream,struct.pack('<IIII',0,0,0,0x787c70 if existing_error else 0));u.mem_write(field,bytes(40));u.mem_write(field+22,bytes([field_type]))
  calls=[];names=['audio_pb_decode_static_field_48f968','audio_pb_decode_callback_field_48fb30','audio_pb_decode_pointer_field_48fb1c'];stock=[0x48f968,0x48fb30,0x48fb1c]
  for ix,name in enumerate(names):
   addr=sy[name] if is_c else stock[ix]
   def hook(uc,pc,n,user,kind=ix):
    calls.append((kind,tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))))
    uc.reg_write(UC_ARM_REG_R0,child_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,2),(UC_ARM_REG_R2,field),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  target=sy['audio_pb_decode_field_48fbe4'] if is_c else 0x48fbe4
  u.emu_start(target|1,0x600000,count=1000)
  err=struct.unpack('<I',bytes(u.mem_read(stream+12,4)))[0];msg=bytes(u.mem_read(err,32)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),calls,msg
 total=0
 for field_type in (0,0x40,0x80,0xc0):
  for child_result in (0,1):
   for existing_error in (False,True):
    a=run(False,field_type,child_result,existing_error);b=run(True,field_type,child_result,existing_error)
    assert a==b,(field_type,child_result,existing_error,a,b)
    total+=1
print('PASS_PB_DECODE_FIELD_DISPATCH_NATIVE',total)
