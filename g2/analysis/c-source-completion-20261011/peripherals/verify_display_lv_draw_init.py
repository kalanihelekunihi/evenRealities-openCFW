from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/init_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512]; void audio_uart_lv_draw_memzero_48aa54(void*a,unsigned b){} unsigned audio_uart_font_bitmap_stride(unsigned a,unsigned char b){return 0;} void *audio_uart_lv_draw_align_48ab04(void*a,unsigned b){return a;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_init_48aef8',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for width,height,cf,stride,size,aligned in itertools.product([0,17,0xffffffff],[0,2,0x80000000],[0,16,0x12345678],[0,8,0x80000000],[0,15,16,0xffffffff],[0,1]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj=0x20003000;data=0x20004003;sp=0x200ff000;u.mem_write(obj,b'\xa5'*28)
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def string(a):
    out=bytearray()
    while (v:=bytes(u.mem_read(a+len(out),1)))!=b'\0':out.extend(v)
    return out.decode()
   for off,val in [(0,stride),(4,data),(8,size)]:put(sp+off,val)
   calls=[];cuts={(syms[n] if isc else a)&~1:k for n,a,k in [('audio_uart_lv_draw_memzero_48aa54',0x48aa54,'zero'),('audio_uart_font_bitmap_stride',0x48aad8,'stride'),('audio_uart_lv_draw_align_48ab04',0x48ab04,'align'),('audio_uart_lvgl_log',0x44d25c,'log')]}
   def hook(uc,a,size_,user):
    if a not in cuts:return
    kind=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if kind=='zero':calls.append((kind,*args[:2]));u.mem_write(args[0],bytes(args[1]))
    elif kind=='stride':calls.append((kind,*args[:2]));ret=8
    elif kind=='align':
     calls.append((kind,*args[:2]));expected=(syms['audio_uart_display_lv_root']+0xc8) if isc else 0x2006f610;assert word(obj+24)==expected;put(obj+24,0x2006f610);ret=data if aligned else data+1
    else:
     stack=uc.reg_read(UC_ARM_REG_SP);fmt=string(word(stack));extra=[word(stack+4),word(stack+8)] if fmt.startswith('Data size') else [];calls.append((kind,args[0],string(args[1]),args[2],string(args[3]),fmt,extra))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in [(UC_ARM_REG_R0,obj),(UC_ARM_REG_R1,width),(UC_ARM_REG_R2,height),(UC_ARM_REG_R3,cf)]:u.reg_write(reg,val)
   u.emu_start((syms['audio_uart_lv_draw_buf_init_48aef8'] if isc else 0x48aef8)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(obj,28)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(width,height,cf,stride,size,aligned,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_DRAW_INIT_NONNULL','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Zero/stride/align/logger controlled child cuts; native root handlers pointer asserted before normalization.','Covers wrapped size, truncation and alignment warning; null-buffer assertion remains separate required comparison.','Provider implementations and full image layout/byte equality/hardware unproven.']};(SRC.parent/'init-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
