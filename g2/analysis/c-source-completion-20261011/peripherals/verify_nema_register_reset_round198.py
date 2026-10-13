from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-register-reset-round198';S=D/'candidate.c';CELL=0x20002e08;BASE=0x40090000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entries=[(0x514184,'audio_uart_nema_reset_last_submission_514184'),(0x51418e,'audio_uart_nema_last_submission_51418e'),(0x51403c,'audio_uart_nema_reg_read_51403c'),(0x514046,'audio_uart_nema_reg_write_514046')]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native514184..514194.');z=selected.index('#include <stdint.h>',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native514184')[0]+selected[a:z])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_reg_read_51403c','-Wl,--defsym=audio_uart_nema_last_submission='+hex(CELL),'-Wl,--defsym=audio_uart_nema_register_base=0x78f2f4',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,which,offset,value,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(BASE,4096)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(value));u.mem_write(BASE,bytes([seed])*1024);trace=[]
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or BASE<=a<BASE+1024 or 0x78f2f4<=a<0x78f2f8:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,offset);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);entry=sym[entries[which][1]] if isc else entries[which][0];u.emu_start(entry|1,0x600000,count=200);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(CELL,4)),bytes(u.mem_read(BASE,1024)),u.reg_read(UC_ARM_REG_R0) if which in [1,2] else None,u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product(range(4),[0,4,8,252,256,508,1020],[0,1,0x80000000,0xffffffff,0xa5a55a5a],[0,165]))
 for case in cases:assert run(False,*case)==run(True,*case),case
 receipt={'status':'PASS_NATIVE_REGISTER_RESET_ACCESSORS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Ordered base-cell/RAM-backed register and last-submission accesses, full1024registerbytes/state/meaningful return/SP compared.','Only aligned in-window offsets; wrapped/fault boundaries, physical MMIO effects and data ownership/layout remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
