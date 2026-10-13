from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-cl-unbind-round195';S=D/'candidate.c';CELL=0x20074efc;P=0x20001000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native5144ba..5144fa:');S=Path(t)/'selected.c';S.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_context_cell[];\n'+selected[a:])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_cl_unbind_5144ba','-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL),str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,present,capacity,used,flags,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(P));u.mem_write(P,bytes([seed])*256);u.mem_write(P+4,W(P+256 if present else 0));u.mem_write(P+256,bytes([seed])*64);u.mem_write(P+264,W(P+512));u.mem_write(P+272,W(capacity));u.mem_write(P+276,W(used));u.mem_write(P+280,W(flags));u.mem_write(P+512,bytes([seed])*256);trace=[]
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or P<=a<P+768:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);entry=sym['audio_uart_nema_cl_unbind_5144ba'] if isc else 0x5144ba;u.emu_start(entry|1,0x600000,count=300);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,768)),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1],[0,1,2,3,8,0x7fffffff,0x80000000,0xffffffff],[0,1,2,6],[0,8,32,40,0xffffffff],[0,165]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_trace':a[0],'source_trace':b[0]},indent=2)+'\n');raise AssertionError(c)

 receipt={'status':'PASS_NATIVE_COMMAND_LIST_UNBIND','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Ordered context/list/command accesses, signed capacity test, flags, full768bytes and SP compared for valid small used indexes.','Invalid context/command pointer faults and wrapped large used indexes, selection/connection/full-image/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
