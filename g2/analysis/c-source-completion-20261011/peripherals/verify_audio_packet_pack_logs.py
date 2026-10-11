#!/usr/bin/env python3
"""Native/C packet packer including diagnostic logger ABI and packet bytes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/packet_pack_alias_candidate/alias.c'
BASE=Path('/tmp/opencfw-codec-request/drain.elf')
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with BASE.open('rb') as stream:
 elf=ELFFile(stream);base_segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'wrapper.o';path=directory/'wrapper.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=codec_pack=0x100033',
                 '--defsym=audio_log_flags=0x101011','--defsym=audio_log_extended=0x101021',
                 '--defsym=audio_log_simple=0x101031','-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,length,flag,mask,null_wire,null_total):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x30000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in base_segments+segments:unit.mem_write(address,data)
  unit.mem_write(0x20042000,bytes(range(32)))
  unit.mem_write(0x20041000,bytes([0xa5])*64)
  unit.mem_write(0x20044000,b'\xee\xee')
  unit.mem_write(0x20075013,b'\xfe')
  stack=0x200f0000
  for off,value in ((0,flag),(4,0 if null_wire else 0x20041000),(8,0 if null_total else 0x20044000)):
   unit.mem_write(stack+off,(value&0xffffffff).to_bytes(4,'little'))
  for reg,value in ((A.UC_ARM_REG_R0,0x12ab),(A.UC_ARM_REG_R1,0xcd34),
                    (A.UC_ARM_REG_R2,0x20042000),(A.UC_ARM_REG_R3,length),
                    (A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):
   unit.reg_write(reg,value)
  targets=({0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'simple'} if native else
           {0x101010:'flags',0x101020:'extended',0x101030:'simple'})
  calls=[];done=[False]
  def string(pointer):
   value=bytearray()
   for offset in range(256):
    ch=unit.mem_read(pointer+offset,1)[0]
    if not ch:break
    value.append(ch)
   return bytes(value)
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=targets.get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)]
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if kind=='flags':calls.append((kind,));cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif kind=='extended':
    line=int.from_bytes(cpu.mem_read(sp,4),'little');fmt=string(int.from_bytes(cpu.mem_read(sp+4,4),'little'))
    n=8 if b'Pack message(total' in fmt else 1
    args=[int.from_bytes(cpu.mem_read(sp+8+4*i,4),'little') for i in range(n)]
    calls.append((kind,r[0],string(r[1]),string(r[2]),string(r[3]),line,fmt,tuple(args)))
   else:
    fmt=string(r[1]);n=8 if b'Pack message(total' in fmt else 1
    args=[r[3]]+[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(n-1)]
    calls.append((kind,r[0],fmt,string(r[2]),tuple(args)))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  unit.emu_start((0x57bb0a if native else symbols['audio_packet_pack'])|1,0,count=2500)
  assert done[0],(native,length,flag,mask,null_wire,null_total)
  return (unit.reg_read(A.UC_ARM_REG_R0),calls,bytes(unit.mem_read(0x20041000,40)),
          bytes(unit.mem_read(0x20044000,2)),bytes(unit.mem_read(0x20075013,1)))
 total=0
 for length,flag,nw,nt in ((0,0,0,0),(1,0,0,0),(12,1,0,0),(17,0,0,0),(13,1,0,0),
                           (1,0,1,0),(1,0,0,1)):
  for mask in (0,1,2,4,7):
   original=run(True,length,flag,mask,nw,nt);candidate=run(False,length,flag,mask,nw,nt)
   assert original==candidate,(length,flag,mask,nw,nt,original,candidate)
   total+=1
 print('PASS_AUDIO_PACKET_PACK_LOGS',total)
