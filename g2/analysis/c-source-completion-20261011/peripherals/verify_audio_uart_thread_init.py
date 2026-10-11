#!/usr/bin/env python3
"""Bounded UART thread initialization failure comparison with native bytes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/thread.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'thread.o';p=Path(td)/'thread.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 names=[l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(o)],text=True).splitlines()]
 data={'g2_uart_thread_mutex':0x20074b18,'g2_uart_thread_event':0x20074b10,'g2_uart_thread_transport':0x20074b14,'g2_uart_thread_initialize_callback':0x20000658,'g2_uart_command':0x20074080,'g2_uart_rx_buffer':0x2006c930}
 stubs={'audio_uart_mutex_new':0x101010,'audio_uart_event_new':0x101020,'audio_uart_transport_new':0x101030,'audio_uart_ready':0x101040,'audio_log_flags':0x101050}
 vals={n:data.get(n,stubs.get(n,0x101100+i*0x10)) for i,n in enumerate(names)}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in vals.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='uart_thread_handler')
 old={0x44971c:'mutex',0x449590:'event',0x57df7c:'transport',0x45e8d0:'ready',0x43d0ce:'flags'}
 new={0x101010:'mutex',0x101020:'event',0x101030:'transport',0x101040:'ready',0x101050:'flags'}
 def run(native,step):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x40000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20000658,(0x101a01).to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,0);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  extended_old={0x101a00:'callback',0x444720:'prepare0',0x5417c4:'prepare1',0x584e94:'prepare2',0x4ac828:'prepare3',0x45a570:'mode',0x471528:'prepare4',0x47e4a6:'prepare5',0x47d818:'prepare6',0x4ff99a:'prepare7',0x501d5c:'prepare8',0x501066:'prepare9',0x44969c:'wait',0x449642:'clear',0x45e664:'event2',0x45d4b8:'event4'}
  extended_new={0x101a00:'callback',**{v & ~1:k.removeprefix('audio_uart_service_').replace('audio_uart_','') for k,v in vals.items() if k.startswith('audio_uart_service_')}}
  extended_new.update({vals[k]&~1:n for k,n in [('audio_event_wait','wait'),('audio_uart_event_clear','clear'),('audio_uart_process_event2','event2'),('audio_uart_process_event4','event4')]})
  calls=[];done=[False];waits=[0]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind is None and step>=4: kind=(extended_old if native else extended_new).get(pc)
   if kind:
    if kind=='wait':
     waits[0]+=1
     if waits[0]==2:done[0]=True;cpu.emu_stop();return
    calls.append((kind,cpu.reg_read(A.UC_ARM_REG_R0)))
    result={'mutex':0 if step==0 else 0x20052000,'event':0 if step==1 else 0x20053000,'transport':0 if step==2 else 0x20054000,'ready':0 if step>=4 else 1,'flags':0,'mode':0,'wait':(0,2,4,6)[step-4] if step>=4 else 0}.get(kind,0)
    cpu.reg_write(A.UC_ARM_REG_R0,result);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x5417d6 if native else entry)|1,0,count=2000);assert done[0],step
  cells=tuple(int.from_bytes(u.mem_read(a,4),'little') for a in (0x20074b18,0x20074b10,0x20074b14))
  return calls,cells
 for step in range(8):
  a=run(True,step);b=run(False,step);assert a==b,(step,a,b)
 print('PASS_AUDIO_UART_THREAD_INIT_AND_EVENT 8')
