from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-rgb-round78/rgb_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D,DATA,DATA2,DRAW,PIX,FILE=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20006000
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_draw_buf_create_ex_48b010(void*a,unsigned b,unsigned c,unsigned d,unsigned e){return 0;} unsigned audio_uart_lv_fs_read_at_4c8d3c(void*a,unsigned b,void*c,unsigned d,unsigned*e){return 0;} void audio_uart_font_bitmap_release(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_bin_decode_rgb_4c8780',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,dimensions,stride,alloc,status,mode,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[8]=0x87650019|(cf<<8);desc[9]=dimensions;desc[10]=stride;desc[18]=DATA;u.mem_write(D,W(*desc))
  data=[0x12345678]*17;data[0]=FILE;u.mem_write(DATA,W(*data));u.mem_write(DATA2,W(*data));u.mem_write(DRAW,W(0,0,0,0,PIX,0,0));calls=[]
  cuts={(syms[n] if isc else a)&~1:n for n,a in [('audio_uart_lv_draw_buf_create_ex_48b010',0x48b010),('audio_uart_lv_fs_read_at_4c8d3c',0x4c8d3c),('audio_uart_font_bitmap_release',0x48b216),('audio_uart_lvgl_log',0x44d25c)]}
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
    if mutation:uc.mem_write(D+72,W(DATA2));uc.mem_write(DATA,W(FILE+16,*([0xabcdef01]*16)));uc.mem_write(DRAW+16,W(PIX+16))
    value=DRAW if alloc else 0
   elif n=='audio_uart_lv_fs_read_at_4c8d3c':
    ptr=struct.unpack('<I',uc.mem_read(sp,4))[0];count=(args[3]+mode)&0xffffffff;uc.mem_write(ptr,W(count));calls.append(('read',*args,count))
    if mutation:uc.mem_write(D+44,W(0xdeadbeef));uc.mem_write(DATA+28,W(0xdeadbeef))
    value=status
   elif n=='audio_uart_font_bitmap_release':calls.append(('destroy',args[0]));value=0
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];extra=tuple(struct.unpack('<3I',uc.mem_read(sp+4,12))) if args[2]==809 else ();calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x11111111);u.reg_write(UC_ARM_REG_R1,D)
  u.emu_start((syms['audio_uart_lv_bin_decode_rgb_4c8780'] if isc else 0x4c8780)|1,0x600000,count=3000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(D,80)),bytes(u.mem_read(DATA,68)),bytes(u.mem_read(DATA2,68)),bytes(u.mem_read(DRAW,28))
 count=0
 for cf,dim,stride,alloc,status,mode,mutation in itertools.product([0,7,14,20,255],[0,0x00020003,0xffff0001,0xffffffff],[0,8,0xdeadffff],[False,True],[0,1,256,257],[0,1,-1],[False,True]):
  a=run(False,cf,dim,stride,alloc,status,mode,mutation);b=run(True,cf,dim,stride,alloc,status,mode,mutation);assert a==b,(cf,dim,stride,alloc,status,mode,mutation,a,b);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_RGB_DECODE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Create/read-at/destroy/log child cuts verify owner, count, argument and cleanup contracts; full providers required.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
