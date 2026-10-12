from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-fs-tell-round82/tell_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];W=lambda *v:struct.pack('<'+'I'*len(v),*v)
F,D,C,O=0x20001000,0x20002000,0x20003000,0x20004000
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_file_tell_4c7018',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for driver,cap,callback,position,status,alias in itertools.product([False,True],[0,8,0xffffffff],[False,True],[0,17,0xffffffff],[0,1,256,257],[False,True]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(F,W(0x12345678,D if driver else 0,C));u.mem_write(D,W(0,cap,0,0,0,0,0,0,0x610001 if callback else 0));u.mem_write(C,W(0,0,position));u.mem_write(O,W(0xa5a5a5a5));out=F+4 if alias else O;calls=[]
   def hook(uc,a,size,user):
    if a!=0x610000:return
    args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];calls.append(tuple(args));uc.mem_write(args[2],W(position));uc.reg_write(UC_ARM_REG_R0,status);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,F);u.reg_write(UC_ARM_REG_R1,out);u.emu_start((syms['audio_uart_lv_fs_file_tell_4c7018'] if isc else 0x4c7018)|1,0x600000,count=1000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(F,12)),bytes(u.mem_read(O,4))))
  assert outputs[0]==outputs[1],(driver,cap,callback,position,status,alias,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_TELL','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Valid output/cache pointer contract; driver tell callback cut. Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
