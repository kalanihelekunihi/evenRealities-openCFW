from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-sectored-bind-round236';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_error_set_4b127c'];native=[0x4b127c];cuts=[0x101010]
entries=['audio_uart_nema_cl_bind_sectored_5143d4'];orig=[0x5143d4]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('static int32_t bind236_div');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('static int32_t bind236_div')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,capacity,sectors,parent,bound,oldcap,used,align,null):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for i in range(3):
   row=[0xa5a50000+j for j in range(16)];row[2]=P+512;row[3]=0x20008000+align;row[4]=oldcap if i==2 else capacity;row[5]=used;row[6]=44;row[9]=P+64 if parent and i==0 else 0;u.mem_write(P+i*64,b''.join(W(v) for v in row))
  u.mem_write(P+512,bytes([165])*256);u.mem_write(CELL,W(CTX));u.mem_write(CTX,bytes([165])*256);u.mem_write(CTX+4,W(P+128 if bound else 0));events=[]
  def hook(uc,a,n,user):
   if a!=(cuts[0] if isc else native[0]):return
   events.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0 if null else P);u.reg_write(UC_ARM_REG_R1,sectors);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[0]] if isc else orig[0])|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,192)).hex(),bytes(u.mem_read(P+512,256)).hex(),bytes(u.mem_read(CTX,256)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=[(c,s,p,b,oc,u,0,0) for c,s,p,b,oc,u in itertools.product([0,1,128,256,512,1024,25600,0x20000000,0x80000000,0xffffffff],[0,1,2,3,4,5,8,100,0x80000000,0xffffffff],range(2),range(2),[0,8,0x80000000],[0,3])]
 cases += [(512,s,0,1,8,3,a,n) for s,a,n in itertools.product([0,2,5,100],[0,1,7],range(2))]
 for c in cases:
  a=run(False,*c);z=run(True,*c)
  if a!=z:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_SECTORED_BIND','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Full three-list/context/old-command state,error events and SP matched; one diagnostic cut. Ordered bus/concurrent mutations,pointer faults/ownership and full-image gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
