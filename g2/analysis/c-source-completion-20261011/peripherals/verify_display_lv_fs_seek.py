from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-fs-seek-round74/seek_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
F,D,C,D2,C2,B,O=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20006000,0x20007000
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_fs_file_read_4c6f46(void*a,void*b,unsigned c,unsigned*d){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_read_at_4c8d3c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,name,native,position,whence,driver,cap,seek,tell,status,tell_status,mutation,readat=False,out=True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  for d in [D,D2]:u.mem_write(d,W(0,cap,0,0,0,0,0,0x610001 if seek else 0,0x610101 if tell else 0))
  for c in [C,C2]:u.mem_write(c,W(10,20,0xfffffff8,0))
  u.mem_write(F,W(0x12345678,D if driver else 0,C));u.mem_write(O,W(0xa5a5a5a5));calls=[]
  read=(syms['audio_uart_lv_fs_file_read_4c6f46'] if isc else 0x4c6f46)&~1
  def hook(uc,a,size,user):
   if a not in [0x610000,0x610100,read]:return
   args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if a==0x610000:
    calls.append(('seek',*args))
    if mutation:uc.mem_write(F,W(0x87654321,D2,C2))
    value=status
   elif a==0x610100:
    calls.append(('tell',args[0],args[1]));uc.mem_write(args[2],W(0xfffffffe))
    if mutation:uc.mem_write(F+8,W(C))
    value=tell_status
   else:
    ptr=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
    calls.append(('read',*args,ptr))
    if ptr:uc.mem_write(ptr,W(37))
    value=tell_status
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  args=[F,position,B,0xffffffff] if readat else [F,position,whence,0]
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
  if readat:u.mem_write(0x200ff000,W(O if out else 0))
  u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(F,12)),bytes(u.mem_read(C,16)),bytes(u.mem_read(C2,16)),bytes(u.mem_read(O,4))
 counts={}
 for name,native in [('audio_uart_lv_fs_file_seek_4c6fba',0x4c6fba),('audio_uart_lv_fs_seek_cached_4c7364',0x4c7364)]:
  count=0
  configurations=itertools.product([False,True],[0,8,0xffffffff],[False,True],[False,True],[0,1,256,257],[0,1,256,257],[False,True],[0,1,0xffffffff],[0,1,2,3,256,258,0xffffffff])
  for driver,cap,seek,tell,status,ts,mut,pos,whence in configurations:
   if native==0x4c7364 and (not driver or not seek or not tell):continue
   a=run(False,name,native,pos,whence,driver,cap,seek,tell,status,ts,mut);b=run(True,name,native,pos,whence,driver,cap,seek,tell,status,ts,mut)
   assert a==b,(name,driver,cap,seek,tell,status,ts,mut,pos,whence,a,b);count+=1
  counts[name]=count
 name='audio_uart_lv_fs_read_at_4c8d3c';count=0
 for driver,cap,seek,tell,status,ts,mut,pos,out in itertools.product([False,True],[0,8],[False,True],[False,True],[0,1,256,257],[0,1,256,257],[False,True],[0,0xffffffff],[False,True]):
  a=run(False,name,0x4c8d3c,pos,0,driver,cap,seek,tell,status,ts,mut,True,out);b=run(True,name,0x4c8d3c,pos,0,driver,cap,seek,tell,status,ts,mut,True,out)
  assert a==b,(name,driver,cap,seek,tell,status,ts,mut,pos,out,a,b);count+=1
 counts[name]=count
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_SEEK_AND_READ_AT','cases':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Driver seek/tell and file-read child cuts; full production providers remain required.','No full image layout/byte equality/hardware proof.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
