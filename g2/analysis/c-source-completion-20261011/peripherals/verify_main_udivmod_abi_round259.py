from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-main-udivmod-abi-round259';S=D/('original.c' if '--original' in sys.argv else 'candidate.c')
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
if '--selected' in sys.argv:assert S.read_bytes()==(R/'components/audio/uart_power_config_offline/division_support.c').read_bytes()
values=[0,1,2,3,65535,65536,65537,0xffffff,0x1000000,0x1000001,0xffffffff,0x100000000,0x100000001,0x7fffffffffffffff,0x8000000000000000,0xffffffff00000000,0xffffffffffffffff]
cases=list(itertools.product(values,values));rng=random.Random(0x47cc60);cases += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(1024)];cases += [(rng.getrandbits(64),rng.choice(values[:11])) for _ in range(256)]
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,__aeabi_uldivmod',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,n,d):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[n&0xffffffff,n>>32,d&0xffffffff,d>>32]):u.reg_write(reg,v)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for i,reg in enumerate(saved):u.reg_write(reg,0xabc00000+i*17)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['__aeabi_uldivmod'] if isc else 0x47cc60)|1,0x600000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  regs=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];assert [u.reg_read(r) for r in saved]==[0xabc00000+i*17 for i in range(8)];assert u.reg_read(UC_ARM_REG_SP)==0x200ff000
  return regs
 for c in cases:
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/('original-mismatch.json' if '--original' in sys.argv else 'candidate-mismatch.json')).write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');assert '--original' in sys.argv,c;print('EXPECTED_ORIGINAL_ABI_MISMATCH',c);sys.exit(0)
  q,r=divmod(*c) if c[1] else (c[0],0);assert a==[q&0xffffffff,q>>32,r&0xffffffff,r>>32],c
 assert '--original' not in sys.argv
 receipt={'status':'PASS_NATIVE_FULL_UNSIGNED_DIVISION_ABI','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['R0..R3 quotient/remainder,callee-saved registers/SP and independent integer oracle matched. Native zero callback executes unchanged no-op. Exact bytes/timing/stack scratch/interrupt/fault/whole-image/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
