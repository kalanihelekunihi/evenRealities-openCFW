"""Actual C/native SCB cache maintenance MMIO sequence on bounded geometry."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_cache_maintenance',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_cache_maintenance.c'),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for enabled,range_words,clean,geometry in ((0,None,1,0),(1,None,0,0),(1,None,1,0),(1,None,1,0x2008),(1,(0x20080213,0),1,0),(1,(0x20080213,1),0,0),(1,(0x20080213,33),1,0)):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
   u.mem_write(0xe000ed14,struct.pack('<I',enabled<<16));u.mem_write(0xe000ed80,struct.pack('<I',geometry))
   events=[]
   def hook(uc,access,a,n,v,_):
    if a>=0xe000e000:events.append((a,n,v&((1<<(n*8))-1)))
   u.hook_add(UC_HOOK_MEM_WRITE,hook)
   arg=0
   if range_words:
    arg=0x20080000;u.mem_write(arg,struct.pack('<II',*range_words))
   u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_R1,clean)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_privacy_cache_maintenance'] if c else 0x475014)|1,0x600000,count=100000)
   obs.append(events)
  assert obs[0]==obs[1],(enabled,range_words,clean,geometry,obs)
  print('PASS cache',enabled,range_words,clean,geometry,len(obs[0]))
