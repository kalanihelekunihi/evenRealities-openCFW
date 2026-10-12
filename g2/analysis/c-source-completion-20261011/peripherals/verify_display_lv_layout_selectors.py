"""Actual ARM C/native style property IDs and result width for flex/grid leaves."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
BASE=ROOT/'components/audio/uart_thread_source_candidate'
SOURCES=[BASE/'display_lv_flex_repos_selectors.c',BASE/'display_lv_grid_selectors.c']
CASES={
 0x48b982:(0x18,False),0x48b98c:(0x19,False),0x48b996:(0x1a,False),
 0x48b9a0:(0x1b,False),0x48b946:(0x6c,False),0x48b950:(0x6d,False),
 0x48b9fc:(0x7e,True),0x48c82e:(0x6c,False),0x48c838:(0x6d,False),
 0x48c856:(0x14,False),0x48c860:(0x15,False),0x48c86a:(0x18,False),
 0x48c874:(0x19,False),0x48c87e:(0x1a,False),0x48c888:(0x1b,False),
 0x48c8a8:(0x27,True),0x48c8b4:(0x82,False),0x48c8be:(0x7f,True),
 0x48c8ca:(0x81,False),0x48c8d4:(0x80,True),0x48c8e0:(0x83,False),
 0x48c8ea:(0x85,True),0x48c8f6:(0x84,False),0x48c900:(0x86,False),
 0x48c90a:(0x88,True),0x48c916:(0x87,False)}
WRAPPERS={0x48c97c:(0x82,False),0x48c986:(0x81,False),
 0x48c990:(0x83,False),0x48c99a:(0x86,False),0x48c9a4:(0x84,False),
 0x48c9ae:(0x87,False),0x48c9b8:(0x85,True),0x48c9c2:(0x88,True),
 0x48c9cc:(0x7f,True),0x48c9d6:(0x80,True)}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('#include <stdint.h>\nuint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_flex_grow_48b9fc',
                 *(str(x) for x in SOURCES),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for native,(prop,narrow) in {**CASES,**WRAPPERS}.items():
  name=next(n for n in syms if n.endswith('_'+format(native,'x')))
  outs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,5)
   lower=(syms['audio_uart_lv_style_property_44bdea']&~1) if is_c else 0x44bdea
   calls=[]
   def hook(uc,a,size,_):
    if a!=lower:return
    calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_R0,0x123456ff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms[name] if is_c else native)|1,0x600000,count=30)
   outs.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert outs[0]==outs[1],(name,outs)
  assert outs[0]==([(0x20003000,0 if native in WRAPPERS else 5,prop)],0xff if narrow else 0x123456ff)
 print(f'PASS {len(CASES)+len(WRAPPERS)} compiled-C/native flex/grid style-selector cases')
