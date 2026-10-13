from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-list-controls-round233';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_error_set_4b127c','audio_uart_nema_sector_rollover_5147b0','audio_uart_nema_poll_514026'];native=[0x4b127c,0x5147b0,0x514026];cuts=[0x101010,0x101020,0x101030]
entries=['audio_uart_nema_cl_rewind_514384','audio_uart_nema_cl_submit_514cf2','audio_uart_nema_cl_wait_514d00'];orig=[0x514384,0x514cf2,0x514d00]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('/* Native514384');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native514384')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,parent,chain,bound,submission,result,mutation,null):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for i in range(3):
   row=[0xa5a50000+i*100+j for j in range(16)];row[7]=submission;row[8]=P+(i+1)*64 if chain and i<2 else 0;row[9]=P+64 if parent and i==0 else P+128 if parent==2 and i==1 else 0;u.mem_write(P+i*64,b''.join(W(v) for v in row))
  u.mem_write(CELL,W(CTX));u.mem_write(CTX,bytes([165])*256);u.mem_write(CTX+4,W(P+bound*64));events=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a);arg=uc.reg_read(UC_ARM_REG_R0);events.append([k,arg,bytes(uc.mem_read(CTX+249,1)).hex()])
   if mutation:uc.mem_write(P+28,W(0x12345678));uc.mem_write(CELL,W(CTX+512))
   uc.reg_write(UC_ARM_REG_R0,result&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0 if null else P);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[mode]] if isc else orig[mode])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,192)).hex(),bytes(u.mem_read(CTX,1024)).hex(),bytes(u.mem_read(CELL,4)).hex(),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_R0) if mode==2 else None
 cases=[(0,p,c,b,7,0,0,0) for p,c,b in itertools.product(range(3),range(2),range(3))]
 cases += [(1,0,0,0,7,r,m,n) for r,m,n in itertools.product([0,0xffffffff],range(2),range(2))]
 cases += [(2,0,0,0,s,r,m,n) for s,r,m,n in itertools.product([0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0x80000000,0xffffffff],range(2),range(2))]
 cases += [(0,0,0,0,7,0,0,1)]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_LIST_CONTROLS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Full list/context state,child events,wait result and SP matched; child contracts controlled. Cyclic/faulting pointers,concurrency,physical drivers and full-image gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
