from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-vg-path-shape-round286';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074f04
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
selected=R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c';text=selected.read_text()
def function(name):
 match=re.search(r'void '+re.escape(name)+r'\([^;{}]*\)\s*\{',text);assert match; a=match.start();z=text.index('{',a);depth=1;i=z+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
helpers=['audio_uart_nema_vg_set_error_51565c'];helper_text='#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_vg_context_cell;\nextern void audio_uart_lv_pool_free_48429e(void *,void *);\n'+'\n'.join(function(n) for n in helpers);H=D/'selected-helpers-fixture.c';H.write_text(helper_text)
entries=['audio_uart_nema_vg_path_shape_514f3c'];native=[0x514f3c]
if '--selected' in sys.argv:
 for n in entries:assert function(n) in S.read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(CELL),'-Wl,--defsym=audio_uart_nema_vg_path_process_561c68=0x180001',str(S),str(H),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,k,pointer,seed,flags,segments,data,segment_count,data_count):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,segment_bytes in segs:u.mem_write(a,segment_bytes)
  u.mem_write(P,bytes([seed])*256);u.mem_write(CTX,bytes([seed])*512);u.mem_write(CELL,W(CTX));u.mem_write(CTX+144,W(flags));events=[];children=[]
  def mem(u,access,a,size,value,data):
   if not(P<=a<P+256 or CTX<=a<CTX+512 or a==CELL):return
   v=value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little');events.append(['w' if access==UC_MEM_WRITE else 'r',a,size,v])
  def free(u,a,size,unused):
   if a!=(0x180000 if isc else 0x561c68):return
   path=u.reg_read(UC_ARM_REG_R0);children.append([path]);assert path==P
   assert bytes(u.mem_read(P,16))==W(segment_count)+W(data_count)+W(segments)+W(data)
   if flags==1:u.mem_write(P,bytes([0x37])*256)
   elif flags==0xffffffff:u.mem_write(CTX,bytes([0x81])*512)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,free)
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if pointer else 0);u.reg_write(UC_ARM_REG_R1,segment_count);u.reg_write(UC_ARM_REG_R2,segments);u.reg_write(UC_ARM_REG_R3,data_count);u.mem_write(0x200ff000,W(data));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else native[k])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return children,events,bytes(u.mem_read(P,256)).hex(),bytes(u.mem_read(CTX,512)).hex(),u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product(range(1),[0,1],[0,0xff],[0,1,0xffffffff],[0,P,0xffffffff],[0,P+4,0xffffffff],[0,1,0xffffffff],[0,1,0xffffffff]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_PATH_SHAPE_REAL_ERROR','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'helper_fixture_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Full wrapper and actual NULLerror provider; ordered fields and independent pre-postprocessor state assertion/full256path+512VGguards/SP match with controlled postprocessor mutation. Actual561c68 processing/state ownership/pointerfault/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
