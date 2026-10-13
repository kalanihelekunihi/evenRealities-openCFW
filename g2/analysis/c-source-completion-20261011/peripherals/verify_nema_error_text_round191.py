from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,random,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-error-text-round191';S=D/'candidate.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('struct audio_uart_nema_error_row {');S=Path(t)/'selected.c';S.write_text('#include <stdint.h>\n'+selected[a:])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_error_interpret_4b0594',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def setup():
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  return u
 native=setup();source=setup()
 def run(u,entry,error):
  u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,error);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start(entry|1,0x600000,count=5000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  p=u.reg_read(UC_ARM_REG_R0);raw=bytes(u.mem_read(p,128));return raw.split(b'\0',1)[0],u.reg_read(UC_ARM_REG_SP)
 rng=random.Random(191);cases=set(range(513));cases.update([0xffffffff,0x80000000]);cases.update(rng.getrandbits(32) for _ in range(512))
 for i in range(32):cases.update([(1<<i),(1<<i)-1,((1<<i)+1)&0xffffffff])
 n=0
 for entry,name in [(0x4b0584,'audio_uart_nema_vg_error_interpret_4b0584'),(0x4b0594,'audio_uart_nema_error_interpret_4b0594')]:
  for error in sorted(cases):
   a=run(native,entry,error);b=run(source,sym[name],error);assert a==b,(hex(entry),hex(error),a,b);n+=1
 receipt={'status':'PASS_NATIVE_SOURCE_ERROR_LABELS','cases':n,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['All listed codes, near-power boundaries, low codes and seeded full-width samples; unknown fallback, decoded text and restored SP compared.','Source-owned strings relocate; native pointer identity/layout and hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
