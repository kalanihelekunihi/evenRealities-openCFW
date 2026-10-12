from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/from_image_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_draw_buf_init_48aef8(void*a,unsigned b,unsigned c,unsigned d,unsigned e,void*f,unsigned g){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_from_image_48b762',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for header,dimensions,stride,result,mutation,alias in itertools.product([0,0xffffffff,0x12345619],[0,0xffffffff,0x12345678],[0,0xffff0001],[0,1,256,257],[0,1],[0,1]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   src=0x20003000;dst=src if alias else 0x20004000
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   put(dst,0xabcd0123)
   for off,v in [(0,header),(4,dimensions),(8,stride),(12,0x87654321),(16,0x20005000)]:put(src+off,v)
   calls=[];cut=(syms['audio_uart_lv_draw_buf_init_48aef8'] if isc else 0x48aef8)&~1
   def hook(uc,a,size,user):
    if a!=cut:return
    sp=uc.reg_read(UC_ARM_REG_SP);calls.append(tuple(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3])+tuple(word(sp+i) for i in [0,4,8]));put(dst,0x76543210)
    if mutation:put(src,0xfedcba98)
    uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src);u.emu_start((syms['audio_uart_lv_draw_buf_from_image_48b762'] if isc else 0x48b762)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(src,28)),bytes(u.mem_read(dst,28)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(header,dimensions,stride,result,mutation,alias,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_FROM_IMAGE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Initializer controlled cut verifies seven-argument register/stack ABI, byte result truncation, post-child flags reload and source/destination aliasing.','Initializer production body and full image data/layout/byte equality/hardware remain unproven.']};(SRC.parent/'from-image-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
