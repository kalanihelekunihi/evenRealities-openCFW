from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-context-unlock-round180';S=D/'candidate.c';P=0x20001000;W=lambda v:struct.pack('<I',v&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4b0886..4b092a.');fixture=Path(t)/'selected.c';fixture.write_text(S.read_text().split('/* Native4b0886')[0]+selected[a:]);S=fixture
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_context_unlock_4b0886','-Wl,--defsym=audio_uart_lvgl_log=0x101011','-Wl,--defsym=audio_uart_lv_unlock_core=0x101021',str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,present,count,result,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*256);u.mem_write(P+140,W(count));events=[];trace=[];fault=[]
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if a==(0x101010 if isc else 0x44d25c):
    sp=uc.reg_read(UC_ARM_REG_SP);fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];args=[string(struct.unpack('<I',uc.mem_read(sp+i*4,4))[0]) for i in [1,2]] if r[2]!=301 else [];events.append(('log',r[0],string(r[1]),r[2],string(r[3]),string(fmt),args));ret=0xa5a5a5a5
   elif a==(0x101020 if isc else 0x4d4696):
    events.append(('unlock',r[0],bytes(uc.mem_read(P,256)).hex()));ret=result
    if mutation:uc.mem_write(P+140,W(0x12345678))
   else:return
   uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+256:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  def bad(uc,access,a,n,v,user):fault.append((a,n,v));return False
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if present else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  try:u.emu_start((sym['audio_uart_ambiq_context_unlock_4b0886'] if isc else 0x4b0886)|1,0x600000,count=2000)
  except UcError:assert fault==[(0xffffffff,4,0)],fault
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,fault,None if fault else u.reg_read(UC_ARM_REG_R0),None if fault else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,256))
 cases=list(itertools.product([0,1],[0,1,2,0x80000000,0xffffffff],[0,1,255,256,257,0xffffffff],[0,1],[0,165]))
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_AMBIQ_CONTEXT_UNLOCK','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Logger/mutex-unlock cuts; NULL/count assertions exact fault, volatile decrement/reread ordering, low-byte result, child count mutation, full256unitbytes, applicable return/SP compared.','Actual recursive mutex/scheduling/hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
