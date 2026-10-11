#!/usr/bin/env python3
"""Bounded original-byte/C onboarding flag RPC and diagnostics."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/service_prepare5.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'candidate.o';p=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_onboarding_flag':0x20000040,'audio_uart_handshake_send':0x101011,
       'audio_log_flags':0x101021,'audio_log_extended':0x101031,
       'compressed_log_output':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];entry=next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='audio_uart_service_prepare5')
 old={0x465480:'send',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed'}
 new={0x101010:'send',0x101020:'flags',0x101030:'extended',0x101040:'compressed'}
 def run(native,flag,mask):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20000040,bytes([flag]));calls=[]
  def string_at(uc,address):return bytes(uc.mem_read(address,160)).split(b'\0')[0]
  def hook(uc,address,size,user):
   kind=(old if native else new).get(address)
   if not kind:return
   sp=uc.reg_read(A.UC_ARM_REG_SP)
   if kind=='send':
    calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_R1),2)),
                  uc.reg_read(A.UC_ARM_REG_R2),uc.reg_read(A.UC_ARM_REG_R3),int.from_bytes(uc.mem_read(sp,4),'little')))
   elif kind=='extended':
    line=int.from_bytes(uc.mem_read(sp,4),'little')
    msg=int.from_bytes(uc.mem_read(sp+4,4),'little')
    arg=int.from_bytes(uc.mem_read(sp+8,4),'little')
    calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                  string_at(uc,uc.reg_read(A.UC_ARM_REG_R2)),string_at(uc,uc.reg_read(A.UC_ARM_REG_R3)),
                  line,string_at(uc,msg),arg))
   elif kind=='compressed':
    calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                  string_at(uc,uc.reg_read(A.UC_ARM_REG_R2)),uc.reg_read(A.UC_ARM_REG_R3)))
   else:calls.append((kind,))
   uc.reg_write(A.UC_ARM_REG_R0,mask if kind=='flags' else 0)
   uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x47e4a6 if native else entry)|1,0x101ff0,count=1000)
  return calls
 n=0
 for flag in (0,1,255):
  for mask in (0,1,2,4,7):
   a=run(True,flag,mask);b=run(False,flag,mask);assert a==b,(flag,mask,a,b);n+=1
 print('PASS_AUDIO_UART_SERVICE_PREPARE5',n)
