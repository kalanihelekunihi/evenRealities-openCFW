#!/usr/bin/env python3
"""Bounded original-byte/C call-order oracle for both public PDM initializers."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pdm_init_source_candidate/init.c';O=D/'codec-pdm-init-m4.o';E=D/'codec-pdm-init-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
children=[('g2_pdm_clock_enable',0x4c31d8,'clock',1),('g2_codec_pin_write',0x53a5be,'pin',2),('g2_pdm_acquire',0x591fac,'acquire',2),('g2_pdm_disable',0x592046,'disable',3),('g2_pdm_configure',0x5920cc,'configure',2),('g2_pdm_prepare_clock',0x592462,'prepare_clock',2),('g2_pdm_prepare_dma',0x592556,'prepare_dma',2),('g2_codec_irq_priority',0x57b484,'priority',2),('g2_codec_irq_enable',0x57b444,'irq_enable',1),('g2_pdm_irq_prepare',0x592230,'irq_prepare',1),('g2_pdm_start',0x59235e,'start',2),('audio_log_flags',0x43d0ce,'flags',0),('audio_log_extended',0x43d574,'extended',0),('audio_log_simple',0x43ce9e,'simple',0)]
data={'g2_pdm_production_initialized':0x20074fbb,'g2_pdm_production_handle':0x20074550,'g2_pdm_production_config':0x20000928,'g2_pdm_production_irq':0x78f55c,'g2_pdm_production_descriptor':0x20000944,'g2_pdm_alternate_initialized':0x20074fba,'g2_pdm_alternate_handle':0x2007454c,'g2_pdm_alternate_config':0x20000900,'g2_pdm_alternate_irq':0x78f55a,'g2_pdm_alternate_descriptor':0x2000091c}
source_calls={0x101000+0x10*i:(k,n) for i,(_s,_a,k,n) in enumerate(children)}
stock_calls={a:(k,n) for _s,a,k,n in children}
args=['arm-none-eabi-ld','-Ttext=0x100000']
args += [f'--defsym={n}={a:#x}' for n,a in data.items()]
args += [f'--defsym={n}={a+1:#x}' for a,(n,_,_,_) in zip(source_calls,children)]
subprocess.run(args+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def cstr(u,a):return bytes(u.mem_read(a,256)).split(b'\0',1)[0].decode('ascii')
def run(original,variant,initial,flags):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 u.mem_write(0x438000,stock)
 if not original:
  for a,b in segs:u.mem_write(a,b)
 p=variant==0;state=0x20074fbb if p else 0x20074fba;cell=0x20074550 if p else 0x2007454c;irq=0x78f55c if p else 0x78f55a
 u.mem_write(state,bytes([initial]));put(u,cell,0);u.mem_write(irq,(44 if p else 45).to_bytes(2,'little'))
 u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 events=[];reads=[0];done=[False];calls=(stock_calls.copy() if original else source_calls)
 if original and not p:
  calls[0x57b748]=calls.pop(0x57b484)
  calls[0x57b704]=calls.pop(0x57b444)
 def hook(cpu,pc,_s,_):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  item=calls.get(pc)
  if item is None:return
  kind,argc=item;regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP)
  if kind=='flags':events.append((kind,));result=flags[reads[0]%len(flags)];reads[0]+=1
  elif kind=='extended':events.append((kind,regs[0],cstr(cpu,regs[1]),cstr(cpu,regs[2]),cstr(cpu,regs[3]),word(cpu,sp),cstr(cpu,word(cpu,sp+4))));result=0
  elif kind=='simple':events.append((kind,regs[0],cstr(cpu,regs[1]),cstr(cpu,regs[2])));result=0
  else:
   events.append((kind,*regs[:argc]));result=0
   if kind=='acquire':put(cpu,regs[1],0x20001000)
  cpu.reg_write(A.UC_ARM_REG_R0,result);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=(0x57b4a8 if p else 0x57b770) if original else sym['audio_pdm_enable_primary' if p else 'audio_pdm_enable_alternate']
 try:u.emu_start(entry|1,0,count=600)
 except Exception as ex:raise RuntimeError((original,variant,initial,flags,hex(u.reg_read(A.UC_ARM_REG_PC)),events)) from ex
 assert done[0],(original,variant,initial,flags)
 return bytes(u.mem_read(state,1)),word(u,cell),events
n=0
for variant in (0,1):
 for initial in (0,1,2):
  for flags in ((0,),(1,),(2,),(4,),(7,),(0,4,0),(2,0,4)):
   a=run(True,variant,initial,flags);b=run(False,variant,initial,flags)
   assert a==b,(variant,initial,flags,a,b)
   n+=1
print('PASS_AUDIO_CODEC_PDM_INIT',n)
for p in (O,E):p.unlink()
