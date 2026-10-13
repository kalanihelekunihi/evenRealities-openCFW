from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-gpu-reinit-round202';S=D/'candidate.c';CELL=0x20074efc;P=0x20001000;ALT=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_reg_read_51403c','audio_uart_nema_cl_unbind_5144ba','audio_uart_lv_memzero_48949c','audio_uart_nema_child_523c88','audio_uart_nema_reg_write_514046','audio_uart_nema_child_523304','audio_uart_nema_child_5138a4','audio_uart_nema_child_514846','audio_uart_nema_child_522602','audio_uart_nema_child_52296a','audio_uart_nema_child_52262e','audio_uart_nema_child_52261a'];native=[0x51403c,0x5144ba,0x48949c,0x523c88,0x514046,0x523304,0x5138a4,0x514846,0x522602,0x52296a,0x52262e,0x52261a];cuts=[0x101010+i*16 for i in range(len(names))]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4b11b0..4b127c.');S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native4b11b0')[0]+selected[a:selected.index('#include <stdint.h>',a)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_gpu_reinit_4b11b0','-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,tag,caps,features,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(P));u.mem_write(P,bytes([seed])*256);u.mem_write(ALT,bytes([90])*256);events=[];trace=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);args=[r0,r1] if i in [2,4,7] else [r0] if i in [0,5,9,10] else [];events.append((i,args,bytes(uc.mem_read(CELL,4)).hex()));ret=0xa5a5a5a5
   if i==0:ret=tag
   elif i==2:uc.mem_write(r0,bytes(r1))
   elif i==8:ret=caps
   elif i==11:ret=features
   if mutation==i:
    uc.mem_write(CELL,W(ALT));uc.mem_write(ALT+12,W(0x12345678));uc.mem_write(ALT+16,W(0x80000000));uc.mem_write(ALT+28,W(1));uc.mem_write(ALT+8,b'\x81\x42\x24')
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or P<=a<P+256 or ALT<=a<ALT+256:trace.append((access,a,n,v&((1<<(8*n))-1) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_gpu_reinit_4b11b0'] if isc else 0x4b11b0)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CELL,4)),bytes(u.mem_read(P,256)),bytes(u.mem_read(ALT,256))
 cases=list(itertools.product([0,0x86362000,0xffffffff],[0,1,1<<18,(1<<18)-1,1<<31,0xffffffff],[0,1,1<<9,0xffffffff],[0,165],[-1,1,2,3,8,9,10,11]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_GPU_REINIT_CHILD_CONTRACTS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':12,'limits':['Tag match/mismatch, bit18/bit9 policies, child context mutation at seven phases, ordered child calls/context access, full512contextbytes/result/SP compared.','Actual child ABIs beyond observed arguments, real initialization/driver/MMIO/full-image/hardware gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
