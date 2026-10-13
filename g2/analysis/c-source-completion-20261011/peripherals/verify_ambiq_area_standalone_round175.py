from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-area-leaves-round175';S=D/'candidate.c';P=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_area_copy_4c73c4',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,kind,a,b,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for addr,data in segs:u.mem_write(addr,data)
  u.mem_write(P,bytes((i*37+seed)&255 for i in range(256)));trace=[]
  def hook(uc,access,addr,n,val,user):
   if P<=addr<P+256:trace.append((access,addr,n,val if access==17 else bytes(uc.mem_read(addr,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if kind==0:
   name='audio_uart_ambiq_area_copy_4c73c4';native=0x4c73c4;u.reg_write(UC_ARM_REG_R0,P+a);u.reg_write(UC_ARM_REG_R1,P+b)
  else:
   name='audio_uart_ambiq_area_move_450bb2';native=0x450bb2;u.mem_write(P,W(seed,0x80000000,0xffffffff,0x7fffffff));u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,a);u.reg_write(UC_ARM_REG_R2,b)
  u.emu_start((sym[name] if isc else native)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,256)),u.reg_read(UC_ARM_REG_SP)
 cases=[(0,a,b,seed) for a,b,seed in itertools.product(range(0,36,4),range(0,36,4),[0,165,255])]
 cases +=[(1,a,b,seed) for a,b,seed in itertools.product([0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0xffffffff])]
 for case in cases:assert run(False,*case)==run(True,*case),case
 receipt={'status':'PASS_NATIVE_AREA_COPY_MOVE_STANDALONE','cases':len(cases),'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Aligned overlap in both directions/equal/disjoint; wrapped coordinate boundary inputs; exact ordered reads/writes/full256bytes/SP. Void scratch R0 ignored.','No physical rendering or full-image proof.']};(D/'standalone-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
