"""Actual C/native file facade guard paths with allocator and mutex cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
LOWERS={'codec_allocate':0x474cd2,'audio_file_heap_free':0x474d16,
 'audio_file_mutex_acquire':0x4497b6,'audio_file_mutex_release':0x44981c,
 'audio_file_lfs_open':0x4cfa94,'audio_file_lfs_read':0x4cfb40,
 'audio_file_lfs_seek':0x4cfbb2,'audio_file_lfs_tell':0x4cfbe8}
FUN={'open':('audio_file_open',0x474550),'read':('audio_file_read',0x474634),
 'seek':('audio_file_seek',0x474814),'tell':('audio_file_tell',0x474870)}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('#include <stdint.h>\nuint8_t audio_file_lfs_context[4];void *audio_file_api_mutex;\n'+
 ''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("'+
 ('movs r0, #1' if n=='audio_file_mutex_acquire' else 'movs r0, #0')+'\\n bx lr");}\n' for n in LOWERS))
 elf=Path(td)/'file.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_open',str(ROOT/'components/audio/uart_thread_source_candidate/display_file_api.c'),str(shim),'-o',str(elf)],check=True)
 syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,kind,variant):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000);F=0x20010000;u.mem_write(F,b'\0'*128)
  args={'open':(0,0,0,0),'read':(0,1,2,F),'seek':(F,0,3 if variant=='invalid' else 0,0),
        'tell':(0 if variant=='null' else F,0,0,0)}[kind]
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if not candidate:
   def bypass(uc,address,size,_):
    if address in LOWERS.values():
     uc.reg_write(UC_ARM_REG_R0,1 if address==0x4497b6 else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,bypass)
  name,stock=FUN[kind];u.emu_start((syms[name] if candidate else stock)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(F,128))
 for kind,variant in [('open','allocation-fail'),('read','mutex-fail'),('seek','invalid'),
                      ('seek','mutex-fail'),('tell','null'),('tell','mutex-fail')]:
  a=run(False,kind,variant);b=run(True,kind,variant)
  assert a==b,(kind,variant,a[0],b[0]);print('PASS file API',kind,variant)
