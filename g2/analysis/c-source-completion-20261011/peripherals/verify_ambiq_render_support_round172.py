from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-render-support-round172';S=D/'candidate.c';W=lambda v:struct.pack('<I',v);T=0x20001000;A=0x20002000;C=0x20003000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c752e..4c7548:');f=Path(t)/'selected.c';f.write_text(S.read_text().split('/* Native4c752e')[0]+selected[a:]);S=f
 e=Path(t)/'test.elf';names=['audio_uart_ambiq_execute_drawing_4c7752','audio_uart_lv_draw_dispatch_request_48462e','audio_queue_delete'];cs=[0x101010,0x101020,0x101030];ns=[0x4c7752,0x48462e,0x441ea2]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_execute_unit_4c752e']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cs)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 entries=[('audio_uart_ambiq_execute_unit_4c752e',0x4c752e,False),('audio_uart_lv_thread_sync_delete_4d475c',0x4d475c,True),('audio_uart_lv_mutex_delete_4d46c2',0x4d46c2,True)]
 def run(isc,entry,initialized,handle,mutation,seed):
  name,native,retval=entry;u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for a in [T,A,C]:u.mem_write(a,bytes([seed])*128)
  u.mem_write(T,W(initialized));u.mem_write(T+4,W(handle));u.mem_write(T+76,W(A));events=[];trace=[]
  def hook(uc,a,n,user):
   targets=cs if isc else ns
   if a not in targets:return
   i=targets.index(a);args=() if i==1 else (uc.reg_read(UC_ARM_REG_R0),);events.append((i,args,bytes(uc.mem_read(T,128)).hex(),bytes(uc.mem_read(A,128)).hex(),bytes(uc.mem_read(C,128)).hex()))
   if mutation and i==0:uc.mem_write(T+76,W(C));uc.mem_write(T+80,W(0x12345678))
   if mutation and i==2:uc.mem_write(T,W(255));uc.mem_write(T+4,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,value,user):
   if any(x<=a<x+128 for x in [T,A,C]):trace.append((access,a,n,value if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[name] if isc else native)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0) if retval else None,u.reg_read(UC_ARM_REG_SP),tuple(bytes(u.mem_read(a,128)) for a in [T,A,C])
 cases=list(itertools.product(entries,[0,1,255,0xffffffff],[0,A,0xffffffff],[0,1],[0,165]))
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
 receipt={'status':'PASS_NATIVE_RENDER_SUPPORT_THREE_BODIES','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Drawing/dispatch/queue deletion controlled cuts; ordered shared accesses, mutated unit pointer, initialized/handle variants, full three128byte regions, applicable return/SP compared.','Actual drawing, queue deletion and hardware unproven.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
