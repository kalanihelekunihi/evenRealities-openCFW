from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-poll-wait-round223';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['xQueueSemaphoreTake','g2_file_heap_error_log','audio_uart_nema_wait_irq_51400a'];native=[0x441c44,0x4733ee,0x51400a];cuts=[0x101010+i*16 for i in range(3)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native51400a');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native51400a')[0]+selected[a:z if z>=0 else len(selected)])
 fixture=Path(t)/'fixture.c';fixture.write_text('extern void audio_uart_nema_wait_irq_51400a(void);\n'+S.read_text().replace('void audio_uart_nema_wait_irq_51400a(void) {','void fixture_wait(void) {'));e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_poll_514026']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+['-Wl,--defsym=audio_uart_nema_last_submission=0x20002e08',str(fixture),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,initial,target,take,loops,handle):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x20002e08,W(initial));u.mem_write(0x20074814,W(handle));events=[];trace=[];calls=0
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   nonlocal calls
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a)
   if mode==1 and i==2:return
   r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append((i,r if i==0 else string(r[0]) if i==1 else []))
   if i==2:
    calls+=1
    if calls>=loops:uc.mem_write(0x20002e08,W(target))
   uc.reg_write(UC_ARM_REG_R0,take if i==0 else 0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if a in [0x20002e08,0x20074814]:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,target);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  entry=(sym['fixture_wait' if mode==1 else 'audio_uart_nema_poll_514026'] if isc else 0x51400a if mode==1 else 0x514026);u.emu_start(entry|1,0x600000,count=2000);returned=u.reg_read(UC_ARM_REG_PC)==0x600000;assert returned==(mode==0 or take==1)
  return events,trace,bytes(u.mem_read(0x20002e08,4)).hex(),returned,u.reg_read(UC_ARM_REG_R0) if mode==0 else None,u.reg_read(UC_ARM_REG_SP) if returned else None
 cases=[(0,initial,target,1,loops,0x20006000) for initial,target,loops in itertools.product([0,1,0x7fffffff,0x80000000,0xffffff,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffff,0xffffffff],[1,2,3])]
 cases += [(1,0,0,take,1,handle) for take,handle in itertools.product([0,1,257,0xffffffff],[0,0x20006000,0xffffffff])]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_NEMA_POLL_WAIT','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Signed current/target compare, zero-to-three controlled waits/fresh reads, semaphore1000/exactsuccess1, handle values, exact diagnostic text and native failure nonreturn loop matched.','Poll wait child and semaphore/log handlers controlled; bounded loop observation is not eventual scheduler/IRQ/hardware proof.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
