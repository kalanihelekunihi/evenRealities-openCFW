from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-array-external-init-round278';S=D/'candidate.c';P=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entry='audio_uart_lv_array_init_external_488440'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry,'-Wl,--defsym=audio_uart_lvgl_log=0x180001',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,buffer,count,stride,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes((seed+i*13)&255 for i in range(128)));trace=[];logs=[]
  def string(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def log(u,a,n,unused):
   if a!=(0x180000 if isc else 0x44d25c):return
   regs=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];extra=struct.unpack("<III",u.mem_read(u.reg_read(UC_ARM_REG_SP),12));logs.append([regs[0],string(regs[1]),regs[2],string(regs[3])]+[string(x) for x in extra]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,log)
  def mem(u,access,a,size,value,unused):
   if P<=a<P+128:trace.append(['w' if access==UC_MEM_WRITE else 'r',a,size,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little'))&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[P,buffer,count,stride]):u.reg_write(reg,value)
  u.reg_write(UC_ARM_REG_R4,0x12345678);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  fault=None
  try:u.emu_start((sym[entry] if isc else 0x488440)|1,0x600000,count=1000)
  except UcError as e:assert not buffer and e.errno==UC_ERR_WRITE_UNMAPPED;fault="unmapped_fail_stop_store"
  if buffer:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  else:assert fault
  return logs,trace,bytes(u.mem_read(P,128)).hex(),u.reg_read(UC_ARM_REG_SP) if buffer else None,u.reg_read(UC_ARM_REG_R4) if buffer else None,fault
 count=0
 for c in itertools.product([0,P,P+4,P+16,P+64],[0,1,0xffffffff],[0,1,4,0xffffffff],[0,0x5a,0xff]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2));raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_EXTERNAL_ARRAY_INITIALIZER','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Ordered sparse stores, buffer aliases, wrapped counts/strides, full128byteguard and returning SP/R4 match. NULL buffer logs and unmapped fail-stop existence match; real logger, array lifecycle, pointer faults and hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
