from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-draw-area-set-round177';S=D/'candidate.c';P=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native450b5c..450b6c;');fixture=Path(t)/'selected.c';fixture.write_text('#include <stdint.h>\n'+selected[a:]);S=fixture
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_area_set_450b5c',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,kind,a,b,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for addr,data in segs:u.mem_write(addr,data)
  u.mem_write(P,bytes((i*37+seed)&255 for i in range(256)));trace=[]
  def hook(uc,access,addr,n,val,user):
   if P<=addr<P+256:trace.append((access,addr,n,val if access==17 else bytes(uc.mem_read(addr,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  name='audio_uart_lv_area_set_450b5c';native=0x450b5c;u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,a);u.reg_write(UC_ARM_REG_R2,b);u.reg_write(UC_ARM_REG_R3,seed);u.mem_write(0x200ff000,W(seed^0xffffffff))
  u.emu_start((sym[name] if isc else native)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,256)),u.reg_read(UC_ARM_REG_SP)
 cases=[(2,a,b,seed) for a,b,seed in itertools.product([0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff])]
 for case in cases:assert run(False,*case)==run(True,*case),case
 receipt={'status':'PASS_NATIVE_AREA_SET_STANDALONE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Four coordinate boundary patterns incl fifth stack argument; exact ordered four stores/full256bytes/SP. Void scratch R0 ignored.','No physical rendering or full-image proof.']};(D/'standalone-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
