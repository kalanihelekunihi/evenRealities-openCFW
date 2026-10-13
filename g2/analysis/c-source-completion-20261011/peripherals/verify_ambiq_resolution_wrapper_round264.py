from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-resolution-wrapper-round264';S=D/'candidate.c';P=0x20001000;A=0x20002000;C=0x20003000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_ambiq_default_unit_4c791a','audio_uart_nema_vg_path_reset_514e50','audio_uart_nema_vg_paint_reset_515048','audio_uart_nema_vg_state_reset_515676','audio_uart_ambiq_blend_clear_4b075e','audio_uart_ambiq_stencil_adjust_4b0b5a','audio_uart_lvgl_log','audio_uart_lv_memzero_48949c','audio_uart_nema_vg_set_framebuffer_5223a2'];native=[0x4c791a,0x514e50,0x515048,0x515676,0x4b075e,0x4b0b5a,0x44d25c,0x48949c,0x5223a2];cuts=[0x180000+i*16 for i in range(9)];entry='audio_uart_ambiq_set_resolution_4b0bea'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,width,height,status,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*256);u.mem_write(A,bytes([0x6b])*64);u.mem_write(C,bytes([0x7c])*64);u.mem_write(P+64,W(A));u.mem_write(P+68,W(A+32));u.mem_write(P+72,W(C+32));events=[];accesses=[]
  def readstr(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def hook(u,a,size,data):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a);regs=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP)
   if k==0:events.append([k]);ret=P
   elif k in [1,2,4]:events.append([k,regs[0]]);ret=0
   elif k==3:events.append([k]);ret=0
   elif k==5:events.append([k,regs[:3]]);ret=status
   elif k==6:events.append([k,regs[0],readstr(regs[1]),regs[2],readstr(regs[3]),readstr(int.from_bytes(u.mem_read(sp,4),'little'))]);ret=0
   elif k==7:
    events.append([k,regs[1]]);u.mem_write(regs[0],bytes(regs[1]));ret=0
    if mutation:u.mem_write(regs[0]+4,W(0x76543210))
   else:events.append([k,regs+list(struct.unpack('<II',u.mem_read(sp,8)))]);ret=0
   if mutation and k in [1,2,3,4,5,7]:u.mem_write(P+64,W(C));u.mem_write(P+72,W(A+48));u.mem_write(C+12,W(k+17));u.mem_write(C+16,W(k+29))
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,size,value,data):
   if not(P<=a<P+256 or A<=a<A+64 or C<=a<C+64):return
   v=value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little');accesses.append(['w' if access==UC_MEM_WRITE else 'r',a,size,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,width);u.reg_write(UC_ARM_REG_R1,height);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entry] if isc else 0x4b0bea)|1,0x600000,count=4000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,accesses,[bytes(u.mem_read(a,n)).hex() for a,n in [(P,256),(A,64),(C,64)]],u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product([0,1,3,4,7,0x80000000,0xfffffffd,0xffffffff],[0,1,8,0xfffffffe,0xffffffff],[0,1,257,256,0xffffffff],[0x5a,0xff],[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_RESOLUTION_WRAPPER_CONTROLLED_CHILDREN','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':9,'limits':['Watched ordered unit/framebuffer accesses,child/log order,by-value four-word AAPCS descriptor,full guards/SP match with controlled mutations. Existing caller uses void contract; incidental native R0 not qualified. Real children/ownership/pointerfault/concurrency/physical GPU/layout/image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
