from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,re,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-framebuffer-cleanup-round268';S=D/'candidate.c';P=0x200732e8;CUT=0x180000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
def function(name):
 m=re.search(r'void\s*\*?\s*'+re.escape(name)+r'\([^;{}]*\)\s*\{',text);assert m;a=m.start();z=text.index('{',a);depth=1;i=z+1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
helpers=['audio_uart_nema_pool_select_514050','audio_uart_nema_cl_buffer_destroy_5140c6'];H=D/'selected-helpers-fixture.c';H.write_text('#include <stdint.h>\nextern void audio_uart_lv_pool_free_48429e(void *,void *);\n'+'\n'.join(function(n) for n in helpers))
if '--selected' in sys.argv:assert S.read_text() in text
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_vg_framebuffer_destroy_5155dc','-Wl,--defsym=audio_uart_nema_vg_framebuffer_descriptor_200732e8='+hex(P),'-Wl,--defsym=audio_uart_lv_pool_free_48429e='+hex(CUT|1),str(S),str(H),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,pool,data,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(P,bytes([seed])*128);u.mem_write(P+4,W(pool));u.mem_write(P+8,W(data));events=[];accesses=[]
  def hook(u,a,size,unused):
   if a!=(CUT if isc else 0x48429e):return
   events.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
   if mutation:u.mem_write(P,b''.join(W(v) for v in [1,2,3,4]))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,size,value,unused):
   if P<=a<P+128:accesses.append(['w' if access==UC_MEM_WRITE else 'r',a,size,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little'))&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_vg_framebuffer_destroy_5155dc'] if isc else 0x5155dc)|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,accesses,bytes(u.mem_read(P,128)).hex(),u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product([0,1,2,3,4,0xffffffff],[0,0x20009000,0xffffffff],[0,0x5a,0xff],[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_FRAMEBUFFER_CLEANUP_REAL_DESTROY_POOL_SELECT','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'helper_fixture_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Actual destroy/pool-select execute,free arguments and ordered descriptor accesses/full128byteguard/SP match with free child mutations. Real free allocator,descriptor lifecycle,pointerfault/ownership/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
