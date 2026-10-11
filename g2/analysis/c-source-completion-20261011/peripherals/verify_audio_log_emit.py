#!/usr/bin/env python3
"""Native/C packet-ring emit comparison with identical lock/copy/wake cuts."""
from pathlib import Path
import struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_log_format_source_candidate/emit.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'emit.o';path=Path(td)/'emit.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(obj)],check=True)
 defs={'g2_audio_log_ring_state':0x200004c8,'audio_log_lock_state':0x20074388,'audio_log_lock':0x101011,'audio_log_unlock':0x101021,'audio_log_flags':0x101031,'g2_lfs_memcpy':0x101041,'audio_log_wake_allowed':0x101051,'audio_log_transport_ready':0x101061,'audio_log_transport_wake':0x101071}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as f:
  e=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_log_emit')
 def run(native,read,write,length,flags,lockok,wake,ready):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x200004c8,struct.pack('<4I',0x20050000,256,read,write));u.mem_write(0x20074388,struct.pack('<I',0x20040200))
  u.mem_write(0x20050000,bytes([0xa5])*256);u.mem_write(0x20040000,bytes(range(256)))
  for reg,value in ((A.UC_ARM_REG_R0,0x20040000),(A.UC_ARM_REG_R1,length),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,value)
  old={0x441750:'lock',0x441710:'unlock',0x43d0ce:'flags',0x439be4:'copy',0x443484:'wake_allowed',0x4487ac:'ready',0x448f7c:'wake'}
  new={0x101010:'lock',0x101020:'unlock',0x101030:'flags',0x101040:'copy',0x101050:'wake_allowed',0x101060:'ready',0x101070:'wake'}
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(4)];ret=0
   if kind=='lock':calls.append((kind,r[0],r[1]));ret=lockok
   elif kind=='unlock':calls.append((kind,r[0]))
   elif kind=='flags':calls.append((kind,));ret=flags
   elif kind=='copy':calls.append((kind,r[0],r[1],r[2]));cpu.mem_write(r[0],bytes(cpu.mem_read(r[1],r[2])))
   elif kind=='wake_allowed':calls.append((kind,));ret=wake
   elif kind=='ready':calls.append((kind,));ret=ready
   else:calls.append((kind,))
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x43ca50 if native else entry)|1,0,count=10000);assert done[0]
  return calls,bytes(u.mem_read(0x200004c8,16)),bytes(u.mem_read(0x20050000,256))
 count=0
 for read,write,length,flags,lockok,wake,ready in itertools.product((10,100,240),(0,20,90,230),(0,10,40,80,250),(0,1,4,5),(0,1),(0,1),(0,1)):
  a=run(True,read,write,length,flags,lockok,wake,ready);b=run(False,read,write,length,flags,lockok,wake,ready)
  assert a==b,(read,write,length,flags,lockok,wake,ready,a,b)
  count+=1
 print('PASS_AUDIO_LOG_EMIT',count)
