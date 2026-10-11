#!/usr/bin/env python3
"""Native/C GX8002 UART exchange wrapper with diagnostic ABI comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/transaction_exchange_source_candidate/exchange.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'exchange.o';path=directory/'exchange.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'codec_response_read':0x101011,'audio_dump_hex':0x101021,
       'audio_log_flags':0x101031,'audio_log_extended':0x101041,
       'audio_log_simple':0x101051}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={key}=0x{value:x}' for key,value in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,buffer,length,status,mask):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x20000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in segments:unit.mem_write(address,data)
  unit.mem_write(0x20007000,b'\xee\xee')
  for reg,value in ((A.UC_ARM_REG_R0,buffer),(A.UC_ARM_REG_R1,length),
                    (A.UC_ARM_REG_R2,0x20007000),(A.UC_ARM_REG_R3,77),
                    (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
   unit.reg_write(reg,value)
  targets=({0x57c1fc:'read',0x43dacc:'dump',0x43d0ce:'flags',
            0x43d574:'extended',0x43ce9e:'simple'} if native else
           {0x101010:'read',0x101020:'dump',0x101030:'flags',
            0x101040:'extended',0x101050:'simple'})
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
   if kind=='read':calls.append((kind,r[0],r[1],r[2]));cpu.reg_write(A.UC_ARM_REG_R0,status&0xffffffff)
   elif kind=='flags':calls.append((kind,));cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif kind=='dump':calls.append((kind,string(r[0]),r[1],r[2],r[3]));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif kind=='extended':
    line=int.from_bytes(cpu.mem_read(sp,4),'little');fmt=string(int.from_bytes(cpu.mem_read(sp+4,4),'little'))
    arg=int.from_bytes(cpu.mem_read(sp+8,4),'little')
    calls.append((kind,r[0],string(r[1]),string(r[2]),string(r[3]),line,fmt,arg))
   else:calls.append((kind,r[0],string(r[1]),string(r[2]),r[3]))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  unit.emu_start((0x57c442 if native else symbols['audio_transaction_exchange'])|1,0,count=350)
  assert done[0],(native,buffer,length,status,mask)
  return unit.reg_read(A.UC_ARM_REG_R0),calls,bytes(unit.mem_read(0x20007000,2))
 total=0
 for buffer,length,status in ((0,30,10),(0x20006000,0,10),(0x20006000,30,-1),
                              (0x20006000,30,0),(0x20006000,30,14)):
  for mask in (0,1,2,4,7):
   original=run(True,buffer,length,status,mask);candidate=run(False,buffer,length,status,mask)
   assert original==candidate,(buffer,length,status,mask,original,candidate)
   total+=1
 print('PASS_AUDIO_TRANSACTION_EXCHANGE',total)
