from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-load-indexed-round81/load_indexed_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D,DATA,DATA2,DRAW,PIX,FILE,IMAGE,DECOMP=range(0x20001000,0x20009000,0x1000);W=lambda *v:struct.pack('<'+'I'*len(v),*v)
NAMES={'audio_uart_lv_draw_buf_from_image_48b762':0x48b762,'audio_uart_lv_draw_buf_create_ex_48b010':0x48b010,'audio_uart_lv_fs_read_at_4c8d3c':0x4c8d3c,'audio_uart_lv_fs_file_seek_4c6fba':0x4c6fba,'audio_uart_lv_fs_file_tell_4c7018':0x4c7018,'audio_uart_font_bitmap_release':0x48b216,'audio_uart_lvgl_log':0x44d25c}
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text(' '.join('unsigned '+n+'(){return 0;}' for n in NAMES));elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_bin_load_indexed_4c8570',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,kind,compressed,allocated,image_stride,from_result,stage,status,length,mutation,alias=False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[3]=IMAGE;desc[4]=kind;desc[8]=0x80000019|(cf<<8)|(compressed<<16);desc[9]=0x00020003;desc[10]=0xdead0010;desc[18]=D+12 if alias else DATA;u.mem_write(D,W(*desc))
  data=[0x12345678]*17;data[0]=FILE;data[8]=DECOMP;u.mem_write(DATA,W(*data));u.mem_write(DATA2,W(*data));u.mem_write(DRAW,W(0,0,0,0,PIX,0,0));u.mem_write(IMAGE,W((allocated<<16)|0x719,0x00050006,0xbeef0000|image_stride,100,PIX,0,0));calls=[];read_count=0
  if alias:u.mem_write(D+44,W(DECOMP))
  cuts={(syms[n] if isc else a)&~1:n for n,a in NAMES.items()}
  def readstr(ptr):
   out=bytearray()
   for j in range(512):
    v=bytes(u.mem_read(ptr+j,1))
    if v==b'\0':return out.decode()
    out+=v
   raise AssertionError('unterminated string')
  def hook(uc,a,size,user):
   nonlocal read_count
   if a not in cuts:return
   n=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
   if n=='audio_uart_lv_draw_buf_from_image_48b762':
    calls.append(('from',*args[:2]));uc.mem_write(args[0],W(0x719,0x00050006,0xbeef0000|image_stride,100,PIX,0,0));value=from_result
    if mutation:uc.mem_write(D+40,W(0x12345678));uc.mem_write(D+72,W(DATA2))
   elif n=='audio_uart_lv_draw_buf_create_ex_48b010':
    extra=struct.unpack('<I',uc.mem_read(sp,4))[0];calls.append(('create',*args,extra));assert args[0]==0x2006f650;value=0 if stage=='alloc' else DRAW
    if mutation:uc.mem_write(DATA,W(FILE+16));uc.mem_write(D+72,W(DATA2));uc.mem_write(DRAW+16,W(PIX+16))
   elif n=='audio_uart_lv_fs_read_at_4c8d3c':
    read_count+=1;which='palette' if read_count==1 else 'image';ptr=struct.unpack('<I',uc.mem_read(sp,4))[0];count=(args[3]+(1 if stage==which+'_short' else 0))&0xffffffff;uc.mem_write(ptr,W(count));calls.append(('read',*args,count));value=status if stage==which else 0
    if mutation:uc.mem_write(DRAW+16,W(PIX+64));uc.mem_write(DATA+28,W(0xdeadbeef))
   elif n=='audio_uart_lv_fs_file_seek_4c6fba':calls.append(('seek',*args[:3]));value=status if stage=='seek' else 0
   elif n=='audio_uart_lv_fs_file_tell_4c7018':calls.append(('tell',args[0]));uc.mem_write(args[1],W(length));value=status if stage=='tell' else 0
   elif n=='audio_uart_font_bitmap_release':calls.append(('destroy',args[0]));value=0
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num={750:3,768:3,778:1}.get(args[2],0);extra=tuple(struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4))) if num else ();calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x11111111);u.reg_write(UC_ARM_REG_R1,D);u.emu_start((syms['audio_uart_lv_bin_load_indexed_4c8570'] if isc else 0x4c8570)|1,0x600000,count=5000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(D,80)),bytes(u.mem_read(DATA,68)),bytes(u.mem_read(DATA2,68)),bytes(u.mem_read(DRAW,28)),bytes(u.mem_read(IMAGE,28))
 cases=[(7,kind,compressed,allocated,stride,result,'success',0,100,mutation,alias) for kind,compressed,allocated,stride,result,mutation,alias in itertools.product([0,1,2,255],[0,8],[0,16],[0,17],[0,1,256,257],[False,True],[False,True]) if not alias or compressed]
 cases += [(cf,1,0,0,0,1,stage,status,length,mutation,False) for cf,stage,status,length,mutation in itertools.product([0,7,8,9,10,255],['success','alloc','palette','palette_short','seek','tell','image','image_short'],[0,1,256,257],[0,12,20,1036,0xffffffff],[False,True])]
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a,b)
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_LOAD_INDEXED','cases':len(cases),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Child cuts for create/from-image/read/seek/tell/destroy/log; direct compressed ownership and aliased field effects compared.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
