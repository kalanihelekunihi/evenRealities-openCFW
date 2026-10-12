from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-decompress-round85/decompress_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D,C,DRAW,DATA=0x20001000,0x20002000,0x20003000,0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
NAMES={'audio_uart_lv_bin_decoder_data_get_4c81a2':0x4c81a2,'audio_uart_lv_draw_buf_create_ex_48b010':0x48b010,'audio_uart_font_bitmap_release':0x48b216,'audio_uart_lvgl_log':0x44d25c}
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text(' '.join('unsigned '+n+'(){return 0;}' for n in NAMES));elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_bin_decompress_image_4c8d8c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,method,out_len,capacity,get,alloc,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[8]=0x87651019;desc[9]=0x00020003;desc[10]=0xbeef0010;u.mem_write(D,W(*desc));u.mem_write(C,W(method,0xffffffff,out_len,0x20005000));u.mem_write(DRAW,W(0,0,0,capacity,0x20006000,0,0));calls=[];cuts={(syms[n] if isc else a)&~1:n for n,a in NAMES.items()}
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
   if n=='audio_uart_lv_bin_decoder_data_get_4c81a2':
    calls.append(('get',args[0]));value=DATA if get else 0
    if mutation:uc.mem_write(D+36,W(0xffff0001));uc.mem_write(D+40,W(0xdeadffff))
   elif n=='audio_uart_lv_draw_buf_create_ex_48b010':
    extra=struct.unpack('<I',uc.mem_read(sp,4))[0];calls.append(('create',*args,extra));assert args[0]==0x2006f650;value=DRAW if alloc else 0
    if mutation:uc.mem_write(C,W(method^0xf0,1,out_len^0xffffffff,0));uc.mem_write(D+72,W(DATA))
   elif n=='audio_uart_font_bitmap_release':calls.append(('destroy',args[0]));value=0
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num={1117:2,1122:2,1171:1}.get(args[2],0);extra=tuple(struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4))) if num else ();calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_R1,C);u.emu_start((syms['audio_uart_lv_bin_decompress_image_4c8d8c'] if isc else 0x4c8d8c)|1,0x600000,count=3000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(D,80)),bytes(u.mem_read(C,16))
 cases=[(m,1,1,True,True,False) for m in range(256)];cases+=list(itertools.product([0,1,2,255],[0,1,0xffffffff],[0,1,0xffffffff],[False,True],[False,True],[False,True]))
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a,b)
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_DISABLED_CODEC_PROVIDER','cases':len(cases),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Data-get/create/destroy/log child cuts; all native provider paths return zero, including disabled RLE/LZ4.','No successful decompression, custom codec configuration, full image layout/byte equality/hardware proof.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
