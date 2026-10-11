#!/usr/bin/env python3
"""Bounded native/C ring-status branch and logger comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/service_prepare6.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
old={0x4a2fdc:'ready',0x4a2914:'active',0x47cf28:'idle',0x47ced6:'sync',
     0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'compressed'}
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'candidate.o';p=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 names=('audio_uart_ring_mac_ready','audio_uart_ring_active','audio_uart_ring_sync_idle','audio_uart_ring_sync_active','audio_log_flags','audio_log_extended','compressed_log_output')
 defs={name:0x101101+i*16 for i,name in enumerate(names)}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];entry=next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='audio_uart_service_prepare6')
 new={0x101100+i*16:label for i,label in enumerate(('ready','active','idle','sync','flags','extended','compressed'))}
 def run(native,ready,active,mask):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  calls=[]
  def string_at(uc,addr):return bytes(uc.mem_read(addr,160)).split(b'\0')[0]
  def hook(uc,address,size,user):
   kind=(old if native else new).get(address)
   if not kind:return
   sp=uc.reg_read(A.UC_ARM_REG_SP)
   if kind=='extended':
    line=int.from_bytes(uc.mem_read(sp,4),'little');msg=int.from_bytes(uc.mem_read(sp+4,4),'little')
    calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                  string_at(uc,uc.reg_read(A.UC_ARM_REG_R2)),string_at(uc,uc.reg_read(A.UC_ARM_REG_R3)),line,string_at(uc,msg)))
   elif kind=='compressed':
    calls.append((kind,uc.reg_read(A.UC_ARM_REG_R0),string_at(uc,uc.reg_read(A.UC_ARM_REG_R1)),
                  string_at(uc,uc.reg_read(A.UC_ARM_REG_R2))))
   else:calls.append((kind,))
   uc.reg_write(A.UC_ARM_REG_R0,ready if kind=='ready' else active if kind=='active' else mask if kind=='flags' else 0)
   uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x47d818 if native else entry)|1,0x101ff0,count=1000)
  return calls
 n=0
 for ready in (0,1):
  for active in (0,1):
   for mask in (0,1,2,4,7):
    a=run(True,ready,active,mask);b=run(False,ready,active,mask)
    assert a==b,(ready,active,mask,a,b);n+=1
 print('PASS_AUDIO_UART_SERVICE_PREPARE6',n)
