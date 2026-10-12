from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-reshape-round75/reshape_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
W=lambda *v:struct.pack('<'+'I'*len(v),*v);OBJ=0x20001000
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_font_bitmap_stride(unsigned w,unsigned char f){return 0;}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_reshape_48b196',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,name,native,args,child,mutation,capacity):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(OBJ,W(0xa5a51419,0xdeadbeef,0xff008000,capacity,0x12345678,0x87654321,0x20003000));calls=[];cut=(syms['audio_uart_font_bitmap_stride'] if isc else 0x48aad8)&~1
  def hook(uc,a,size,user):
   if a!=cut:return
   calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   if mutation:uc.mem_write(OBJ,W(0x98760a19,0xffeeddcc,0xdead1234,0xffffffff,0x12345678,0x87654321,0x20003000))
   uc.reg_write(UC_ARM_REG_R0,child);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
  if len(args)>4:u.mem_write(0x200ff000,W(args[4]))
  u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000)
  return u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(OBJ,28)),u.reg_read(UC_ARM_REG_SP)
 counts={};name='audio_uart_lv_draw_buf_size_48b86c';count=0
 for cf,upper,height,stride,child in itertools.product(range(256),[0,0xffffff00],[0,1,0xffffffff],[0,7,0xffffffff],[0,8,0xffffffff]):
  args=[0xffffffff,height,cf|upper,stride];a=run(False,name,0x48b86c,args,child,False,0);b=run(True,name,0x48b86c,args,child,False,0);assert a==b,(args,child,a,b);count+=1
 counts[name]=count;name='audio_uart_lv_draw_buf_reshape_48b196';count=0
 for obj,cf,width,height,stride,child,mutation,cap in itertools.product([0,OBJ],[0,7,20,0x100,0x12345678],[0,0xffffffff],[1,0xffffffff],[0,7,0xffffffff],[0,8],[False,True],[0,15,0xffffffff]):
  args=[obj,cf,width,height,stride];a=run(False,name,0x48b196,args,child,mutation,cap);b=run(True,name,0x48b196,args,child,mutation,cap);assert a==b,(args,child,mutation,cap,a,b);count+=1
 counts[name]=count;r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_SIZE_AND_RESHAPE','cases':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Stride child cut verifies call contract and mutation paths; actual production stride remains selected.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
