from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-native-trig-mode-wrappers-round294';S=D/'candidate.c';entries=['audio_uart_float_trig_mode1_50968c','audio_uart_float_trig_mode0_509690'];native=[0x50968c,0x509690]
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_float_trig_core_5094c0=0x180001',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,k,bits,rounding,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  events=[]
  def hook(u,a,n,unused):
   if a!=(0x180000 if isc else 0x5094c0):return
   mode=u.reg_read(UC_ARM_REG_R0);value=u.reg_read(UC_ARM_REG_S0);events.append([mode,value]);assert mode==1-k and value==bits
   u.reg_write(UC_ARM_REG_S0,bits^0x12345678);u.reg_write(UC_ARM_REG_R0,0xfeedbeef)
   if mutation:u.reg_write(UC_ARM_REG_FPSCR,(rounding<<22)|0x11)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_FPSCR,rounding<<22);u.reg_write(UC_ARM_REG_S0,bits);u.reg_write(UC_ARM_REG_R0,0x56789abc);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else native[k])|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_FPSCR),u.reg_read(UC_ARM_REG_SP)
 count=0
 for c in itertools.product(range(2),[0,0x80000000,1,0x3f800000,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffffffff],range(4),[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2));raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_TRIG_MODE_WRAPPERS_VFP_PCS','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Both mode wrappers preserve exactS0bits andsendR0mode; controlledcore S0return/FPSCR and SP match for zeros/subnormal/finite/inf/NaNs acrossroundingmodes. Actualcore math/fullpostprocessor/FPUownership/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
