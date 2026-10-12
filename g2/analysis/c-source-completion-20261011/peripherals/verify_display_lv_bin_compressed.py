from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-compressed-round86/compressed_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
D,DATA,IMAGE,SOURCE,SOURCE2,BUF,FILE,DECOMP=range(0x20001000,0x20009000,0x1000);W=lambda *v:struct.pack('<'+'I'*len(v),*v)
NAMES={'audio_uart_lv_bin_decoder_data_get_4c81a2':0x4c81a2,'audio_uart_lv_basic_box_clear_454746':0x454746,'audio_uart_lv_fs_file_seek_4c6fba':0x4c6fba,'audio_uart_lv_fs_file_tell_4c7018':0x4c7018,'audio_uart_lv_fs_read_at_4c8d3c':0x4c8d3c,'audio_uart_lv_fs_file_read_4c6f46':0x4c6f46,'audio_uart_lv_malloc':0x44f718,'audio_uart_lv_heap_free':0x44f758,'audio_uart_lv_grid_copy_454738':0x454738,'audio_uart_lv_bin_decompress_image_4c8d8c':0x4c8d8c,'audio_uart_lv_bin_load_indexed_4c8570':0x4c8570,'audio_uart_lv_bin_decode_indexed_4c8256':0x4c8256,'audio_uart_lv_bin_decode_alpha_4c887c':0x4c887c,'audio_uart_lvgl_log':0x44d25c}
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text(' '.join('unsigned '+n+'(){return 0;}' for n in NAMES));elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decode_compressed_4c8a2c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,kind,cf,use_indexed,stage,status,length,result,dispatch,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[1]=use_indexed<<24;desc[3]=IMAGE;desc[4]=kind;desc[8]=0x80080019|(cf<<8);desc[18]=DATA;u.mem_write(D,W(*desc));data=[0x12345678]*17;data[0]=FILE;data[8]=DECOMP;u.mem_write(DATA,W(*data));u.mem_write(IMAGE,W(0,0,0,length,SOURCE));header_len=(length-(24 if kind==1 else 12))&0xffffffff;header_len=(header_len+(1 if stage=='mismatch' else 0))&0xffffffff;u.mem_write(SOURCE,W(2,header_len,32));u.mem_write(SOURCE2,W(1,header_len,16));calls=[];cuts={(syms[n] if isc else a)&~1:n for n,a in NAMES.items()}
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
   if n=='audio_uart_lv_bin_decoder_data_get_4c81a2':calls.append(('get',args[0]));value=DATA
   elif n=='audio_uart_lv_basic_box_clear_454746':calls.append(('zero',*args[:3]));uc.mem_write(args[0],bytes([args[1]&255])*args[2]);value=0
   elif n=='audio_uart_lv_fs_file_seek_4c6fba':calls.append(('seek',*args[:3]));value=status if stage=='seek' else 0
   elif n=='audio_uart_lv_fs_file_tell_4c7018':calls.append(('tell',args[0]));uc.mem_write(args[1],W(length));value=status if stage=='tell' else 0
   elif n=='audio_uart_lv_fs_read_at_4c8d3c':
    ptr=struct.unpack('<I',uc.mem_read(sp,4))[0];count=13 if stage=='header_short' else 12;uc.mem_write(ptr,W(count));uc.mem_write(args[2],bytes(uc.mem_read(SOURCE,12)));calls.append(('header',*args,count));value=status if stage=='header' else 0
   elif n=='audio_uart_lv_fs_file_read_4c6f46':
    count=(args[2]+(1 if stage=='payload_short' else 0))&0xffffffff;uc.mem_write(args[3],W(count));calls.append(('payload',*args[:3],count));value=status if stage=='payload' else 0
   elif n=='audio_uart_lv_malloc':calls.append(('malloc',args[0]));value=0 if stage=='alloc' else BUF
   elif n=='audio_uart_lv_heap_free':
    calls.append(('free',args[0]));value=0
    if mutation:uc.mem_write(D+32,W(0x00080e19));uc.mem_write(D+72,W(0x20009000))
   elif n=='audio_uart_lv_grid_copy_454738':
    calls.append(('copy',*args[:3]));uc.mem_write(args[0],bytes(uc.mem_read(args[1],args[2])));value=args[0]
    if mutation:uc.mem_write(IMAGE+16,W(SOURCE2))
   elif n=='audio_uart_lv_bin_decompress_image_4c8d8c':
    calls.append(('decompress',*args[:2],bytes(uc.mem_read(args[1],16)).hex()));value=result
    if mutation:uc.mem_write(IMAGE+16,W(0));uc.mem_write(DATA+32,W(DECOMP+16))
   elif n in ['audio_uart_lv_bin_load_indexed_4c8570','audio_uart_lv_bin_decode_indexed_4c8256','audio_uart_lv_bin_decode_alpha_4c887c']:calls.append((n,*args[:2]));value=dispatch
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num={944:3,949:2,964:3,982:2}.get(args[2],0);extra=tuple(struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4))) if num else ();calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x11111111);u.reg_write(UC_ARM_REG_R1,D);u.emu_start((syms['audio_uart_lv_bin_decode_compressed_4c8a2c'] if isc else 0x4c8a2c)|1,0x600000,count=5000)
  return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(D,80)),bytes(u.mem_read(DATA,68)),bytes(u.mem_read(IMAGE,20))
 cases=[(kind,cf,indexed,'success',0,32,result,dispatch,mutation) for kind,cf,indexed,result,dispatch,mutation in itertools.product([0,1,2],[0,7,8,9,10,11,12,13,14,16,255],[0,1],[0,1,256,257],[0,1,256,257],[False,True])]
 cases += [(1,7,0,stage,status,length,0,0,False) for stage,status,length in itertools.product(['seek','tell','header','header_short','mismatch','alloc','payload','payload_short'],[0,1,256,257],[0,12,24,32,0xffffffff])]
 cases += [(0,7,0,'mismatch',0,length,0,0,False) for length in [0,12,32,0xffffffff]]
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a,b)
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_COMPRESSED_WRAPPER','cases':len(cases),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Children are controlled cuts; zero/copy perform actual memory writes.','Success-dispatch child returns are synthetic reachability tests: locked decompression provider always returns zero.','No successful real decompression, full image layout/byte equality/hardware proof.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
