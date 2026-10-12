#!/usr/bin/env python3
"""Actual C/native callback-storage field control flow and child ABI cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
STUB='unsigned audio_pb_skip_wire_48f6a0(void*a,unsigned b){(void)a;(void)b;return 0;} unsigned audio_pb_substream_begin_48f77e(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_substream_end_48f7ca(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_callback_payload_48f6ea(void*a,unsigned b,void*c,unsigned*d){(void)a;(void)b;(void)c;(void)d;return 0;} unsigned audio_pb_buffer_read_48f3a4(void*a,void*b,unsigned c){(void)a;(void)b;(void)c;return 1;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_callback_field_48fb30',str(S/'display_pb_decode_callback_field.c'),str(S/'display_pb_decode_stream_init.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,wire,has_cb,cb_ok,left,suberr):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;it=0x20080100;desc=0x20080200;u.mem_write(stream,bytes(16));u.mem_write(it,bytes(40));u.mem_write(desc,bytes(24))
  u.mem_write(it,struct.pack('<I',desc));u.mem_write(desc+12,struct.pack('<I',0x100801 if has_cb else 0));calls=[]
  names=['audio_pb_skip_wire_48f6a0','audio_pb_substream_begin_48f77e','audio_pb_substream_end_48f7ca','audio_pb_callback_payload_48f6ea']
  stock=[0x48f6a0,0x48f77e,0x48f7ca,0x48f6ea]
  for ix,name in enumerate(names):
   addr=sy[name] if is_c else stock[ix]
   def hook(uc,pc,n,user,kind=ix):
    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    calls.append((kind,regs[0] if kind in (0,1,2,3) else 0,regs[1] if kind in (0,3) else 0))
    if kind==1:
     uc.mem_write(regs[1]+8,struct.pack('<I',3));uc.mem_write(regs[1]+12,struct.pack('<I',0x787c70 if suberr else 0))
    if kind==3:uc.mem_write(regs[2],b'\x05');uc.mem_write(regs[3],struct.pack('<I',1))
    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  def cb(uc,pc,n,user):
   p=uc.reg_read(UC_ARM_REG_R0);calls.append((4,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
   if wire==2:uc.mem_write(p+8,struct.pack('<I',left))
   uc.reg_write(UC_ARM_REG_R0,cb_ok);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cb,begin=0x100800,end=0x100800)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,wire),(UC_ARM_REG_R2,it),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_callback_field_48fb30'] if is_c else 0x48fb30)|1,0x600000,count=1000)
  err=struct.unpack('<I',bytes(u.mem_read(stream+12,4)))[0];msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),calls,msg
 cases=[(0,False,1,0,False),(2,False,1,0,False),(2,True,1,0,False),(2,True,1,3,False),(2,True,0,3,False),(2,True,0,3,True),(0,True,1,0,False),(0,True,0,0,False)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DECODE_CALLBACK_FIELD_NATIVE',len(cases))
