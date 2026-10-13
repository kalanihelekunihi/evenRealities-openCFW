from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-buffer-aligned-connected-round214';S=B/'root-nema-buffer-create-round211/candidate.c';P=0x20001000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
 if '--selected' in sys.argv:
  a=selected.index('/* Native514070..5140c6:');S=Path(t)/'selected.c';S.write_text((B/'root-nema-buffer-create-round211/candidate.c').read_text().split('/* Native514070')[0]+selected[a:selected.index('#include <stdint.h>',a)])
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('void *audio_uart_nema_pool_select_514050(uint32_t pool_id) {');z=selected.index('/* Native5140c6',a);pool=Path(t)/'pool.c';pool.write_text('#include <stdint.h>\n'+selected[a:z]);e=Path(t)/'test.elf';copy=R/'components/audio/uart_thread_source_candidate/byte_copy.c';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_buffer_create_514070','-Wl,--defsym=audio_uart_lv_pool_allocate_484180=0x101011','-Wl,--defsym=xQueueSemaphoreTake=0x101031','-Wl,--defsym=audio_uart_lv_tlsf_aligned_allocate_4d0744=0x101041','-Wl,--defsym=audio_uart_lv_allocation_size_4d05e4=0x101051','-Wl,--defsym=audio_uart_queue_send=0x101061',str(S),str(pool),str(copy),str(B/'root-lv-pool-aligned-allocate-round212/candidate.c'),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,id,flag,size,result,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  p=0x20000370 if id==2 else 0x20000338 if id==3 else 0x20000354;u.mem_write(p,bytes([seed])*28);u.mem_write(p+24,bytes([flag]));u.mem_write(p,W(0x20006000)+W(0x20005000)+W(16)+W(32));u.mem_write(P,bytes([seed])*64);events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=[0x101010,0x101020] if isc else [0x484180,0x4841d8]
   extra=[0x101030,0x101040,0x101050,0x101060] if isc else [0x441c44,0x4d0744,0x4d05e4,0x4417ee]
   if a in extra:
    j=extra.index(a);args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][:[2,3,1,4][j]];events.append((j+2,args));uc.reg_write(UC_ARM_REG_R0,[1,result,64,0xa5a5a5a5][j]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if a not in addresses or addresses.index(a)==1:return
   i=addresses.index(a);events.append((i,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2) if i else None));uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+64 or p<=a<p+28:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,id);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_buffer_create_514070'] if isc else 0x514070)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,64)),bytes(u.mem_read(p,28))
 cases=list(itertools.product([0,1,2,3,4,0xff,0xa5000002,0xffffffff],[0,1,255],[0,1,31,32,33,1024,0xffffffe0,0xffffffff,0x80000000],[0,0x20007000,0xffffffe0],[0,165]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a[:-2],'source':b[:-2]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_CONNECTED_BUFFER_CREATE_ACTUAL_ALIGNED_ALLOCATOR','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'copy_sha256':hashlib.sha256(copy.read_bytes()).hexdigest(),'pool_selector_sha256':hashlib.sha256(pool.read_bytes()).hexdigest(),'aligned_candidate_sha256':hashlib.sha256((B/'root-lv-pool-aligned-allocate-round212/candidate.c').read_bytes()).hexdigest(),'child_cuts':5,'limits':['Cache flag/32byte size rounding including overflow, IDs0/1/2 aligned8 vs general, full-width pool-ID and pointer/failure descriptor, ordered pool/output accesses/full92bytes/SP compared. Actual poolselector and copy execute.','Actual aligned wrapper/accounting executes; general allocator, queue/TLSF/block-size children controlled; output alias/NULL faults, actual allocator/physical mapping/pool ownership and hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
