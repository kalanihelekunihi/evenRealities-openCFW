from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;SRC=BASE/'root-postprocess-round90/postprocess_candidate.c';LEAVES=BASE/'root-postprocess-leaves-round89/leaves_candidate.c';ROOT=BASE.parents[2]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
D,A,B,C=0x20001000,0x20002000,0x20003000,0x20004000
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('''unsigned audio_uart_font_bitmap_stride(unsigned a,unsigned char b){return 0;} unsigned audio_uart_lv_draw_buf_adjust_stride_48b34e(void*a,unsigned b){return 0;} void *audio_uart_lv_draw_buf_create_ex_48b010(void*a,unsigned b,unsigned c,unsigned d,unsigned e){return 0;} void audio_uart_lv_draw_buf_copy_48ad42(void*a,const void*b,const void*c,const void*d){} void audio_uart_lv_draw_buf_premultiply_48b540(void*a){} void *audio_uart_lv_draw_buf_duplicate_ex_48b134(void*a,const void*b){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}''');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_decoder_postprocess_489168',str(SRC),str(LEAVES),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 maps=[('stride','audio_uart_font_bitmap_stride',0x48aad8),('adjust','audio_uart_lv_draw_buf_adjust_stride_48b34e',0x48b34e),('create','audio_uart_lv_draw_buf_create_ex_48b010',0x48b010),('copy','audio_uart_lv_draw_buf_copy_48ad42',0x48ad42),('pre','audio_uart_lv_draw_buf_premultiply_48b540',0x48b540),('dup','audio_uart_lv_draw_buf_duplicate_ex_48b134',0x48b134),('log','audio_uart_lvgl_log',0x44d25c)]
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  engines.append((u,{(syms[s] if isc else native)&~1:op for op,s,native in maps},(syms['audio_uart_lv_decoder_postprocess_489168'] if isc else 0x489168)|1))
 def readstr(u,ptr):
  data=bytes(u.mem_read(ptr,256));return data.split(b'\0')[0].decode()
 count=0
 cases=list(itertools.product([7,11,14,16,19,20,24,255],[0,1],[0,1],[0,1,32,33],[16,17,0x10010],[0,1,0x101,0x100],[0,1,2]))
 for cf,align,pre,flags,expected,adjust,mode in cases:
  outs=[]
  for u,cuts,entry in engines:
   u.mem_write(D,W(0,align|(pre<<8)));u.mem_write(A,W((flags<<16)|(cf<<8),11|(7<<16),16,0xa5a5a5a5));u.mem_write(B,W((flags<<16)|(cf<<8),11|(7<<16),16,0xb5b5b5b5));u.mem_write(C,W((flags<<16)|(cf<<8),11|(7<<16),16,0xc5c5c5c5));calls=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
    if op=='stride':calls.append((op,*r[:2]));ret=expected
    elif op=='adjust':
     calls.append((op,*r[:2]));ret=adjust
     if mode==2:uc.mem_write(A,W((32<<16)|(16<<8),13|(9<<16),17,0xdddddddd));uc.mem_write(D+5,b'\x01')
    elif op=='create':calls.append((op,*r,struct.unpack('<I',uc.mem_read(sp,4))[0]));ret=0 if mode==0 else B
    elif op=='copy':
     calls.append((op,*r));ret=0xabcdef
     if mode==2:uc.mem_write(B,W((32<<16)|(19<<8)));uc.mem_write(D+5,b'\x01')
    elif op=='dup':calls.append((op,*r[:2]));ret=0 if mode==0 else C
    elif op=='pre':calls.append((op,r[0]));uc.mem_write(r[0]+12,W(0x13579bdf));ret=0xfedcba98
    elif op=='log':calls.append((op,r[0],readstr(uc,r[1]),r[2],readstr(uc,r[3]),readstr(uc,struct.unpack('<I',uc.mem_read(sp,4))[0])))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   handle=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_R1,A)
   u.emu_start(entry,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),*[bytes(u.mem_read(p,n)) for p,n in [(D,8),(A,16),(B,16),(C,16)]]));u.hook_del(handle)
  assert outs[0]==outs[1],(cf,align,pre,flags,expected,adjust,mode,outs);count+=1
 # Null decoded must return before touching descriptor.
 for u,cuts,entry in engines:
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,0);u.emu_start(entry,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_R0)==0
 count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_POSTPROCESS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'leaves_sha256':hashlib.sha256(LEAVES.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'489168..48925a','limits':['Actual color/flag leaves execute; stride/adjust/create/copy/duplicate/premultiply/logger child cuts.','Native branch, logs, argument widths, child mutation ordering verified on bounded cases. Full image/layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
