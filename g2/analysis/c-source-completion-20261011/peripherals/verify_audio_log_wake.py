#!/usr/bin/env python3
"""Original-byte wake predicates and event signaling versus C."""
from pathlib import Path
import struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_log_format_source_candidate/wake.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'w.o';p=Path(td)/'w.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_audio_log_wake_enabled':0x20074f2c,'g2_audio_log_transport_bits':0x20075043,'g2_audio_log_transport_alt':0x20072730,'g2_audio_log_event_handle':0x20074570,'g2_log_transport_signal':0x101011}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,which,enabled,bits,alt,handle):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20074f2c,bytes([enabled]));u.mem_write(0x20075043,bytes([bits]));u.mem_write(0x20072730,bytes([alt]));u.mem_write(0x20074570,struct.pack('<I',handle))
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   if pc in ((0x4495e4,) if native else (0x101010,)):
    calls.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  native_entry={'allowed':0x443484,'ready':0x4487ac,'wake':0x448f7c}[which]
  source_entry={'allowed':'audio_log_wake_allowed','ready':'audio_log_transport_ready','wake':'audio_log_transport_wake'}[which]
  u.emu_start((native_entry if native else sym[source_entry])|1,0,count=1000);assert done[0]
  return (u.reg_read(A.UC_ARM_REG_R0) if which!='wake' else None,calls)
 count=0
 for enabled,bits,alt,handle,which in itertools.product((0,1,2,255),(0,1,2,3,4,255),(0,1,2),(0,0x20040700),('allowed','ready','wake')):
  a=run(True,which,enabled,bits,alt,handle);b=run(False,which,enabled,bits,alt,handle)
  assert a==b,(which,enabled,bits,alt,handle,a,b)
  count+=1
 print('PASS_AUDIO_LOG_WAKE',count)
