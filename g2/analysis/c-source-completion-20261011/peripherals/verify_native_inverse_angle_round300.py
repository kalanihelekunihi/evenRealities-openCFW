from pathlib import Path
import tempfile,subprocess,json,hashlib,itertools,sys,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-native-inverse-angle-round300';S=D/'candidate.c';H=B/'root-native-float-sqrt-round295/candidate.c';entries=['audio_uart_float_inverse_core_55e99c','audio_uart_float_inverse_ratio_58ec74','audio_uart_float_inverse_magnitude_58ecbc'];native=[0x55e99c,0x58ec74,0x58ecbc];CELL=0x20074f14
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert H.read_text() in selected
if '--selected' in sys.argv:assert S.read_text() in selected
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_float_math_error_cell_20074f14='+hex(CELL),str(S),str(H),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def run(isc,k,mode,bits,fpscr):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  trace=[];u.mem_write(CELL,bytes([0xa5])*16)
  def mem(u,access,a,n,value,unused):
   if CELL<=a<CELL+16:trace.append(["w" if access==UC_MEM_WRITE else "r",a,n,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,n),"little"))&((1<<(8*n))-1)])
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem)
  u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_FPSCR,fpscr);u.reg_write(UC_ARM_REG_S0,bits);u.reg_write(UC_ARM_REG_S16,0x12345678);u.reg_write(UC_ARM_REG_R0,mode)
  for i,r in enumerate(saved):u.reg_write(r,0x12340000+i)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[k]] if isc else native[k])|1,0x600000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;assert [u.reg_read(r) for r in saved]==[0x12340000+i for i in range(8)]
  return u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_FPSCR),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_S16),trace,bytes(u.mem_read(CELL,16)).hex()
 count=0;randomizer=random.Random(300)
 values=[0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x3fc90fdb,0xbfc90fdb,0x40490fdb,0xc0490fdb,0x4f000000,0xcf000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345,0x7fa12345,0xffa12345,0x7fffffff,0xffffffff,0x39800000,0xb9800000]
 values+= [v+delta&0xffffffff for v in [0x39800000,0x3e8930a4,0x3f3504f4,0x3f800000,0x4c800000] for delta in [-1,0,1]]
 values+=[randomizer.getrandbits(32) for _ in range(16)]
 control_states=[(mode<<22)|extra for mode in range(4) for extra in [0,0x0300009f]]
 cases=list(itertools.product([0],range(16),values,control_states))+list(itertools.product([1,2],[0xdeadbeef],values,control_states))
 for c in cases:
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2));raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_INVERSE_CORE_REAL_UNARY_DOMAIN_GRAPH','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Fullinversecore(mode0..15) andactualunaryentries/domainhandler,S0resultbits/finalFPSCR/SP/S16/allcallee-savedcore registers/orderederrorstore/full16guard match acrosspolynomial/reciprocal/threshold/domain boundaries,zeros/subnormals/finite/inf/NaNs/randominputs,fourroundingmodes/FZ/DN/stickyflags. Larger coremodeindices/APSR/otherABIclobbers/exceptionenabled/FPUownership/layout/hardware remain. Noopcodeblob.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
