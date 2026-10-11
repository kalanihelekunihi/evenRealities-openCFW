#!/usr/bin/env python3
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent; R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
src=R/'g2/components/bootloader/initializer_callbacks/startup_runtime.c'; elf=H/'startup-pcm21-slots.elf'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_startup_spot_dispatch','-Wl,--gc-sections','-Wl,--defsym=hw_state_compose_42bdf0_native=0x10030001','-Wl,--unresolved-symbols=ignore-all',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
slots=((0x14,0x42bd8d,'pcm21_slot14_config'),(0x18,0x42bda1,'pcm21_slot18_timing'),(0x1c,0x42bdbd,'pcm21_slot1c_timing'))
watched=(0x4002034c,0x40020080,0x40020088,0x400201b0)
def run(source,rev,var,magic,info,seed,callback_ret):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x100000)
 def w(p,x):u.mem_write(p,struct.pack('<I',x))
 def rd(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 w(0x4002000c,rev);w(0x20000098,var);w(0x40020028,seed);w(0x40020060,seed)
 w(0x20026ba0,magic);w(0x20026bc0,info);w(0x20026c08,info)
 for p in watched:w(p,seed)
 u.mem_write(0x20026e38,b'\xa5'*60)
 u.reg_write(UC_ARM_REG_SP,0x2003eff0);u.reg_write(UC_ARM_REG_LR,0x10000001)
 def hook(emu,pc,size,data):
  if pc in (0x42bdf0,0x10030000):
   emu.reg_write(UC_ARM_REG_R0,callback_ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((sym['opencfw_boot_startup_spot_dispatch'] if source else 0x41ce52)|1,0x10000000,count=30000)
 result=[u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200271a9,6)).hex(),rd(0x40020028),rd(0x40020060)]
 for offset,original,name in slots:
  target=rd(0x20026e38+offset)
  assert target==((sym[name]|1) if source else original),(source,rev,var,offset,hex(target))
  before=bytes(u.mem_read(0x20026e38,60));u.reg_write(UC_ARM_REG_R0,info);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_LR,0x10000001)
  u.emu_start(target,0x10000000,count=100)
  assert bytes(u.mem_read(0x20026e38,60))==before
  result.extend((offset,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)))
  result.extend(rd(p) for p in watched)
 return result
cases=[]
for rev,var in ((34,2),(35,1)):
 for magic,info,seed,callback_ret in itertools.product((0,0x1f01600d),(0,0xffffffff,0x12345678),(0,0xa5a5a5a5),(0,7)):
  a,b=run(False,rev,var,magic,info,seed,callback_ret),run(True,rev,var,magic,info,seed,callback_ret)
  assert a==b,(rev,var,hex(magic),hex(info),hex(seed),callback_ret,a,b)
  cases.append((rev,var,magic,info,seed,callback_ret))
receipt=dict(status='PASS',cases=len(cases),stock_image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='PCM2.1 silicon branch only; first callback return controlled. Compares installed source pointers and sequential callback effects on observed RAM/MMIO, not root startup or physical silicon. Scalar M4 original/source execution; M55 archive independent.')
(H/'startup-pcm21-slots-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS startup PCM2.1 slots',len(cases))
