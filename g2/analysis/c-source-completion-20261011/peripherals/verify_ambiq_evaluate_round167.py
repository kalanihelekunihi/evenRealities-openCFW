from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-evaluate-round167';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);T=0x20001000;DS=0x20002000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_evaluate_4c7548','-Wl,--defsym=audio_uart_ambiq_color_format_src_4b05a4=0x101011',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,typ,gradient,blend,cf,mapped,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(T,bytes([seed])*128);u.mem_write(DS,bytes([seed])*128);u.mem_write(T+4,bytes([typ]));u.mem_write(T+84,W(DS));u.mem_write(DS+47,bytes([gradient]));u.mem_write(DS+67,bytes([gradient]));u.mem_write(DS+81,bytes([blend]));u.mem_write(DS+32,W(0x12340000|(cf<<8)|0xab));events=[];trace=[]
  def hook(uc,a,n,user):
   if a!=(0x101010 if isc else 0x4b05a4):return
   events.append(('map',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(T,128)).hex()))
   if mutation:uc.mem_write(T+84,W(0x20003000));uc.mem_write(DS+81,bytes([2 if mutation==1 else 0]))
   uc.reg_write(UC_ARM_REG_R0,mapped&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,value,user):
   if T<=a<T+128 or DS<=a<DS+128:trace.append((access,a,n,value if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,T);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sym['audio_uart_ambiq_evaluate_4c7548'] if isc else 0x4c7548)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,128)),bytes(u.mem_read(DS,128))
 cases=[(typ,0,0,16,0,0,seed) for typ,seed in itertools.product(range(256),[0,0xa5])]
 cases += [(typ,g,0,16,0,0,0xa5) for typ,g in itertools.product([1,10],range(256))]
 cases += [(6,0,blend,cf,mapped,mutation,0xa5) for blend,cf,mapped,mutation in itertools.product(range(8),[0,15,16,18,255],[-1,0,16],[0,1,2])]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
 receipt={'status':'PASS_NATIVE_AMBIQ_EVALUATOR_TRACE','cases':len(cases),'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Format mapper controlled cut; all256tasktypes/allgradientbytes,blendbits/format rejection/childdescriptor mutation,full task/descriptor bytes,ordered field read/write trace,return0/SP compared.','No actual rendering or mapper implementation/fullimage proof.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
