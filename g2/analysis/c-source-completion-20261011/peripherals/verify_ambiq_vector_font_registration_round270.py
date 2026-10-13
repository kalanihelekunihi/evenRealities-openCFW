from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-vector-font-registration-round270';S=D/'candidate.c';P=0x20001000;DATA=0x20002000;CTX=0x20003000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_font_outline_context','audio_uart_ambiq_vector_font_push_53d8fc','audio_uart_ambiq_vector_font_allocate_53da54','audio_uart_ambiq_vector_font_release_53db3c','audio_uart_lvgl_log'];native=[0x4b1fcc,0x53d8fc,0x53da54,0x53db3c,0x44d25c];cuts=[0x180000+i*16 for i in range(5)];entries=['audio_uart_ambiq_vector_font_callback_53d82c','audio_uart_font_outline_register_529bf2','audio_uart_ambiq_vector_font_init_53d6da'];orig=[0x53d82c,0x529bf2,0x53d6da]
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0]]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,k,code,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*64);u.mem_write(DATA,bytes([seed])*64);u.mem_write(CTX,bytes([seed])*64);u.mem_write(P+8,W(code));u.mem_write(P+16,W(DATA));u.mem_write(DATA,W(0x20004000));events=[];accesses=[]
  callback=sym[entries[0]] if isc else 0x53d82d
  def norm(v):return 'source_callback' if v==callback else v
  def readstr(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def hook(u,a,size,unused):
   addresses=cuts if isc else native
   if a not in addresses:return
   z=addresses.index(a);r=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if z==0:events.append([0]);ret=CTX
   elif z==4:
    sp=u.reg_read(UC_ARM_REG_SP);msg,value=struct.unpack('<II',u.mem_read(sp,8));events.append([z,r[0],readstr(r[1]),r[2],readstr(r[3]),readstr(msg),value]);ret=0
   else:events.append([z,r[0]]);ret=0
   if mutation:u.mem_write(P+16,W(0xffffffff));u.mem_write(CTX+16,W(0x20008001))
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,size,value,unused):
   if not(P<=a<P+64 or DATA<=a<DATA+64 or CTX<=a<CTX+64):return
   v=(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little'))&((1<<(8*size))-1);accesses.append(['w' if access==UC_MEM_WRITE else 'r',a,size,norm(v)])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33)
  u.reg_write(UC_ARM_REG_R0,P if k==0 else (callback if k==1 else DATA));u.reg_write(UC_ARM_REG_R1,code);u.reg_write(UC_ARM_REG_R2,DATA);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else orig[k])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  state=[bytes(u.mem_read(a,64)).hex() for a in [P,DATA]];ctx=list(struct.unpack('<16I',u.mem_read(CTX,64)));ctx[4]=norm(ctx[4]);return events,accesses,state,ctx,u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product(range(3),[0,36,40,41,0x8024,0x8028,0x8029,0x10024,0xffffffff],[0,0x5a,0xff],[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_VECTOR_FONT_REGISTRATION_DISPATCH','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':5,'limits':['Three bodies and actual registration call connected; callback pointers normalized only to verified native/source callback symbols. Watched ordered accesses/full event/data/context guards/SP/log contents match. Outline context and event children controlled; callback final placement,ownership/pointerfault/bus/full-image/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
