#!/usr/bin/env python3
"""Native/compiled-C scalar field wire-type dispatch and child argument effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_scalar_dispatch.c'
names=['bool_4901cc','varint_4901d6','fixed32_490190','fixed64_4901ac','bytes_490358','string_4903ea','submessage_49048c','extension_49053c']
stocks=[0x4901cc,0x4901d6,0x490190,0x4901ac,0x490358,0x4903ea,0x49048c,0x49053c]
STUB=' '.join(f'unsigned audio_pb_decode_{name}(void*a,void*b){{(void)a;(void)b;return 0;}}' for name in names)
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_scalar_48f7f4',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,typ,wire):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;it=0x20080100;data=0x20080200;u.mem_write(s,bytes(16));u.mem_write(it,bytes(40));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',data));calls=[]
  for ix,name in enumerate(names):
   addr=sy['audio_pb_decode_'+name] if is_c else stocks[ix]
   def hook(uc,pc,n,user,kind=ix):
    calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,wire),(UC_ARM_REG_R2,it),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_scalar_48f7f4'] if is_c else 0x48f7f4)|1,0x600000,count=1000)
  err=struct.unpack('<I',bytes(u.mem_read(s+12,4)))[0];msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),calls,msg
 total=0
 for typ in range(12):
  for wire in (0,1,2,5,255):
   a=run(False,typ,wire);b=run(True,typ,wire)
   assert a==b,(typ,wire,a,b)
   total+=1
print('PASS_PB_DECODE_SCALAR_NATIVE',total)
