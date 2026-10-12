from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-create-binding-round80/binding_candidate.c';CANON=ROOT/'components/audio/uart_thread_source_candidate/display_font_bitmap_allocate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DEV,OBJ,PIX=0x20001000,0x20002000,0x20003000;STATE=0x2006f548
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_heap_alloc(unsigned a){return 0;} void audio_uart_lv_heap_free(void*a){} unsigned audio_uart_font_bitmap_stride(unsigned a,unsigned char b){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,const char*e,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_state=0x2006f548','-Wl,-e,audio_uart_lv_draw_buf_create_ex_48b010',str(SRC),str(CANON),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,width,height,stride,child_stride,heap,callback,pixels,align,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(OBJ,b'\xa5'*28);u.mem_write(DEV,W(0x610001 if callback else 0));u.mem_write(STATE+0xc8+8,W(0x610101 if align else 0));calls=[];faults=[]
  cuts={(syms[n] if isc else a)&~1:n for n,a in [('audio_uart_lv_heap_alloc',0x44f730),('audio_uart_lv_heap_free',0x44f758),('audio_uart_font_bitmap_stride',0x48aad8),('audio_uart_lvgl_log',0x44d25c)]};cuts[0x610000]='pixel';cuts[0x610100]='align'
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
   if n=='audio_uart_lv_heap_alloc':calls.append(('heap',args[0]));value=OBJ if heap else 0
   elif n=='audio_uart_lv_heap_free':calls.append(('free',args[0]));value=0
   elif n=='audio_uart_font_bitmap_stride':calls.append(('stride',*args[:2]));value=child_stride
   elif n=='pixel':
    calls.append(('pixel',*args[:2]));value=PIX if pixels else 0
    if mutation:uc.mem_write(OBJ,W(0x12345678,0x87654321,0xdeadbeef));uc.mem_write(STATE+0xc8+8,W(0x610101 if not align else 0))
   elif n=='align':
    calls.append(('align',*args[:2]));value=PIX+7
    if mutation:uc.mem_write(OBJ,W(0xcafefeed,0x778899aa,0xdeadbeef))
   else:
    fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];num=2 if args[2]==325 else 5;extra=struct.unpack('<'+'I'*num,uc.mem_read(sp+4,num*4));extra=tuple(readstr(v) for v in extra) if args[2]==325 else extra;calls.append(('log',args[0],readstr(args[1]),args[2],readstr(args[3]),readstr(fmt),extra));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[DEV,width,height,cf]):u.reg_write(reg,value)
  u.mem_write(0x200ff000,W(stride))
  try:u.emu_start((syms['audio_uart_lv_draw_buf_create_ex_48b010'] if isc else 0x48b010)|1,0x600000,count=5000)
  except UcError:
   assert faults==[(0xffffffff,4,0)],faults
  return calls,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),faults,bytes(u.mem_read(OBJ,28)),bytes(u.mem_read(STATE+0xc8+8,4))
 cases=[(cf,13,7,16,8,True,True,True,True,False) for cf in range(256)]
 cases += list(itertools.product([0x100,7,10,20,0xffffffff],[0,0x10001,0xffffffff],[0,0x80000000,0xffffffff],[0,7,0xffffffff],[0,8,0xffffffff],[True],[False,True],[False,True],[False,True],[False,True]))
 cases += [(cf,13,7,16,8,False,True,True,True,False) for cf in [0,20,0xffffffff]]
 for params in cases:
  a=run(False,*params);b=run(True,*params);assert a==b,(params,a,b)
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_CANONICAL_CREATE_BINDING','cases':len(cases),'binding_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'canonical_source_sha256':hashlib.sha256(CANON.read_bytes()).hexdigest(),'limits':['Canonical allocator executes actual C; heap/stride/handler/log cuts cover unsigned size, null paths, mutation and configured fatal first store.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
