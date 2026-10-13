from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-vg-path-create-round242';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_node_allocate_51416c','audio_uart_nema_vg_set_error_51565c'];native=[0x51416c,0x51565c];cuts=[0x101010,0x101020]
entries=['audio_uart_nema_vg_path_create_514ebc'];orig=[0x514ebc]
assert (B/'root-nema-matrix-identity-round240/candidate.c').read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text(), 'Real matrix fixture differs from selected production body'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('/* Native514ebc');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native514ebc')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),str(B/'root-nema-matrix-identity-round240/candidate.c'),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,failed,seed,offset,low):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  if low:u.mem_map(0,4096);u.mem_write(0,bytes([165])*4096)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*256);events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a);arg=uc.reg_read(UC_ARM_REG_R0);events.append([k,arg]);uc.reg_write(UC_ARM_REG_R0,0 if failed else P+offset if k==0 else 0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  from unicorn import UC_HOOK_MEM_WRITE,UcError
  def mem(uc,access,a,n,v,user):
   if P<=a<P+256 or a==132:trace.append([a,n,v])
  u.hook_add(UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=False
  try:u.emu_start((sym[entries[0]] if isc else orig[0])|1,0x600000,count=3000)
  except UcError:
   if not(failed and not low):raise
   fault=True
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,bytes(u.mem_read(P,256)).hex(),bytes(u.mem_read(0,256)).hex() if low else None,fault,None if fault else u.reg_read(UC_ARM_REG_R0),None if fault else u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product(range(2),[0,165,255],[0,4,16],range(2)))
 for c in cases:
  a=run(False,*c);z=run(True,*c)
  if a!=z:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_VG_PATH_CONSTRUCTOR_REAL_MATRIX_ORDERED_STORES','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'matrix_source_sha256':hashlib.sha256((B/'root-nema-matrix-identity-round240/candidate.c').read_bytes()).hexdigest(),'matrix_selected_text_verified':True,'limits':['Real matrix identity; allocation/error controlled. Ordered stores/full256bytes,return/SP,pre-null absolute store and mapped/unmappedNULL outcomes match. Exact fault instruction/FPU ownership/allocator/physical effects/full-image gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
