#!/usr/bin/env python3
"""Native/C SyncModuleReceivedDataHandler branches with controlled log/module children."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/process_receive.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'receive.o';p=Path(td)/'receive.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_uart_sync_module':0x200749c4,'g2_uart_sync_module_name':0x77c07c,'g2_uart_sync_source_file':0x705fb8,'g2_uart_sync_receive_function':0x765890,'g2_uart_sync_uninit_message':0x783c30,'g2_uart_sync_uninit_short':0x7440c8,'audio_log_flags':0x101011,'audio_log_extended':0x101021,'compressed_log_output':0x101031,'audio_uart_module_receive':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_process_receive')
 old={0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'short',0x491b9a:'receive'};new={0x101010:'flags',0x101020:'extended',0x101030:'short',0x101040:'receive'}
 def run(native,handle,flags,length):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x200749c4,(0x20050000 if handle else 0).to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,0x20060000);u.reg_write(A.UC_ARM_REG_R1,length);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind:
    args=tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    calls.append((kind,(() if kind=='flags' else args[:3] if kind in ('short','receive') else args)))
    cpu.reg_write(A.UC_ARM_REG_R0,flags if kind=='flags' else 0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x45d4dc if native else entry)|1,0,count=1000);assert done[0]
  return calls
 count=0
 for h,f,n in itertools.product((0,1),(0,1,2,4,7),(0,1,16,1024)):
  a=run(True,h,f,n);b=run(False,h,f,n);assert a==b,(h,f,n,a,b);count+=1
 print('PASS_AUDIO_UART_PROCESS_RECEIVE',count)
