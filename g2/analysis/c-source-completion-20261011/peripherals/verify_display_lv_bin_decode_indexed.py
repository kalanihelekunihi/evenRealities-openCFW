from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-decode-indexed-round84/indexed_candidate.c';LINE=Path(__file__).parent/'root-indexed-line-round77/indexed_line_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D,DATA,DATA2,INDEXED,INPIX,FILE,IMAGE,DECOMP,SOURCE,PAL,DECODED,OUT=range(0x20001000,0x2000d000,0x1000);W=lambda *v:struct.pack('<'+'I'*len(v),*v)
NAMES={'audio_uart_lv_malloc':0x44f718,'audio_uart_lv_heap_free':0x44f758,'audio_uart_lv_draw_buf_create_ex_48b010':0x48b010,'audio_uart_lv_fs_read_at_4c8d3c':0x4c8d3c,'audio_uart_lv_fs_file_seek_4c6fba':0x4c6fba,'audio_uart_lv_fs_file_tell_4c7018':0x4c7018,'audio_uart_font_bitmap_release':0x48b216,'audio_uart_lvgl_log':0x44d25c}
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text(' '.join('unsigned '+n+'(){return 0;}' for n in NAMES));elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_bin_decode_indexed_4c8256',str(SRC),str(LINE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,kind,compressed,stage,status,length,mutation,height):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  desc=[0xa5a5a5a5]*20;desc[3]=IMAGE;desc[4]=kind;desc[8]=0x80000019|(cf<<8)|(compressed<<16);desc[9]=(height<<16)|3;desc[10]=0xdead0010;desc[18]=DATA;u.mem_write(D,W(*desc))
  data=[0x12345678]*17;data[0]=FILE;data[8]=DECOMP;u.mem_write(DATA,W(*data));u.mem_write(DATA2,W(*data));u.mem_write(INDEXED,W(0,0,0xdead0010,0,INPIX,0,0));u.mem_write(DECODED,W(0,0,0xbeef0020,0,OUT,0,0));u.mem_write(IMAGE+16,W(SOURCE));u.mem_write(DECOMP+16,W(SOURCE))
  colors=W(*[((i*0x1020304)^0x87654321)&0xffffffff for i in range(256)]);u.mem_write(SOURCE,colors+bytes((i*37+11)&255 for i in range(3072)));u.mem_write(PAL,colors);u.mem_write(INPIX,bytes((i*37+11)&255 for i in range(4096)));u.mem_write(OUT,b'\xa5'*4096)
  calls=[];faults=[];read_count=0;create_count=0;line_count=0;cuts={(syms[n] if isc else a)&~1:n for n,a in NAMES.items()};line=(syms['audio_uart_lv_bin_decode_indexed_line_4c8c94'] if isc else 0x4c8c94)&~1
  def readstr(ptr):
   out=bytearray()
   for j in range(512):
    v=bytes(u.mem_read(ptr+j,1))
    if v==b'\0':return out.decode()
    out+=v
   raise AssertionError('unterminated string')
  def hook(uc,a,size,user):
   nonlocal read_count,create_count,line_count
   args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
   if a==line:
    extra=struct.unpack('<II',uc.mem_read(sp,8));calls.append(('line',*args,*extra));line_count+=1
    if mutation and line_count==1:uc.mem_write(D+36,W(0x00010004));uc.mem_write(D+40,W(17));uc.mem_write(D+48,W(PAL))
    return
   if a not in cuts:return
   n=cuts[a]
   if n=='audio_uart_lv_malloc':calls.append(('malloc',args[0]));value=0 if stage=='heap' else PAL
   elif n=='audio_uart_lv_heap_free':calls.append(('free',args[0]));value=0
   elif n=='audio_uart_lv_draw_buf_create_ex_48b010':
    create_count+=1;extra=struct.unpack('<I',uc.mem_read(sp,4))[0];calls.append(('create',*args,extra));assert args[0]==0x2006f650
    indexed=(kind==1 and not compressed and create_count==1);which='indexed_alloc' if indexed else 'decoded_alloc';value=0 if stage==which else INDEXED if indexed else DECODED
    if mutation:uc.mem_write(D+72,W(DATA2));uc.mem_write(DATA+4,W(0xdeadbeef))
   elif n=='audio_uart_lv_fs_read_at_4c8d3c':
    read_count+=1;which='palette' if read_count==1 else 'image';ptr=struct.unpack('<I',uc.mem_read(sp,4))[0];count=(args[3]+(1 if stage==which+'_short' else 0))&0xffffffff;uc.mem_write(ptr,W(count));calls.append(('read',*args,count));value=status if stage==which else 0
   elif n=='audio_uart_lv_fs_file_seek_4c6fba':calls.append(('seek',*args[:3]));value=status if stage=='seek' else 0
   elif n=='audio_uart_lv_fs_file_tell_4c7018':calls.append(('tell',args[0]));uc.mem_write(args[1],W(length));value=status if stage=='tell' else 0
   elif n=='audio_uart_font_bitmap_release':calls.append(('destroy',args[0]));value=0
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num={588:2,596:3,624:3}.get(args[2],0);extra=tuple(struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4))) if num else ();extra=tuple(readstr(v) for v in extra) if args[2]==588 else extra;calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x11111111);u.reg_write(UC_ARM_REG_R1,D)
  try:u.emu_start((syms['audio_uart_lv_bin_decode_indexed_4c8256'] if isc else 0x4c8256)|1,0x600000,count=10000)
  except UcError:assert faults==[(0xffffffff,4,0)],faults
  return calls,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),faults,bytes(u.mem_read(D,80)),bytes(u.mem_read(DATA,68)),bytes(u.mem_read(DATA2,68)),bytes(u.mem_read(OUT,4096))
 cases=[(cf,kind,compressed,'success',0,1052,mutation,height) for cf,kind,compressed,mutation,height in itertools.product([0,7,8,9,10,255],[0,1,2],[0,8],[False,True],[0,2])]
 cases += [(cf,1,0,stage,status,length,mutation,2) for cf,stage,status,length,mutation in itertools.product([7,8,9,10],['heap','indexed_alloc','decoded_alloc','palette','palette_short','seek','tell','image','image_short'],[0,1,256,257],[0,1052,0xffffffff],[False,True])]
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a[:7],b[:7],a[7].hex(),b[7].hex())
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_INDEXED_EXPANSION','cases':len(cases),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'line_source_sha256':hashlib.sha256(LINE.read_bytes()).hexdigest(),'limits':['Actual native/compiled indexed-line bodies execute; heap/create/read/seek/tell/free/log cuts.','No full I/O, image layout/byte equality/hardware proof; fatal compares first unmapped store.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
