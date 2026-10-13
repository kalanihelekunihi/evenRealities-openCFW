from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-path-bounds-reset-round291';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074f04
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
selected=R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c';text=selected.read_text()
def function(name):
 match=re.search(r'void '+re.escape(name)+r'\([^;{}]*\)\s*\{',text);assert match; a=match.start();z=text.index('{',a);depth=1;i=z+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
helpers=[];helper_text='#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_vg_context_cell;\n'+'\n'.join(function(n) for n in helpers);H=D/'selected-helpers-fixture.c';H.write_text(helper_text)
entries=['audio_uart_nema_vg_path_bounds_reset_514e0c'];native=[0x514e0c]
if '--selected' in sys.argv:
 for n in entries:assert function(n) in S.read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(CELL),str(S),str(H),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,k,pointer,seed,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*256);u.mem_write(CTX,bytes([seed])*512);u.mem_write(CELL,W(CTX));u.mem_write(CTX+144,W(flags));events=[]
  def mem(u,access,a,size,value,data):
   if not(P<=a<P+256 or CTX<=a<CTX+512 or a==CELL):return
   v=value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little');events.append(['w' if access==UC_MEM_WRITE else 'r',a,size,v])
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P+pointer);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else native[k])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,256)).hex(),bytes(u.mem_read(CTX,512)).hex(),u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product(range(1),[0,4,64],[0,0x5a,0xff],[0]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_PATH_BOUNDS_RESET','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'helper_fixture_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Full bounds-reset body,ordered sparse writes/full256pathguard/returningSP match with aligned object offsets and seeds. Zero childcuts; NULL/unmapped/unaligned pointerfault,physicalbus,ownership/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
