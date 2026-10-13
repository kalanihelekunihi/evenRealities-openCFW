from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-pool-aligned-allocate-round212';S=D/'candidate.c';P=0x20001000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['xQueueSemaphoreTake','audio_uart_lv_tlsf_aligned_allocate_4d0744','audio_uart_lv_allocation_size_4d05e4','audio_uart_queue_send'];native=[0x441c44,0x4d0744,0x4d05e4,0x4417ee];cuts=[0x101010+i*16 for i in range(4)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4841d8..484234:');S=Path(t)/'selected.c';z=selected.find('\n#include',a);S.write_text((D/'candidate.c').read_text().split('/* Native4841d8')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_pool_aligned_allocate_4841d8']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,size,alignment,take,pointer,amount,total,high,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([165])*64);u.mem_write(P,W(0x20006000)+W(0x20005000)+W(total)+W(high));events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][: [2,3,1,4][i]];events.append((i,args,bytes(uc.mem_read(P,64)).hex()));ret=[take,pointer,amount,0xa5a5a5a5][i]
   if mutation==i:uc.mem_write(P,W(0x20008000)+W(0x20009000)+W(0xfffffff0)+W(3))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+64:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_R2,alignment);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_lv_pool_aligned_allocate_4841d8'] if isc else 0x4841d8)|1,0x600000,count=1500);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,64))
 cases=list(itertools.product([0,60],[0,8,32],[0,1,257],[0,0x20007000],[0,16,0xffffffff],[0,16,0xffffffff],[0,16,0xffffffff],[-1,0,1,2]))
 cases += [(size,align,take,0x20007000,16,0xfffffff0,16,-1) for size,align,take in itertools.product([1,0x80000000,0xffffffff],[1,0xffffffff],[1,0xffffffff])]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_LOCKED_ALIGNED_POOL_ALLOCATOR','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':4,'limits':['Zero size/exact semaphore1, full-width size/alignment, allocator success/failure, wrapped accounting/high-water, child-mutated handles/heap/counters, ordered accesses/events/full64bytes/result/SP matched.','Actual semaphore/queue/TLSF alignment/block-size/arena/hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
