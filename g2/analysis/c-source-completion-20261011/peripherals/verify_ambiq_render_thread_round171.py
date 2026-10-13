from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-render-thread-round171';S=D/'candidate.c';W=lambda v:struct.pack('<I',v);U=0x20001000;T=0x20002000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c7700');f=Path(t)/'selected.c';f.write_text(S.read_text().split('/* Native4c7700')[0]+selected[a:]);S=f
 e=Path(t)/'test.elf';names=['audio_uart_lv_anim_init_4d46de','audio_uart_lv_thread_sync_wait_4d46e8','audio_uart_ambiq_execute_unit_4c752e','audio_uart_lv_thread_sync_delete_4d475c','audio_uart_lv_mutex_delete_4d46c2'];cs=[0x101010+i*16 for i in range(5)];ns=[0x4d46de,0x4d46e8,0x4c752e,0x4d475c,0x4d46c2]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_render_thread_4c7700']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cs)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,initial_task,initial_exit,waits,draws,initmutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(U,bytes([seed])*192);u.mem_write(U+28,W(T if initial_task else 0));u.mem_write(U+57,bytes([initial_exit]));events=[];trace=[];counts=[0]*5
  def hook(uc,a,n,user):
   targets=cs if isc else ns
   if a not in targets:return
   i=targets.index(a);counts[i]+=1;events.append((i,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(U,192)).hex()))
   if i==0 and initmutation:uc.mem_write(U+28,W(0));uc.mem_write(U+57,bytes([0]))
   if i==1 and counts[i]>=waits:
    if draws:uc.mem_write(U+28,W(T))
    else:uc.mem_write(U+57,bytes([1]))
   if i==2:
    if counts[i]>=draws:uc.mem_write(U+57,bytes([1]))
    else:uc.mem_write(U+28,W(T+counts[i]*128))
   if i==3:uc.mem_write(U+60,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,value,user):
   if U<=a<U+192:trace.append((access,a,n,value if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,U);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_render_thread_4c7700'] if isc else 0x4c7700)|1,0x600000,count=5000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(U,192))
 cases=list(itertools.product([0,1],[0,1,255],[1,2,4],[0,1,3],[0,1],[0,165]))
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
 receipt={'status':'PASS_NATIVE_AMBIQ_RENDER_THREAD_CONTROLLED_CHILDREN','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Init/wait/execute/delete children controlled; finite waits and draw sequences, exit flags, mutation, ordered shared accesses/full192unitbytes/SP compared. Void R0 ignored.','Actual synchronization, drawing and hardware remain unqualified.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
