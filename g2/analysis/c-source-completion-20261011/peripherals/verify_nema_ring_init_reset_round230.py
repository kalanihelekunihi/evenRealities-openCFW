from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-ring-init-reset-round230';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_error_set_4b127c','audio_uart_nema_buffer_flush_5140ea','audio_uart_nema_reg_write_514046'];native=[0x4b127c,0x5140ea,0x514046];cuts=[0x101010+i*16 for i in range(3)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native523bf8');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native523bf8')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_ring_initialize_523bf8']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+['-Wl,--defsym=audio_uart_nema_ring_descriptor=0x20073db0',str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,size,initialize,capacity,physical,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xa0001000,4096)
  for a,data in segs:u.mem_write(a,data)
  data=0x20002000;desc=0x20073db0;cap=((size//4)-4)&0xffffffff if mode==0 and 0<size<0x80000000 else capacity;tail=(data+cap*4)&0xffffffff
  u.mem_write(P,W(size)+W(3)+W(data)+W(physical)+W(7)+W(9)+bytes(8));u.mem_write(desc,W(P)+W(data)+W(physical)+W(capacity)+W(size));u.mem_write(tail,bytes([165])*16);events=[];trace=[];writes=0
  def hook(uc,a,n,user):
   nonlocal writes
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append((i,r if i==2 else r[:1]))
   if i==2:writes+=1
   if mutation==1 and i==1 or mutation>=2 and i==2 and writes==mutation-1:
    uc.mem_write(desc,W(0x20001100));uc.mem_write(desc+8,W(0x20009003));uc.mem_write(desc+16,W(0x12345678))
   uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+32 or desc<=a<desc+20 or tail<=a<tail+16:trace.append((access,a,n,v&((1<<(8*n))-1) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,initialize);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);entry=sym['audio_uart_nema_child_523c88' if mode else 'audio_uart_nema_ring_initialize_523bf8'] if isc else 0x523c88 if mode else 0x523bf8;u.emu_start(entry|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,bytes(u.mem_read(P,32)).hex(),bytes(u.mem_read(desc,20)).hex(),bytes(u.mem_read(tail,16)).hex(),u.reg_read(UC_ARM_REG_R0) if mode==0 else None,u.reg_read(UC_ARM_REG_SP)
 cases=[(0,size,init,16,physical,m) for size,init,physical,m in itertools.product([0,1,15,16,32,64,256,0x7fffffff,0x80000000,0xffffffff],[0,1,257],[0,0x20008003,0xffffffff],range(6))]
 cases += [(1,256,0,cap,physical,m) for cap,physical,m in itertools.product([0,1,4,16,0xffffffff,0x7fffffff],[0,0x20008003,0xffffffff],range(6))]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_NEMA_RING_INIT_RESET','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':3,'limits':['Signed size-positive gate/allsize recording, initialize fullwidth flag, wrapped capacity/tail pointers with mapped huge positive size,specific tail-store order,reset,fresh descriptors across flush/register mutations,ordered accesses/fullstate/result/SP matched.','Error/flush/register handlers controlled; mapped addresses do not establish physical allocation,ownership/NULL faults/cache/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
