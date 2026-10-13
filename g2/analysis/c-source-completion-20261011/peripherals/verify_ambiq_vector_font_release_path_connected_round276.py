from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-vector-font-release-path-connected-round276';S=D/'candidate.c';P=0x20001000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_ambiq_get_path_buffers_5fa21c','audio_uart_nema_vg_path_destroy_514d98','audio_uart_lv_heap_free','audio_uart_lvgl_log','audio_uart_lv_pool_free_48429e'];native=[0x5fa21c,0x514d98,0x44f758,0x44d25c,0x48429e];cuts=[0x180000+i*16 for i in range(5)];entry='audio_uart_ambiq_vector_font_release_53db3c'
if '--selected' in sys.argv:
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert (B/'root-ambiq-vector-font-release-round272/candidate.c').read_text() in selected;assert (B/'root-ambiq-path-buffer-getter-round273/candidate.c').read_text() in selected;assert (B/'root-nema-vg-path-destroy-round275/candidate.c').read_text() in selected
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names[2:],cuts[2:])]+['-Wl,--defsym=audio_uart_nema_vg_context_cell=0x20074f04',str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,pointer,path,border,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x20002000,bytes((seed+i*13)&255 for i in range(0x5000)));u.mem_write(P,bytes([seed])*128);u.mem_write(P,W(0x20002000 if path else 0)+W(0x20003000 if border else 0));events=[];accesses=[]
  def readstr(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def hook(u,a,size,unused):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a)
   if k in [0,1]:return
   r=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP)
   if k==0:
    fifth=int.from_bytes(u.mem_read(sp,4),'little');outs=[r[1],r[2],r[3],fifth];assert len(set(outs))==4 and all(v%4==0 for v in outs);events.append([k,r[0],'segsize','datasize','segptr','dataptr'])
    for v,w in zip(outs,[11,22,0x20007000+r[0]%256,0x20008000+r[0]%256]):u.mem_write(v,W(w))
   elif k in [1,2]:events.append([k,r[0]])
   elif k==4:events.append([k,r[0],r[1]]);assert r[0]==0x20000338
   else:
    extra=struct.unpack('<III',u.mem_read(sp,12));events.append([k,r[0],readstr(r[1]),r[2],readstr(r[3])]+[readstr(v) for v in extra])
   if pointer and mutation and k<3:
    n=len(events);u.mem_write(P,W(0 if mutation==1 else 0x20004000+n*16));u.mem_write(P+4,W(0 if mutation==1 else 0x20005000+n*16))
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,size,value,unused):
   if P<=a<P+128:accesses.append(['w' if access==UC_MEM_WRITE else 'r',a,size,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,size),'little'))&((1<<(size*8))-1)])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.mem_write(0x20074f04,W(0x20009000));u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if pointer else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym[entry] if isc else 0x53db3c)|1,0x600000,count=4000)
  except UcError as err:assert not pointer and err.errno==UC_ERR_WRITE_UNMAPPED;fault='native_unmapped_fail_stop_store'
  if pointer:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  else:assert fault
  return events,accesses,bytes(u.mem_read(P,128)).hex(),bytes(u.mem_read(0x20002000,0x5000)).hex(),u.reg_read(UC_ARM_REG_SP) if pointer else None,fault
 count=0
 for c in itertools.product([0,1],[0,1],[0,1],[0,0x5a,0xff],[0,1,2]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_VECTOR_FONT_RELEASE_REAL_GETTER_PATH_DESTROY','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':3,'limits':['Full release body,watched ordered glyph accesses/128byteguard/childargs/log contents/SP on returning cases match with child mutations. Native NULLdiagnostic/unmapped fail-stop store existence matches; exact fault instruction/physical bus not claimed. Real heap/pool free/logger,ownership/pointerfault/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
