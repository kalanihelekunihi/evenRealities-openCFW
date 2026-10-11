#!/usr/bin/env python3
"""Controlled native/source dump comparison with identical snprintf/append/sink cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/audio_dump_hex_source_candidate/dump.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'dump.o'; elfpath=Path(td)/'dump.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-DG2_DUMP_ORACLE','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'g2_audio_dump_log_state':0x20070be8,'g2_audio_dump_buffer':0x2006bd30,'g2_log_guard_enter':0x101011,'g2_log_guard_exit':0x101021,'g2_log_contains':0x101031,'g2_log_append':0x101041,'g2_log_transport_submit':0x101051,'g2_audio_dump_snprintf':0x101061}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(elfpath),str(obj)],check=True)
 with elfpath.open('rb') as f:
  e=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,width,length,level,enabled,token):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_write(0x438000,STOCK)
  u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for addr,data in segs:u.mem_write(addr,data)
  state=bytearray(0x100);state[0]=level;state[0xf1]=enabled
  u.mem_write(0x20070be8,bytes(state));u.mem_write(0x2006bd30,bytes([0xa5])*1024)
  u.mem_write(0x20040000,b'test\0');u.mem_write(0x20040100,bytes(range(64)))
  for reg,value in ((A.UC_ARM_REG_R0,0x20040000),(A.UC_ARM_REG_R1,width),(A.UC_ARM_REG_R2,0x20040100),(A.UC_ARM_REG_R3,length),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,value)
  native_map={0x44b63a:'contains',0x43d416:'enter',0x43d438:'exit',0x44b728:'fmt',0x44b5a0:'padding',0x44b668:'append',0x44aa76:'output'}
  model_map={0x101010:'enter',0x101020:'exit',0x101030:'contains',0x101040:'append',0x101050:'output',0x101060:'fmt'}
  calls=[];done=[False]
  def cs(p):
   out=bytearray()
   for i in range(2048):
    x=u.mem_read(p+i,1)[0]
    if not x:break
    out.append(x)
   return bytes(out)
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(native_map if native else model_map).get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)];sp=cpu.reg_read(A.UC_ARM_REG_SP)
   ret=0
   if kind=='contains':ret=0x20070bea if token else 0;calls.append(('contains',cs(r[0])))
   elif kind in ('enter','exit'):calls.append((kind,))
   elif kind=='fmt':
    fmt=cs(r[2]);arg=r[3]
    if fmt.startswith(b'D/HEX'):
     start=int.from_bytes(cpu.mem_read(sp,4),'little');end=int.from_bytes(cpu.mem_read(sp+4,4),'little');out=f'D/HEX {cs(arg).decode()}: {start:04X}-{end:04X}: '.encode()
    elif fmt==b'%02X ':out=f'{arg:02X} '.encode()
    elif fmt==b'%c':out=bytes([arg&255])
    else:raise AssertionError(fmt)
    capacity=r[1];cpu.mem_write(r[0],out[:max(0,capacity-1)]+b'\0');ret=len(out);calls.append(('fmt',fmt,out))
   elif kind=='padding':cpu.mem_write(r[0],cs(r[1])+b'\0');calls.append(('padding',))
   elif kind=='append':
    src=cs(r[2]);n=min(len(src),max(0,1024-r[0]));cpu.mem_write(r[1],src[:n]);ret=n;calls.append(('append',src,n))
   elif kind=='output':calls.append(('output',bytes(cpu.mem_read(r[0],r[1])),r[1]))
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x43dacc if native else sym['audio_dump_hex'])|1,0,count=200000)
  assert done[0],(native,width,length)
  return calls,bytes(u.mem_read(0x2006bd30,512))
 count=0
 for width,length in ((8,0),(8,1),(8,8),(8,9),(16,17),(16,32)):
  for level,enabled,token in ((4,1,1),(3,1,1),(4,0,1),(4,1,0)):
   a=run(True,width,length,level,enabled,token);b=run(False,width,length,level,enabled,token)
   # Native calls one 8-byte constant copy for padding; candidate writes those bytes in C.
   filtered=lambda x:[v for v in x[0] if v[0]!='padding']
   assert filtered(a)==filtered(b),(width,length,level,enabled,token,filtered(a),filtered(b))
   assert a[1]==b[1],(width,length,'buffer')
   count+=1
 print('PASS_AUDIO_DUMP_HEX',count)
