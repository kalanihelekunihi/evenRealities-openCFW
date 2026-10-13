from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-resolution-connected-round265';S=B/'root-ambiq-resolution-wrapper-round264/candidate.c';D.mkdir(exist_ok=True);P=0x20001000;A=0x20002000;C=0x20003000
PATH=0x20004000;PAINT=0x20005000;VG=0x20006000;CELL=0x200746c0;VGCELL=0x20074f04
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_ambiq_default_unit_4c791a','audio_uart_nema_vg_path_reset_514e50','audio_uart_nema_vg_paint_reset_515048','audio_uart_nema_vg_state_reset_515676','audio_uart_ambiq_blend_clear_4b075e','audio_uart_ambiq_stencil_adjust_4b0b5a','audio_uart_lvgl_log','audio_uart_lv_memzero_48949c','audio_uart_nema_vg_set_framebuffer_5223a2'];native=[0x4c791a,0x514e50,0x515048,0x515676,0x4b075e,0x4b0b5a,0x44d25c,0x48949c,0x5223a2];cuts=[0x180000+i*16 for i in range(9)];entry='audio_uart_ambiq_set_resolution_4b0bea'
text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert S.read_text() in text
helper_names=['audio_uart_ambiq_default_unit_4c791a','audio_uart_nema_vg_path_reset_514e50','audio_uart_nema_vg_paint_reset_515048','audio_uart_nema_vg_state_reset_515676','audio_uart_nema_matrix_identity_561810','audio_uart_nema_vg_set_error_51565c','audio_uart_ambiq_blend_clear_4b075e','audio_uart_lv_memzero_48949c','audio_uart_lv_word_fill_4d555c']
def function(name):
 match=re.search(r'(?:void\s*\*?|uint32_t)\s*'+re.escape(name)+r'\([^;{}]*\)\s*\{',text);assert match,name;a=match.start();z=text.index('{',a);depth=1;i=z+1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
H=D/'selected-helpers-fixture.c';prefix='#include <stdint.h>\nextern volatile uint32_t audio_uart_ambiq_unit_cell[];\nextern volatile uint32_t audio_uart_nema_vg_context_cell;\n'+''.join(function(n).split('{')[0]+';\n' for n in helper_names);H.write_text(prefix+'\n'.join(function(n) for n in helper_names))
stencil=B/'root-ambiq-stencil-adjust-round263/candidate.c';assert stencil.read_text() in text
names += ['audio_uart_display_surface_alloc','audio_uart_lv_draw_buf_reshape_48b196','audio_uart_font_bitmap_release'];native += [0x48affa,0x48b196,0x48b216];cuts += [0x180000+i*16 for i in [9,10,11]]
controlled=[6,8,9,10,11]
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in [(names[i],cuts[i]) for i in controlled]]+['-Wl,--defsym=audio_uart_ambiq_unit_cell='+hex(CELL),'-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(VGCELL),str(S),str(stencil),str(H),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,width,height,existing,create,reshape,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*256);u.mem_write(A,bytes([0x6b])*64);u.mem_write(C,bytes([0x7c])*64);u.mem_write(P+64,W(A if existing else 0));u.mem_write(A+4,W((8<<16)|4));u.mem_write(P+68,W(PATH if seed==0x5a else 0));u.mem_write(P+72,W(PAINT if seed==0x5a else 0));u.mem_write(PATH,bytes([seed])*256);u.mem_write(PAINT,bytes([seed])*256);u.mem_write(VG,bytes([seed])*512);u.mem_write(CELL,W(P));u.mem_write(VGCELL,W(VG));events=[];accesses=[]
  def readstr(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def hook(u,a,size,data):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a)
   if k not in controlled:return
   regs=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP)
   if k==6:events.append([k,regs[0],readstr(regs[1]),regs[2],readstr(regs[3]),readstr(int.from_bytes(u.mem_read(sp,4),'little'))]);ret=0
   elif k==8:events.append([k,regs+list(struct.unpack('<II',u.mem_read(sp,8)))]);ret=0
   elif k==9:events.append([k,regs]);ret=[0,A,C][create]
   elif k==10:events.append([k,regs+[int.from_bytes(u.mem_read(sp,4),'little')]]);ret=[0,A,C][reshape]
   else:events.append([k,regs[0]]);ret=0
   if mutation and k in [9,10,11]:u.mem_write(P+64,W(C));u.mem_write(C+12,W(k+17));u.mem_write(C+16,W(k+29))
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,size,value,data):
   if not(P<=a<P+256 or A<=a<A+64 or C<=a<C+64 or PATH<=a<PATH+256 or PAINT<=a<PAINT+256 or VG<=a<VG+512 or a in [CELL,VGCELL]):return
   v=value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little');accesses.append(['w' if access==UC_MEM_WRITE else 'r',a,size,v&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,width);u.reg_write(UC_ARM_REG_R1,height);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entry] if isc else 0x4b0bea)|1,0x600000,count=15000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,accesses,[bytes(u.mem_read(a,n)).hex() for a,n in [(P,256),(A,64),(C,64),(PATH,256),(PAINT,256),(VG,512)]],u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product([0,1,4,7,0x80000000,0xffffffff],[0,8,0xffffffff],[0,1],range(3),range(3),[0x5a,0xff],[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_RESOLUTION_REAL_RESET_ADJUST_GRAPH','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':5,'helper_fixture_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'stencil_sha256':hashlib.sha256(stencil.read_bytes()).hexdigest(),'limits':['Watched ordered unit/framebuffer accesses,child/log order,by-value four-word AAPCS descriptor,full guards/SP match with controlled mutations. Existing caller uses void contract; incidental native R0 not qualified. Actual default/reset/matrix/error/blend/zero/stencil bodies connected. Create/reshape/release/log/framebuffer controlled; ownership/pointerfault/concurrency/physical GPU/layout/image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
