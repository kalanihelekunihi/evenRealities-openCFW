#!/usr/bin/env python3
"""Native/C UART announcement packet under controlled version/nonce/checksum."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/service_announce.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'announce.o';p=Path(td)/'announce.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'audio_uart_service_version':0x101011,'audio_uart_service_nonce':0x101021,'audio_uart_checksum_copy':0x101031,'audio_uart_handshake_send':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_service_prepare3')
 old={0x45a568:'version',0x4ac776:'nonce',0x439be4:'checksum',0x465480:'send'};new={0x101010:'version',0x101020:'nonce',0x101030:'checksum',0x101040:'send'}
 def run(native,command,version):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,command);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind:
    if kind=='version':calls.append(('version',));cpu.reg_write(A.UC_ARM_REG_R0,version)
    elif kind=='nonce':
     p=cpu.reg_read(A.UC_ARM_REG_R0);cpu.mem_write(p,bytes.fromhex('12345678'));calls.append(('nonce',));cpu.reg_write(A.UC_ARM_REG_R0,0)
    elif kind=='checksum':
     dst=cpu.reg_read(A.UC_ARM_REG_R0);src=cpu.reg_read(A.UC_ARM_REG_R1);size=cpu.reg_read(A.UC_ARM_REG_R2)
     calls.append(('checksum',size,bytes(cpu.mem_read(src,4))));cpu.mem_write(dst,bytes.fromhex('9abcdef0'));cpu.reg_write(A.UC_ARM_REG_R0,dst)
    else:
     sp=cpu.reg_read(A.UC_ARM_REG_SP);buf=cpu.reg_read(A.UC_ARM_REG_R1)
     calls.append(('send',cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(buf,8)),cpu.reg_read(A.UC_ARM_REG_R2),cpu.reg_read(A.UC_ARM_REG_R3),int.from_bytes(cpu.mem_read(sp,4),'little')))
     cpu.reg_write(A.UC_ARM_REG_R0,0)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x4ac828 if native else entry)|1,0,count=1500);assert done[0]
  return calls
 count=0
 for command,version in itertools.product((0,3,255),(0,1,2,255)):
  a=run(True,command,version);b=run(False,command,version);assert a==b,(command,version,a,b);count+=1
 print('PASS_AUDIO_UART_SERVICE_ANNOUNCE',count)
