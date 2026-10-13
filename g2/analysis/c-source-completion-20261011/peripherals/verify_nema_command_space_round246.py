from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-command-space-round246';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_error_set_4b127c','audio_uart_nema_sector_rollover_5147b0','audio_uart_nema_extend_bound_514504'];native=[0x4b127c,0x5147b0,0x514504];cuts=[0x101010,0x101020,0x101030]
entries=['audio_uart_nema_cl_get_space_514aec'];orig=[0x514aec]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('static int32_t space246_div');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('static int32_t space246_div')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,flags,capacity,used,sector,pairs,result,mutation,null):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for i in range(2):
   row=[0xa5a50000+j for j in range(16)];row[2]=P+512;row[4]=capacity;row[5]=used if i==0 else 7;row[6]=flags;row[11]=sector;u.mem_write(P+i*64,b''.join(W(v) for v in row))
  u.mem_write(CELL,W(CTX));u.mem_write(CTX,bytes([165])*1024);u.mem_write(CTX+4,W(0 if null else P));u.mem_write(CTX+516,W(P+64));events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a);arg=uc.reg_read(UC_ARM_REG_R0);events.append([k,arg,bytes(uc.mem_read(CTX+249,1)).hex()])
   if mutation==1:uc.mem_write(CELL,W(CTX+512))
   if mutation==2:uc.mem_write(CTX+4,W(P+64))
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
  def mem(uc,access,a,n,v,user):
   if P<=a<P+128 or CTX<=a<CTX+1024 or a==CELL:trace.append([access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()])
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,pairs);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[0]] if isc else orig[0])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,events,bytes(u.mem_read(P,128)).hex(),bytes(u.mem_read(CTX,1024)).hex(),bytes(u.mem_read(CELL,4)).hex(),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 cases=[(f,c,u,s,p,r,m,0) for f,c,u,s,p,r,m in itertools.product([0,8,32,40],[0,4,128,0x7fffffff],[0,1,5,0x80000000,0xffffffff],[0,4,8,0x80000000],[0,1,3,0x7fffffff,0xffffffff],[0,0x80000000],range(3))]
 cases += [(0,128,0,8,p,0,m,1) for p,m in itertools.product([0,3,0xffffffff],range(3))]
 for c in cases:
  a=run(False,*c);z=run(True,*c)
  if a!=z:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_COMMAND_SPACE_ORDERED_MEMORY','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Ordered context/cell/list accesses,child-mutated bound lists,fullstate/result/SP match. Error/rollover/extension controlled; pointer faults/ownership/physical GPU/full-image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
