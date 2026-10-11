#!/usr/bin/env python3
"""Native/C GX8002 unpacker with error/success diagnostic ABI checks."""
from pathlib import Path
import struct,subprocess,tempfile,zlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/transaction_extract_source_candidate/extract.c'
BASE=Path('/tmp/opencfw-codec-response/drain.elf')
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with BASE.open('rb') as stream:
 elf=ELFFile(stream);base_segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
def frame(body=b'',flag=0,declared=None,magic=b'BUXX',bad_head=False,bad_body=False):
 trailer=struct.pack('<I',zlib.crc32(body)^(1 if bad_body else 0)) if flag&1 else b''
 count=len(body)+len(trailer) if declared is None else declared
 header=magic+struct.pack('<HBBH',0x1234,7,flag,count)
 return header+struct.pack('<I',zlib.crc32(header)^(1 if bad_head else 0))+body+trailer
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'extract.o';path=directory/'extract.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'codec_allocate':0x474cd3,'codec_release':0x474d17,
       'codec_crc32':0x100053,
       'audio_dump_hex':0x101011,'audio_log_flags':0x101021,
       'audio_log_extended':0x101031,'audio_log_simple':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={key}=0x{value:x}' for key,value in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,wire,available,mask,alloc_fail=False,null_wire=False,null_message=False):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x30000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in base_segments+segments:unit.mem_write(address,data)
  unit.mem_write(0x20040000,wire+bytes([0xcc])*(128-len(wire)))
  unit.mem_write(0x20040100,bytes([0xa5])*26)
  unit.mem_write(0x20040200,bytes([0xdd])*32)
  for reg,value in ((A.UC_ARM_REG_R0,0 if null_wire else 0x20040000),
                    (A.UC_ARM_REG_R1,available),(A.UC_ARM_REG_R2,0 if null_message else 0x20040100),
                    (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
   unit.reg_write(reg,value)
  targets={0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'simple',
           0x43dacc:'dump',0x474cd2:'allocate',0x474d16:'free'}
  if not native:targets.update({0x101020:'flags',0x101030:'extended',0x101040:'simple',0x101010:'dump'})
  calls=[];done=[False]
  def string(pointer):
   value=bytearray()
   for offset in range(256):
    byte=unit.mem_read(pointer+offset,1)[0]
    if byte==0:break
    value.append(byte)
   return bytes(value)
  def argc(fmt):
   if b'Unpack message:' in fmt:return 7
   if b'mismatch:' in fmt or b'mismatch: expected=' in fmt:return 2
   if b'content too large' in fmt or b'content length' in fmt:return 1
   return 0
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=targets.get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)]
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if kind=='flags':calls.append((kind,));cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif kind=='allocate':calls.append((kind,r[0]));cpu.reg_write(A.UC_ARM_REG_R0,0 if alloc_fail else 0x20040200)
   elif kind=='free':calls.append((kind,r[0]));cpu.reg_write(A.UC_ARM_REG_R0,0)
   elif kind=='dump':calls.append((kind,string(r[0]),r[1],r[2],r[3]))
   elif kind=='extended':
    line=int.from_bytes(cpu.mem_read(sp,4),'little');fmt=string(int.from_bytes(cpu.mem_read(sp+4,4),'little'))
    args=tuple(int.from_bytes(cpu.mem_read(sp+8+4*i,4),'little') for i in range(argc(fmt)))
    calls.append((kind,r[0],string(r[1]),string(r[2]),string(r[3]),line,fmt,args))
   else:
    fmt=string(r[1]);n=argc(fmt)
    args=tuple(([r[3]] if n else [])+[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(max(0,n-1))])
    calls.append((kind,r[0],fmt,string(r[2]),args))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  unit.emu_start((0x57bd06 if native else symbols['audio_transaction_extract'])|1,0,count=12000)
  assert done[0],(native,available,mask)
  return (unit.reg_read(A.UC_ARM_REG_R0),calls,bytes(unit.mem_read(0x20040100,26)),
          bytes(unit.mem_read(0x20040200,20)))
 fixtures=[(frame(),14,False,False,False),
           (frame(magic=b'BUXY'),14,False,False,False),
           (frame(b'AB'),15,False,False,False),
           (frame(b'AB',bad_head=True),16,False,False,False),
           (frame(bytes(range(17))),31,False,False,False),
           (frame(b'AB'),16,True,False,False),
           (frame(b'AB',flag=1,bad_body=True),20,False,False,False),
           (frame(b'AB',flag=1),20,False,False,False),
           (frame(b'AB'),16,False,True,False),
           (frame(b'AB'),16,False,False,True)]
 total=0
 for wire,available,alloc_fail,null_wire,null_message in fixtures:
  for mask in (0,1,2,4,7):
   original=run(True,wire,available,mask,alloc_fail,null_wire,null_message)
   candidate=run(False,wire,available,mask,alloc_fail,null_wire,null_message)
   assert original==candidate,(wire.hex()[:30],available,mask,alloc_fail,null_wire,null_message,original,candidate)
   total+=1
 print('PASS_AUDIO_TRANSACTION_EXTRACT',total)
