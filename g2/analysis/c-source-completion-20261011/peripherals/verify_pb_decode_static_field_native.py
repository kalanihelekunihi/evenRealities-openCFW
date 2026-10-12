#!/usr/bin/env python3
"""Bounded actual-C/native static-field effects with authentic child ABI cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_static_field.c'
STUB='unsigned audio_pb_decode_scalar_48f7f4(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_substream_begin_48f77e(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_substream_end_48f7ca(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_iter_begin_4d94ba(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_default_fields_48fdf2(void*a){(void)a;return 0;} void audio_uart_buffer_zero(void*a,unsigned b,unsigned c){(void)a;(void)b;(void)c;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_static_field_48f968',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,mode,wire,count0,scalar_result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;it=0x20080100;field=0x20080200;size=0x20080300;desc=0x20080400;subtable=0x20080500
  u.mem_write(stream,bytes(16));u.mem_write(it,bytes(40));u.mem_write(field,bytes(64));u.mem_write(size,struct.pack('<H',count0));u.mem_write(desc,bytes(24));u.mem_write(subtable,bytes(4));u.mem_write(desc+4,struct.pack('<I',subtable))
  u.mem_write(it+16,struct.pack('<HHH',7,4,2));u.mem_write(it+22,bytes([mode|1]));u.mem_write(it+24,struct.pack('<III',field,field,size));u.mem_write(it+36,struct.pack('<I',desc))
  calls=[]
  names=['audio_pb_decode_scalar_48f7f4','audio_pb_substream_begin_48f77e','audio_pb_substream_end_48f7ca','audio_pb_iter_begin_4d94ba','audio_pb_default_fields_48fdf2','audio_uart_buffer_zero']
  stock=[0x48f7f4,0x48f77e,0x48f7ca,0x4d9384,0x48fdf2,0x43c0e4]
  for ix,name in enumerate(names):
   addr=sy[name] if is_c else stock[ix]
   def hook(uc,pc,n,user,kind=ix):
    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
    calls.append((kind,regs))
    if kind==1:uc.mem_write(regs[1]+8,struct.pack('<I',0))
    uc.reg_write(UC_ARM_REG_R0,scalar_result if kind==0 else 1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,wire),(UC_ARM_REG_R2,it),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  target=sy['audio_pb_decode_static_field_48f968'] if is_c else 0x48f968
  u.emu_start(target|1,0x600000,count=1000)
  err=struct.unpack('<I',bytes(u.mem_read(stream+12,4)))[0]
  msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  # Stack-local substream address differs between C and stock, so normalize that call.
  norm=[(k,tuple(0 if k in (1,2) and j==1 else v for j,v in enumerate(regs))) for k,regs in calls]
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(it,40)),bytes(u.mem_read(size,2)),norm,msg
 total=0
 for case in [(0,0,0,1),(0x10,0,0,1),(0x20,0,0,1),(0x20,0,2,1),(0x30,0,7,1),(0x20,2,0,1)]:
  a=run(False,*case);b=run(True,*case)
  assert a==b,(case,a,b)
  total+=1
print('PASS_PB_DECODE_STATIC_NATIVE',total)
