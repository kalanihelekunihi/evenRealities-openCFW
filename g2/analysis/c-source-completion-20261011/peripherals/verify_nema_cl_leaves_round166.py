from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-cl-leaves-round166';S=B/'root-nema-cl-destroy-round165/candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);A=0x20001000;N=0x20002000;C=0x20003000;ALT=0x20003100;CELL=0x20074efc
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';leaf=D/'candidate.c'
 if '--selected-leaves' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native514050');prefix=leaf.read_text().split('/* Native514050')[0];fixture=Path(t)/'selected-leaves.c';fixture.write_text(prefix+selected[a:]);leaf=fixture
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native5142f0');prefix=S.read_text().split('/* Native5142f0')[0];fixture=Path(t)/'selected.c';fixture.write_text(prefix+selected[a:]);S=fixture
 defs={'audio_uart_nema_context_cell':CELL,'audio_uart_lv_pool_free_48429e':0x101011}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_cl_destroy_5142f0',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),str(leaf),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 regions=[(A,64),(N,64),(C,48),(ALT,48),(CELL,4),(0x20004000,32),(0x20005000,32)]
 def run(isc,entry,flags,active,size,offset,mutation,pool_id):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(A,W(0,pool_id,0x20004000,0,size,offset,flags,0,N,0,*[0]*6));u.mem_write(N,W(0,pool_id,0x20005000,0,size,offset,flags,0,0,A,*[0]*6));u.mem_write(C,W(0,active,*[0]*10));u.mem_write(ALT,W(0,N,*[0]*10));u.mem_write(CELL,W(C))
  for a in [0x20004000,0x20005000]:u.mem_write(a,bytes([0xa5])*32)
  events=[];cuts={0x101010 if isc else 0x48429e:'poolfree'}
  def snap():return [bytes(u.mem_read(a,n)).hex() for a,n in regions]
  def hook(uc,a,n,user):
   if a not in cuts:return
   kind=cuts[a];pool=uc.reg_read(UC_ARM_REG_R0);arg=uc.reg_read(UC_ARM_REG_R1);events.append((kind,pool,arg,snap()))
   owner=A if arg==0x20004000 else N if arg==0x20005000 else 0
   if owner and mutation==1:uc.mem_write(owner+36,W(0))
   if mutation==2:uc.mem_write(CELL,W(ALT))
   if arg in [A,N]:uc.mem_write(arg+32,W(0xdeadbeef))
   uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,entry);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sym['audio_uart_nema_cl_destroy_5142f0'] if isc else 0x5142f0)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_SP),snap()
 count=0
 for entry,flags,active,size,offset,mutation,pool_id in itertools.product([0,A,N],[0,8,16,32,56],[0,A,N],[0,1,2,0x80000000],[0,1],[0,1,2],[0,1,2,3,0xffffffff]):
  a=run(False,entry,flags,active,size,offset,mutation,pool_id);b=run(True,entry,flags,active,size,offset,mutation,pool_id);assert a==b,(entry,flags,active,size,offset,mutation,a,b);count+=1
 receipt={'status':'PASS_CONNECTED_NEMA_CL_DESTROY_REAL_LEAVES','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual pool selector/buffer destroy/node release/error setter execute; poolfree controlled cut; null entry,root redirect/two-node chains,shared flags,activecontext,size/offset signed test,commandwords andchild context/root/next mutations compared.','Seven data regions including48bytespercontext plus call snapshots/SP compared; malformed cyclic lists,physicalGPU buffers andfullimage gates remainopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
