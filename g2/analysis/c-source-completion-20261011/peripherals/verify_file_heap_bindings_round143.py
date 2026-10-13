#!/usr/bin/env python3
"""Bounded original-byte/C codec allocation mutex and pool call comparison."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/codec_heap_allocate_source_candidate/allocate.c'
F=R/'g2/components/audio/file_heap_free_candidate/file_heap_free.c';D=Path(__file__).parent/'root-file-heap-bindings-round143';C=D/'candidate.c'
if '--selected' in sys.argv:C=R/'g2/components/audio/uart_thread_source_candidate/display_file_api.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(STOCK).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'allocate.o';e=t/'allocate.elf'
 objects=[]
 for source in [S,F,C]:
  obj=t/(source.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True);objects.append(str(obj))
 names={'g2_codec_heap_mutex':0x200748f8,'g2_codec_heap_pool':0x20074abc,'audio_file_mutex_acquire':0x101011,'audio_file_mutex_release':0x101021,'g2_file_pool_allocate':0x101031,'g2_file_heap_error_log':0x101041,'g2_file_close_error':0x101051,'g2_file_pool_free':0x101061}
 args=['--defsym='+k+'='+hex(v) for k,v in names.items()]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--gc-sections','-e','file_heap_allocate','-u','file_heap_free',*args,'-o',str(e),*objects],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def string(u,a):return bytes(u.mem_read(a,100)).split(b'\0',1)[0].decode('ascii')
 def run(native,kind,lock,bytes_,allocation,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
  u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  put(u,0x200748f8,0x20007700);put(u,0x20074abc,0x20008800)
  u.reg_write(A.UC_ARM_REG_R0,bytes_);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  children=({0x4497b6:'acquire',0x44981c:'release',0x4d0722:'allocate',0x4733ee:'error_log',0x4d09b4:'error',0x4d0808:'free'} if native else {0x101010:'acquire',0x101020:'release',0x101030:'allocate',0x101040:'error_log',0x101050:'error',0x101060:'free'})
  calls=[];done=[False]
  def code(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   kind=children.get(pc)
   if kind is None:return
   r0=c.reg_read(A.UC_ARM_REG_R0);r1=c.reg_read(A.UC_ARM_REG_R1);r2=c.reg_read(A.UC_ARM_REG_R2)
   if kind=='error_log':args=(string(c,r0),)
   elif kind=='error':args=(string(c,r0),string(c,r1),r2)
   else:args=(r0,r1) if kind in ('acquire','allocate','free') else (r0,)
   calls.append((kind,args))
   if kind=='acquire' and mutation==1:put(c,0x200748f8,0x20007740);put(c,0x20074abc,0x20008840)
   if kind in ['allocate','free'] and mutation==2:put(c,0x200748f8,0x20007780)
   c.reg_write(A.UC_ARM_REG_R0,lock if kind=='acquire' else allocation if kind=='allocate' else 0x12345678)
   c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start(((0x474cd2 if kind=='allocate' else 0x474d16) if native else sym['file_heap_'+kind])|1,0,count=300)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0) if kind=='allocate' else None,calls,u.reg_read(A.UC_ARM_REG_SP)
 n=0
 for case in itertools.product(['allocate','free'],[0,1,0xffffffff],[0,1,16,1000,0xffffffff],[0,0x20009000],[0,1,2]):
  a=run(True,*case);c=run(False,*case);assert a==c,(case,a,c);n+=1
 receipt={'status':'PASS_PUBLIC_FILE_HEAP_BINDINGS_CONNECTED_NATIVE','cases':n,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,F,C]},'payload_sha256':hashlib.sha256(STOCK).hexdigest(),'limits':['Actual public bridges and canonical allocate/free bodies execute; mutex,pool,log/error are controlled cuts. Exact allocation return,SP and callbacks plus mutex/pool mutation compared.','Connected TLSF/scheduler,data/layout and hardware image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
