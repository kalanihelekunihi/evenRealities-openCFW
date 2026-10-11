#!/usr/bin/env python3
"""One-command native/C timer drain comparisons at identical lower cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/timer_drain_full_source_candidate/drain.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'drain.o';path=Path(td)/'drain.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'g2_audio_timer_command_queue':0x20074ab0,'audio_timer_queue_receive':0x101011,'audio_timer_list_remove':0x101021,'audio_timer_sample_time':0x101031,'audio_timer_reload_insert':0x101041,'stock_timer_reload':0x101051,'audio_timer_heap_free':0x101061,'offline_assert':0x101081}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,command,flags,container,insert_return):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_write(0x438000,STOCK)
  u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for addr,data in segs:u.mem_write(addr,data)
  u.mem_write(0x20074ab0,struct.pack('<I',0x20040300))
  timer=bytearray(44);struct.pack_into('<I',timer,20,container);struct.pack_into('<I',timer,24,7);struct.pack_into('<I',timer,32,0x101071);timer[40]=flags
  u.mem_write(0x20040100,bytes(timer));u.mem_write(0x20040300,b'\0'*32)
  message=struct.pack('<iIII',command,0x101071 if command<0 else 80,0x20040100,0x11223344)
  for reg,value in ((A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,value)
  old={0x441b0a:'queue',0x4560e8:'remove',0x47e916:'time',0x47e93c:'insert',0x47e812:'reload',0x456210:'free',0x5fa0a4:'assert'}
  new={0x101010:'queue',0x101020:'remove',0x101030:'time',0x101040:'insert',0x101050:'reload',0x101060:'free',0x101080:'assert'}
  calls=[];queued=[False];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if pc==0x101070:kind='callback'
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)];sp=cpu.reg_read(A.UC_ARM_REG_SP);ret=0
   if kind=='queue':
    calls.append(('queue',r[0],r[2]));
    if not queued[0]:cpu.mem_write(r[1],message);queued[0]=True;ret=1
   elif kind=='remove':calls.append(('remove',r[0]))
   elif kind=='time':cpu.mem_write(r[0],struct.pack('<I',0));calls.append(('time',));ret=100
   elif kind=='insert':calls.append(('insert',r[0],r[1],r[2],r[3]));ret=insert_return
   elif kind=='reload':calls.append(('reload',r[0],r[1],r[2]))
   elif kind=='free':calls.append(('free',r[0]))
   elif kind=='callback':calls.append(('callback',r[0],r[1]))
   else:calls.append(('assert',));cpu.emu_stop();return
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x47e97a if native else sym['audio_daemon_drain_commands'])|1,0,count=10000)
  assert done[0],(native,command,flags,container,insert_return,calls)
  return calls,bytes(u.mem_read(0x20040100,44))
 count=0
 for command in (-1,1,2,3,4,5,6,7,8,9,10):
  for flags,container,insert_return in ((0,0,0),(4,0x20040500,1),(2,0,1)):
   a=run(True,command,flags,container,insert_return)
   b=run(False,command,flags,container,insert_return)
   assert a==b,(command,flags,container,insert_return,a,b)
   count+=1
 print('PASS_AUDIO_TIMER_DRAIN_FULL',count)
