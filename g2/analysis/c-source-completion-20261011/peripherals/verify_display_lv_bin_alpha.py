from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-alpha-round79/alpha_candidate.c';BPP=Path(__file__).parent/'root-draw-helpers-round68/bpp_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D,DATA,DATA2,DRAW,PIX,FILE,IMAGE,IMAGE2,DECOMP,DECOMP2,SOURCE,SOURCE2=range(0x20001000,0x2000d000,0x1000)
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_draw_buf_create_ex_48b010(void*a,unsigned b,unsigned c,unsigned d,unsigned e){return 0;} unsigned audio_uart_lv_fs_read_at_4c8d3c(void*a,unsigned b,void*c,unsigned d,unsigned*e){return 0;} void *audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;} void audio_uart_font_bitmap_release(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_bin_decode_alpha_4c887c',str(SRC),str(BPP),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,kind,compressed,stride,height,alloc,status,mode,mutation,helper=None):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[3]=IMAGE;desc[4]=kind;desc[8]=0x80000019|(cf<<8)|(compressed<<16);desc[9]=(height<<16)|17;desc[10]=0xdead0000|stride;desc[18]=DATA;u.mem_write(D,W(*desc))
  data=[0x12345678]*17;data[0]=FILE;data[8]=DECOMP;u.mem_write(DATA,W(*data));u.mem_write(DATA2,W(*data));u.mem_write(DRAW,W(0,0,0,0,PIX,0,0));u.mem_write(PIX,bytes((i*61+3)&255 for i in range(512)))
  for obj,source in [(IMAGE,SOURCE),(IMAGE2,SOURCE2),(DECOMP,SOURCE),(DECOMP2,SOURCE2)]:u.mem_write(obj+16,W(source))
  for source,offset in [(SOURCE,11),(SOURCE2,67)]:u.mem_write(source,bytes((i*37+offset)&255 for i in range(512)))
  calls=[];cuts={(syms[n] if isc else a)&~1:n for n,a in [('audio_uart_lv_draw_buf_create_ex_48b010',0x48b010),('audio_uart_lv_fs_read_at_4c8d3c',0x4c8d3c),('audio_uart_lv_grid_copy_454738',0x454738),('audio_uart_font_bitmap_release',0x48b216),('audio_uart_lvgl_log',0x44d25c)]}
  def readstr(ptr):
   out=bytearray()
   for j in range(512):
    v=bytes(u.mem_read(ptr+j,1))
    if v==b'\0':return out.decode()
    out+=v
   raise AssertionError('unterminated string')
  def hook(uc,a,size,user):
   if a not in cuts:return
   n=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
   if n=='audio_uart_lv_draw_buf_create_ex_48b010':
    extra=struct.unpack('<I',uc.mem_read(sp,4))[0];calls.append(('create',*args,extra));assert args[0]==0x2006f650
    if mutation:
     uc.mem_write(D+72,W(DATA2));uc.mem_write(D+12,W(IMAGE2));uc.mem_write(DATA,W(FILE+16));uc.mem_write(DATA+32,W(DECOMP2));uc.mem_write(DRAW+16,W(PIX+64))
    if mutation==2:uc.mem_write(D+32,W(0x00000e19));uc.mem_write(D+16,W(0))
    value=DRAW if alloc else 0
   elif n=='audio_uart_lv_fs_read_at_4c8d3c':
    ptr=struct.unpack('<I',uc.mem_read(sp,4))[0];count=(args[3]+mode)&0xffffffff;uc.mem_write(ptr,W(count));calls.append(('read',*args,count));assert args[3]<=512
    if args[3]:uc.mem_write(args[2],bytes(uc.mem_read(SOURCE,args[3])))
    value=status
   elif n=='audio_uart_lv_grid_copy_454738':
    calls.append(('copy',*args[:3]));assert args[2]<=512
    if args[2]:uc.mem_write(args[0],bytes(uc.mem_read(args[1],args[2])))
    value=args[0]
   elif n=='audio_uart_font_bitmap_release':calls.append(('destroy',args[0]));value=0
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num={846:1,872:3}.get(args[2],0);extra=tuple(struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4))) if num else ();calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if helper is None:
   u.reg_write(UC_ARM_REG_R0,0x11111111);u.reg_write(UC_ARM_REG_R1,D);name='audio_uart_lv_bin_decode_alpha_4c887c';native=0x4c887c
  else:
   u.reg_write(UC_ARM_REG_R0,helper[0]);u.reg_write(UC_ARM_REG_R1,helper[1]);name='audio_uart_lv_bin_bit_extend_4c884a';native=0x4c884a
  u.emu_start((syms[name] if isc else native)|1,0x600000,count=10000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(D,80)),bytes(u.mem_read(DATA,68)),bytes(u.mem_read(DATA2,68)),bytes(u.mem_read(DRAW,28)),bytes(u.mem_read(PIX,512))
 cases=[(cf,0,0,8,1,True,0,0,0) for cf in range(256)]
 cases += [(cf,kind,compressed,stride,height,True,status,mode,mutation) for cf,kind,compressed,stride,height,status,mode,mutation in itertools.product([11,12,13,14],[0,1,2],[0,8],[0,3,8],[0,2],[0,1,256,257],[0,1,-1],[0,1,2])]
 cases += [(cf,kind,0,8,1,False,0,0,0) for cf,kind in itertools.product([11,12,13,14],[0,1,2])]
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a[:3],b[:3],a[7].hex(),b[7].hex())
 helpers=0
 for value,bits in itertools.product(range(256),[1,2,4,6,8,12,16,24,32]):
  params=(0,0,0,0,0,True,0,0,0);a=run(False,*params,helper=(value,bits));b=run(True,*params,helper=(value,bits));assert a==b,(value,bits,a[:3],b[:3]);helpers+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_ALPHA_AND_INTERPOLATION','alpha_cases':len(cases),'helper_cases':helpers,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'bpp_source_sha256':hashlib.sha256(BPP.read_bytes()).hexdigest(),'limits':['BPP and interpolation execute actual native/compiled bodies; create/copy/read/destroy/log child cuts.','Compressed/variable/file, zero dimensions, read failures, allocation failures and owner changes covered; full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
