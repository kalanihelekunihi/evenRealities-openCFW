#!/usr/bin/env python3
"""Stock/actual-C nanopb submessage callback and parent dispatch effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_submessage.c'
STUB='unsigned audio_pb_substream_begin_48f77e(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_substream_end_48f7ca(void*a,void*b){(void)a;(void)b;return 0;} unsigned audio_pb_decode_parent_48fe98(void*a,const void*b,void*c,unsigned d){(void)a;(void)b;(void)c;(void)d;return 0;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_submessage_49048c',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,typ,desc,begin_ok,cb_result,cb_left,parent_result,end_result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;it=0x20080100;data=0x20080200;ctx=0x20080508;u.mem_write(s,bytes(16));u.mem_write(it,bytes(40));u.mem_write(ctx-8,struct.pack('<I',0x100801))
  u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<III',data,ctx,desc))
  calls=[]
  children=[('audio_pb_substream_begin_48f77e',0x48f77e),('audio_pb_substream_end_48f7ca',0x48f7ca),('audio_pb_decode_parent_48fe98',0x48fe98)]
  for ix,(name,stock) in enumerate(children):
   addr=sy[name] if is_c else stock
   def hook(uc,pc,n,user,kind=ix):
    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    calls.append((kind,regs[0] if kind<2 else regs[1],regs[3] if kind==2 else 0))
    if kind==0:uc.mem_write(regs[1]+8,struct.pack('<I',3))
    uc.reg_write(UC_ARM_REG_R0,[begin_ok,end_result,parent_result][kind]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  def cb(uc,pc,n,user):
   regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   calls.append((3,regs[1],regs[2]));uc.mem_write(regs[0]+8,struct.pack('<I',cb_left))
   uc.reg_write(UC_ARM_REG_R0,cb_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cb,begin=0x100800,end=0x100800)
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,it),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_submessage_49048c'] if is_c else 0x49048c)|1,0x600000,count=1000)
  err=struct.unpack('<I',bytes(u.mem_read(s+12,4)))[0];msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),calls,msg
 cases=[(8,0x20080600,1,1,3,1,1),(9,0x20080600,1,1,0,1,1),(9,0x20080600,1,1,3,1,1),(9,0x20080600,1,0,3,1,1),(8,0,1,1,3,1,1),(8,0x20080600,0,1,3,1,1),(8,0x20080600,1,1,3,1,0),(8,0x20080600,1,1,3,0,1)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DECODE_SUBMESSAGE_NATIVE',len(cases))
