from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-framebuffer-setter-round266';S=D/'candidate.c';P=0x200732e8
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
entries=['audio_uart_nema_vg_framebuffer_store_5155e4','audio_uart_nema_vg_framebuffer_get_51562e'];native=[0x5155e4,0x51562e]
with tempfile.TemporaryDirectory() as t:
 source=Path(t)/'candidate.c';source.write_text('#include <stdint.h>\ntypedef struct {uint32_t words[4];} audio_uart_vg_framebuffer_264;\n'+S.read_text());e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_vg_framebuffer_descriptor_200732e8='+hex(P),str(source),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,k,width,height,seed,rounding):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*128);sp=0x200ff000;u.mem_write(sp,W(0x76543210)+W(0xfedcba98));events=[]
  def mem(u,access,a,size,value,data):
   if P<=a<P+128:events.append([a,size,value&((1<<(size*8))-1)])
  u.hook_add(UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_FPSCR,rounding<<22);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[width,height,0x12345678,0x89abcdef]):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else native[k])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,128)).hex(),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_R0) if k else None,u.reg_read(UC_ARM_REG_FPSCR)
 count=0
 for c in itertools.product(range(2),[0,1,0x1000001,0x7fffffff,0x80000000,0xffffffff],[0,1,0x1000003,0x7fffffff,0x80000000,0xffffffff],[0,0x5a,0xff],range(4)):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_FRAMEBUFFER_SETTER_GETTER','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Ordered watched writes/full128byteguard/SP and getter address matched,including signed dimensions,rounding boundaries and all four FPSCR rounding modes/final FPSCR. Storage lifetime/initialization/placement,FPU ownership/other FPSCR controls,pointerfault/bus/hardware/full-image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
