#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
src=R/'g2/components/bootloader/initializer_callbacks/startup_runtime.c';elf=H/'startup-slot18-candidate.elf';cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_startup_spot_dispatch','-Wl,--gc-sections','-Wl,--defsym=bl_bl009_dispatch_native=0x10030001','-Wl,--unresolved-symbols=ignore-all',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,rev,var,seed,callback_ret,raw):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x100000)
 def w(p,x):u.mem_write(p,struct.pack('<I',x))
 w(0x4002000c,rev);w(0x20000098,var);w(0x40020028,seed);w(0x40020060,seed);w(0x40020080,seed);w(0x2002705c,raw);u.mem_write(0x200271a8,bytes([callback_ret]))
 u.mem_write(0x20026e38,b'\xa5'*60)
 u.reg_write(UC_ARM_REG_SP,0x2003eff0);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,data):
  if pc in (0x42d6c0,0x10030000):
   calls.append('init');emu.reg_write(UC_ARM_REG_R0,callback_ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((sym['opencfw_boot_startup_spot_dispatch'] if source else 0x41ce52)|1,0x10000000,count=30000)
 slot=struct.unpack('<I',u.mem_read(0x20026e50,4))[0]
 assert slot==(sym['bl009_slot18_timing']|1 if source else 0x42d5f9),(source,rev,var,hex(slot))
 state=dict(init=calls,dispatch_ret=u.reg_read(UC_ARM_REG_R0),flags=bytes(u.mem_read(0x200271a9,6)).hex(),reg28=struct.unpack('<I',u.mem_read(0x40020028,4))[0],reg60=struct.unpack('<I',u.mem_read(0x40020060,4))[0])
 u.reg_write(UC_ARM_REG_R0,raw);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_LR,0x10000001)
 before=(bytes(u.mem_read(0x20026e38,60)),bytes(u.mem_read(0x40020028,4)),bytes(u.mem_read(0x40020060,4)))
 u.emu_start(slot,0x10000000,count=20)
 after=(bytes(u.mem_read(0x20026e38,60)),bytes(u.mem_read(0x40020028,4)),bytes(u.mem_read(0x40020060,4)))
 assert before==after
 assert struct.unpack('<I',u.mem_read(0x40020080,4))[0]==(((seed&~0x3ff)|(((raw-7) if raw>=8 else 0)&0x3ff)) if callback_ret else seed)
 state.update(reg80=struct.unpack('<I',u.mem_read(0x40020080,4))[0],flag=u.mem_read(0x200271a8,1)[0],slot_ret=u.reg_read(UC_ARM_REG_R0),slot_sp=u.reg_read(UC_ARM_REG_SP))
 return state
cases=[]
for rev,var in ((33,3),(34,0),(34,1),(35,0)):
 for seed,callback_ret,raw in itertools.product((0,0xffffffff),(0,7),(0,7,8,9,0xffffffff)):
  a,b=run(False,rev,var,seed,callback_ret,raw),run(True,rev,var,seed,callback_ret,raw)
  assert a==b,(rev,var,seed,callback_ret,raw,a,b)
  cases.append((rev,var,seed,callback_ret,raw))
receipt=dict(status='PASS',cases=len(cases),stock_dispatch_sha256=hashlib.sha256(blob[0x41ce52-0x410000:0x41d0ee-0x410000]).hexdigest(),stock_callback_sha256=hashlib.sha256(blob[0x42d5f8-0x410000:0x42d61e-0x410000]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='BL009-family dispatch only; named first callback is synthetic and other unresolved callback symbols are ignored for this isolated fixture. Compares slot18 pointer ownership, dispatcher observable state and actual slot18 invocation. Other table slots, root startup and hardware behavior remain open. Scalar Cortex-M4 execution; M55 archive separate.')
(H/'startup-slot18-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS startup slot18',len(cases))
