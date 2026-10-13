from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-word-fill-round187';S=D/'candidate.c';P=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=D/'fixture.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O0','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_word_fill_4d555c',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,zero,size,pattern):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([165])*512);trace=[]
  def hook(uc,access,a,n,v,user):
   if P<=a<P+512:trace.append((a,n,v))
  u.hook_add(UC_HOOK_MEM_WRITE,hook);u.hook_add(UC_HOOK_CODE,lambda *args:None);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_R2,pattern);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  name='audio_uart_lv_memzero_48949c' if zero else 'audio_uart_lv_word_fill_4d555c';native=0x48949c if zero else 0x4d555c
  u.emu_start((sym[name] if isc else native)|1,0x600000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x600000,(isc,zero,size,pattern,hex(u.reg_read(UC_ARM_REG_PC)))
  return trace,bytes(u.mem_read(P,512)),None if zero else u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1],range(129),[0,1,0xff,0x12345678,0x80000000,0xffffffff]))
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_trace':a[0],'source_trace':b[0],'native_return':a[2],'source_return':b[2]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_WORD_FILL_AND_ZERO','cases':len(cases),'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Aligned destinations, lengths0..128, six word patterns, exact store widths/order/full512bytes/SP and fill return pointer compared; zero void scratchR0 ignored.','Unaligned fault behavior and physical RAM/cache/fullimage behavior not proved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
