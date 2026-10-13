from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-blend-clear-round186';S=D/'candidate.c';P=0x20001000;ALT=0x20002000;CELL=0x200746c0;W=lambda v:struct.pack('<I',v)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 t=Path(t)
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4b075e..4b077e:');z=selected.index('#include <stdint.h>',a);fixture=t/'selected-blend.c';fixture.write_text(S.read_text().split('/* Native4b075e')[0]+selected[a:z]);S=fixture
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c791a..4c7920;');z=selected.index('/* Native4b0c8a',a);getter=t/'getter.c';getter.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_ambiq_unit_cell[];\n'+selected[a:z]);e=t/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_blend_clear_4b075e','-Wl,--defsym=audio_uart_ambiq_unit_cell=0x200746c0',str(S),str(getter),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,present,default,seed,old):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(default));u.mem_write(P,bytes([seed])*128);u.mem_write(ALT,bytes([seed^255])*128);u.mem_write(P+80,W(old));u.mem_write(ALT+80,W(old^0xffffffff));trace=[]
  def hook(uc,access,a,n,v,user):
   if P<=a<P+128 or ALT<=a<ALT+128 or CELL<=a<CELL+4:trace.append((access,a,n,(v&((1<<(n*8))-1)) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if present else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_blend_clear_4b075e'] if isc else 0x4b075e)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,128)),bytes(u.mem_read(ALT,128)),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1],[P,ALT],[0,1,165,255],[0,1,0x12345678,0xffffffff]))
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   print(case,a[0],b[0],a[-1],b[-1]);raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_BLEND_CLEAR_REAL_DEFAULT_GETTER','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['No child cuts, actual default getter; passed/defaultunit distinction, ordered zero-word/threeffbyte stores, full256unitbytes/SP. Void scratch R0 ignored.','PhysicalGPU/fullimage unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
