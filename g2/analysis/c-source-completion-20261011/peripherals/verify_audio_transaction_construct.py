#!/usr/bin/env python3
"""Controlled original-byte/C GX8002 packet construction comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/transaction_construct_source_candidate/construct.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'construct.o';path=directory/'construct.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'g2_audio_tx_packet':0x2007399c,'audio_packet_pack':0x101011,
       'audio_dump_hex':0x101021,'audio_uart_send_bytes':0x101031,
       'audio_log_flags':0x101041,'audio_log_extended':0x101051,
       'audio_log_simple':0x101061}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={key}=0x{value:x}' for key,value in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,code,family,length,flags,failed):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x20000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in segments:unit.mem_write(address,data)
  stack=0x200f0000;unit.mem_write(stack,(flags&0xffffffff).to_bytes(4,'little'))
  for reg,value in ((A.UC_ARM_REG_R0,code),(A.UC_ARM_REG_R1,family),
                    (A.UC_ARM_REG_R2,0x20008000),(A.UC_ARM_REG_R3,length),
                    (A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):
   unit.reg_write(reg,value)
  targets=({0x57bb0a:'pack',0x43dacc:'dump',0x58fb38:'send',0x43d0ce:'flags'} if native else
           {0x101010:'pack',0x101020:'dump',0x101030:'send',0x101040:'flags'})
  calls=[];done=[False]
  def string(pointer):
   value=bytearray()
   for offset in range(64):
    byte=unit.mem_read(pointer+offset,1)[0]
    if byte==0:break
    value.append(byte)
   return bytes(value)
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=targets.get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)]
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if kind=='pack':
    args=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(3)]
    calls.append((kind,*r,*args[:2]))
    cpu.mem_write(args[2],(18).to_bytes(2,'little'))
   elif kind=='dump':calls.append((kind,string(r[0]),r[1],r[2],r[3]))
   elif kind=='send':calls.append((kind,r[0],r[1]))
   else:calls.append((kind,))
   cpu.reg_write(A.UC_ARM_REG_R0,7 if kind==failed else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  unit.emu_start((0x57c0d6 if native else symbols['audio_transaction_construct'])|1,0,count=300)
  assert done[0],(native,code,family,length,flags,failed)
  return unit.reg_read(A.UC_ARM_REG_R0),calls
 total=0
 for args in ((12,0x100,0,0),(0x12345,0x23456,0x33333,0x101),(65535,65535,65535,255)):
  for failure in ('none','pack','send'):
   original=run(True,*args,failure);candidate=run(False,*args,failure)
   assert original==candidate,(args,failure,original,candidate)
   total+=1
 print('PASS_AUDIO_TRANSACTION_CONSTRUCT',total)
