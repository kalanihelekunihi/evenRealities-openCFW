#!/usr/bin/env python3
"""Bounded native/C sync callback install and receiver restart."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/sync_reset.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
data={'g2_uart_sync_driver':0x20074610,'g2_uart_sync_started':0x20074fc9,
      'g2_uart_sync_semaphore_handle':0x2007461c,'g2_uart_sync_mutex':0x20074620,
      'g2_uart_sync_callback_cell':0x20074618,'g2_uart_sync_buffer':0x20000d9c}
children={'audio_uart_sync_sem_new':0x44989a,'audio_uart_mutex_new':0x44971c,
          'audio_uart_sync_driver_bind':0x58dae4,'g2_codec_pin_function':0x480f0c,
          'audio_uart_sync_driver_mode':0x58dbb8,'audio_uart_sync_driver_buffer':0x58e09e,
          'audio_uart_sync_driver_prepare':0x58ddd6,'audio_uart_sync_hal0':0x5849f2,
          'audio_uart_sync_hal1':0x584a10,'audio_uart_sync_hal2':0x5849d4,
          'audio_uart_sync_driver_baud':0x58e782,'audio_uart_sync_finalize':0x584df4}
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'sync.o';p=Path(td)/'sync.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs=[f'--defsym={name}=0x{address:x}' for name,address in data.items()]
 defs += [f'--defsym={name}=0x{(0x101101+i*16):x}' for i,name in enumerate(children)]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*defs,'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 new={0x101100+i*16:name for i,name in enumerate(children)}
 old={addr:name for name,addr in children.items()}
 def run(native,which,driver,callback,sem_present=1,mutex_present=1,bind_success=True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(data['g2_uart_sync_driver'],driver.to_bytes(4,'little'))
  u.mem_write(data['g2_uart_sync_started'],b'\x00')
  u.mem_write(data['g2_uart_sync_callback_cell'],(0x20040001).to_bytes(4,'little'))
  u.mem_write(data['g2_uart_sync_semaphore_handle'],(0x20046000 if sem_present else 0).to_bytes(4,'little'))
  u.mem_write(data['g2_uart_sync_mutex'],(0x20047000 if mutex_present else 0).to_bytes(4,'little'))
  calls=[]
  def cut(uc,address,size,user):
   name=(old if native else new).get(address)
   if name:
    arity={'audio_uart_sync_sem_new':3,'audio_uart_mutex_new':1,
           'audio_uart_sync_driver_bind':2,'g2_codec_pin_function':2,
           'audio_uart_sync_driver_mode':3,'audio_uart_sync_driver_buffer':2,
           'audio_uart_sync_driver_prepare':3,'audio_uart_sync_hal0':1,
           'audio_uart_sync_hal1':2,'audio_uart_sync_hal2':1,
           'audio_uart_sync_driver_baud':2,'audio_uart_sync_finalize':0}[name]
    args=(uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_R1),uc.reg_read(A.UC_ARM_REG_R2))
    calls.append((name,*args[:arity]))
    if name=='audio_uart_sync_driver_bind' and bind_success:
     uc.mem_write(data['g2_uart_sync_driver'],(0x20050000).to_bytes(4,'little'))
    result=(0x20046000 if name=='audio_uart_sync_sem_new' else
            0x20047000 if name=='audio_uart_mutex_new' else
            2 if name=='audio_uart_sync_driver_mode' else
            4 if name=='g2_codec_pin_function' else
            0 if name!='audio_uart_sync_driver_bind' or bind_success else 1)
    uc.reg_write(A.UC_ARM_REG_R0,result)
    uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cut)
  u.reg_write(A.UC_ARM_REG_R0,callback);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  addr=({0:0x584bc0,1:0x584c8c,2:0x584db6}[which]) if native else syms['audio_uart_sync_reset'+str(which)]
  u.emu_start(addr|1,0x101ff0,count=300)
  return (u.reg_read(A.UC_ARM_REG_R0) if which!=1 else 0,
          u.mem_read(data['g2_uart_sync_started'],1),u.mem_read(data['g2_uart_sync_callback_cell'],4),
          u.mem_read(data['g2_uart_sync_driver'],4),
          u.mem_read(data['g2_uart_sync_semaphore_handle'],4),
          u.mem_read(data['g2_uart_sync_mutex'],4),calls)
 n=0
 for callback in (0,0x101101,0x20045001):
  a=run(True,1,0,callback);b=run(False,1,0,callback);assert a==b,(1,callback,a,b);n+=1
 for driver in (0,0x20050000):
  a=run(True,2,driver,0);b=run(False,2,driver,0);assert a==b,(2,driver,a,b);n+=1
 for sem_present in (0,1):
  for mutex_present in (0,1):
   for bind_success in (False,True):
    a=run(True,0,0,0,sem_present,mutex_present,bind_success)
    b=run(False,0,0,0,sem_present,mutex_present,bind_success)
    assert a==b,(0,sem_present,mutex_present,bind_success,a,b)
    n+=1
 print('PASS_AUDIO_UART_SYNC_RESET',n)
