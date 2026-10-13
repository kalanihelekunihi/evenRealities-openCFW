from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-vg-error-state-round193';S=D/'candidate.c';CELL=0x20074f04;P=0x20001000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('extern volatile uint32_t audio_uart_nema_vg_context_cell;');S=Path(t)/'selected.c';S.write_text('#include <stdint.h>\n'+selected[a:])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_vg_get_error_51564c','-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(CELL),str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,setter,value,error,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(P));u.mem_write(P,bytes([seed])*256);u.mem_write(P+128,W(value));trace=[]
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or P<=a<P+256:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,error);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);name='audio_uart_nema_vg_'+('set_error_51565c' if setter else 'get_error_51564c');entry=sym[name] if isc else (0x51565c if setter else 0x51564c);u.emu_start(entry|1,0x600000,count=200);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,256)),None if setter else u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 vals=[0,1,2,0x80000000,0x7fffffff,0xffffffff,0xa5a55a5a];cases=list(itertools.product([0,1],vals,vals,[0,165]))
 for c in cases:assert run(False,*c)==run(True,*c),c
 receipt={'status':'PASS_NATIVE_VG_ERROR_GET_SET','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Ordered context-cell and error read/write, full256contextbytes, getter return/SP and setter SP compared for valid context.','NULL/invalid context fault and concurrent mutation boundaries, context ownership/selection/full-image/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
