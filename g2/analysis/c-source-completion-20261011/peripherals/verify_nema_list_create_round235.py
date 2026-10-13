from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-list-create-round235';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_buffer_create_514070'];native=[0x514070];cuts=[0x101010]
entries=['audio_uart_nema_cl_create_sized_514278'];orig=[0x514278]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('/* Native514278');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native514278')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,requested,actual,physical,failed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([165])*96);events=[]
  def hook(uc,a,n,user):
   if a!=(cuts[0] if isc else native[0]):return
   ptr=uc.reg_read(UC_ARM_REG_R0);events.append([uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)])
   uc.mem_write(ptr,b''.join(W(v) for v in [actual,0,0 if failed else P+512,physical]));uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,requested);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[0]] if isc else orig[0])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,96)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1,102400,0xffffffff],[0,1,7,8,15,32,0x7fffffff,0x80000000,0xfffffff9,0xffffffff],[0,0x20009003,0xffffffff],range(2)))
 for c in cases:
  a=run(False,*c);z=run(True,*c)
  if a!=z:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_LIST_CREATE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Full60byte output and36byte guard,buffer-child arguments and SP matched; buffer allocation controlled. Pointer faults,ownership,ordered bus and full-image gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
