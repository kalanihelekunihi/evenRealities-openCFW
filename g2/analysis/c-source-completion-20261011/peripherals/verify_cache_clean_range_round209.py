from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-cache-clean-range-round209';S=D/'candidate.c';P=0x20001000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('static uint32_t clean_read(uint32_t a)');S=Path(t)/'selected.c';S.write_text('#include <stdint.h>\n'+selected[a:])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_cache_clean_range_47510e',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,present,ccr,ccsidr,address,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe0000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,W(address)+W(size));u.mem_write(0xe000ed14,W(ccr));u.mem_write(0xe000ed80,W(ccsidr));trace=[]
  def hook(uc,a,n,user):
   code=bytes(uc.mem_read(a,n))
   if code==bytes.fromhex('bff34f8f'):trace.append(('DSB',))
   elif code==bytes.fromhex('bff36f8f'):trace.append(('ISB',))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+8 or 0xe000ed00<=a<0xe000f000:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if present else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_cache_clean_range_47510e'] if isc else 0x47510e)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,8)),bytes(u.mem_read(0xe000ed00,0x300))
 cases=list(itertools.product([0,1],[0,1<<16,(1<<16)|1],[0,(1<<13)|(1<<3),(2<<13)|(3<<3)],[0,1,31,32,0xfffffff0],[0,1,31,32,33,64,0xffffffff,0x80000000]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_trace':a[0],'source_trace':b[0]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_SCB_CACHE_CLEAN_RANGE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Cache enabled/disabled, NULL all-set/way, signed size rejection, unaligned ranges/wrapped addresses, ordered range/MMIO accesses/DSB-ISB instructions/state/result/SP compared with RAM-backed SCB.','Physical cache/barrier effects, maximum geometry/long ranges/invalid pointer faults and hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
