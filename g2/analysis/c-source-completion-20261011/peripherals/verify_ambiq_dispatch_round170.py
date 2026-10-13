from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-dispatch-round170';S=D/'candidate.c';W=lambda v:struct.pack('<I',v);U=0x20001000;T=0x20002000;L=0x20003000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c76a8');f=Path(t)/'selected.c';f.write_text(S.read_text().split('/* Native4c76a8')[0]+selected[a:]);S=f
 e=Path(t)/'test.elf';names=['audio_uart_lv_draw_get_available_task_48463a','audio_uart_lv_draw_layer_alloc_buf_484836','audio_uart_lv_thread_sync_signal_4d4724'];cs=[0x101010,0x101020,0x101030];ns=[0x48463a,0x484836,0x4d4724]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_dispatch_4c76a8']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cs)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,busy,task,buf,inited,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(U,bytes([seed])*128);u.mem_write(T,bytes([seed])*128);u.mem_write(U+28,W(T if busy else 0));u.mem_write(U+56,bytes([inited]));events=[];trace=[]
  def hook(uc,a,n,user):
   targets=cs if isc else ns
   if a not in targets:return
   i=targets.index(a);events.append((i,tuple(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][:3 if i==0 else 1]),bytes(uc.mem_read(U,128)).hex(),bytes(uc.mem_read(T,128)).hex()))
   if mutation==i+1:uc.mem_write(U+56,bytes([0 if inited else 1]));uc.mem_write(U+28,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,[T if task else 0,L if buf else 0,1][i]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,value,user):
   if U<=a<U+128 or T<=a<T+128:trace.append((access,a,n,value if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,U);u.reg_write(UC_ARM_REG_R1,L);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_dispatch_4c76a8'] if isc else 0x4c76a8)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(U,128)),bytes(u.mem_read(T,128))
 cases=list(itertools.product([0,1],[0,1],[0,1],[0,1,255],range(4),[0,165]))
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
 receipt={'status':'PASS_NATIVE_AMBIQ_DISPATCH','cases':len(cases),'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'selected': '--selected' in sys.argv,'limits':['Task lookup, layer allocation and sync are controlled cuts; busy/NULL/inited paths and child mutations, ordered reads/writes, full unit/task state and return/SP compared.','Physical GPU/rendering and full-image completion unproven.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
