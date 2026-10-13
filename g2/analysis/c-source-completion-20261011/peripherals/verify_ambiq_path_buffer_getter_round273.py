from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-path-buffer-getter-round273';S=D/'candidate.c';P=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entry='audio_uart_ambiq_get_path_buffers_5fa21c'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry,str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,outputs,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes((seed+i*13)&255 for i in range(128)));trace=[]
  def mem(u,access,a,size,value,unused):
   if P<=a<P+128:trace.append(['w' if access==UC_MEM_WRITE else 'r',a,size,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little'))&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[P]+list(outputs[:3])):u.reg_write(reg,value)
  u.reg_write(UC_ARM_REG_R4,0x12345678);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<I',outputs[3]));u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sym[entry] if isc else 0x5fa21c)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,128)).hex(),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_R4)
 count=0
 for offsets in itertools.product([0,4,8,12,32],repeat=4):
  for seed in [0,0x5a,0xff]:
   args=tuple(P+v for v in offsets);n=run(False,args,seed);c=run(True,args,seed)
   if n!=c:(D/'mismatch.json').write_text(json.dumps({'offsets':offsets,'seed':seed,'native':n,'candidate':c},indent=2));raise AssertionError(offsets)
   count+=1
 receipt={'status':'PASS_NATIVE_PATH_BUFFER_GETTER','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':0,'limits':['Ordered reads and writes, all output aliases with four path fields or shared separate output, full128byteguard, SP and R4 match. Unaligned/unmapped pointers, concurrency, ownership and hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
