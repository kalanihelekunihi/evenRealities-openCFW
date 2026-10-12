#!/usr/bin/env python3
"""Stock/compiled C nanopb stream read and length skip with real buffer effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_read_stream_48f3be',str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,kind,n,direct,skip,fail):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;source=0x20080100;out=0x20080200
  data=(bytes([n]) if kind=='length' else b'')+bytes(range(1,50))
  u.mem_write(source,data);u.mem_write(out,b'\xaa'*64)
  cb=(sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5) if direct else 0x100801
  u.mem_write(stream,struct.pack('<IIII',cb,source,len(data),0))
  def generic(uc,pc,size,user):
   p=uc.reg_read(UC_ARM_REG_R0);dst=uc.reg_read(UC_ARM_REG_R1);count=uc.reg_read(UC_ARM_REG_R2)
   state=struct.unpack('<I',bytes(uc.mem_read(p+4,4)))[0]
   if fail:uc.reg_write(UC_ARM_REG_R0,0)
   else:
    if dst:uc.mem_write(dst,bytes(uc.mem_read(state,count)))
    uc.mem_write(p+4,struct.pack('<I',state+count));uc.reg_write(UC_ARM_REG_R0,1)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,generic,begin=0x100800,end=0x100800)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,0 if skip else out),(UC_ARM_REG_R2,n),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  name='audio_pb_skip_length_48f64c' if kind=='length' else 'audio_pb_read_stream_48f3be'
  target=sy[name] if is_c else {'audio_pb_skip_length_48f64c':0x48f64c,'audio_pb_read_stream_48f3be':0x48f3be}[name]
  u.emu_start(target|1,0x600000,count=5000)
  s=bytes(u.mem_read(stream,16));err=struct.unpack_from('<I',s,12)[0]
  msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),s[4:12],bytes(u.mem_read(out,64)),msg
 total=0
 cases=[('read',0,True,False,False),('read',8,True,False,False),('read',8,True,True,False),('read',17,False,True,False),('read',17,False,True,True),('read',48,False,False,False),('length',4,True,True,False),('length',4,False,True,False)]
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  assert a==b,(case,a,b)
  total+=1
print('PASS_PB_DECODE_STREAM_NATIVE',total)
