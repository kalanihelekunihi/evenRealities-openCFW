from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-array-append-wrappers-connected-round285';S=D/'candidate.c';P=0x20001000;O=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_lv_array_resize_48849c','audio_queue_copy_bytes','audio_uart_buffer_zero','audio_uart_lvgl_log'];native=[0x48849c,0x439be4,0x43c0e4,0x44d25c];cuts=[0x180000+i*16 for i in range(4)];entry='audio_uart_lv_array_push_488506'
if '--selected' in sys.argv:
 assert (B/'root-lv-array-append-round284/candidate.c').read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert (D/'selected-copy-wrapper.c').read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_grid_copy.c').read_text();assert (D/'selected-fill-wrapper.c').read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_theme_basic_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,data,source,fields,stride,result,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,bytes_ in segs:u.mem_write(a,bytes_)
  u.mem_write(P,bytes([seed])*128);u.mem_write(P,struct.pack('<IIII',O if data else 0,fields[0],fields[1],stride));events=[];trace=[]
  def string(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def child(u,a,n,unused):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a);regs=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
   if k==0:events.append([k,regs[0],regs[1]]);ret=result
   elif k in [1,2]:events.append([k]+regs[:3]);assert k!=2 or regs[2]==0
   else:
    stack=struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12));events.append([k,regs[0],string(regs[1]),regs[2],string(regs[3])]+[string(v) for v in stack])
   if mutation and k<3:u.mem_write(P,struct.pack('<IIII',0xfffffff0 if mutation==2 else O+64,fields[0]+len(events)*mutation&0xffffffff,fields[1],stride+mutation&0xffffffff))
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,n,value,unused):
   if P<=a<P+128:trace.append(['w' if access==UC_MEM_WRITE else 'r',a,n,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,n),'little'))&((1<<(8*n))-1)])
  u.hook_add(UC_HOOK_CODE,child);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,O+128 if source else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym[entry] if isc else 0x488506)|1,0x600000,count=4000)
  except UcError as e:assert e.errno==UC_ERR_WRITE_UNMAPPED;fault='unmapped_fail_stop_store'
  assert bool(fault)==(not data)
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000;assert u.reg_read(UC_ARM_REG_R0)==(0 if fields[0]==fields[1] and result==0 else 1)
  return events,trace,bytes(u.mem_read(P,128)).hex(),None if fault else u.reg_read(UC_ARM_REG_SP),None if fault else u.reg_read(UC_ARM_REG_R0),fault
 count=0
 for c in itertools.product([0,1],[0,1],[(0,0),(0,1),(1,0),(1,1),(0xffffffff,0xffffffff)],[0,1,4,0xffffffff],[0,1,256],[0,0xff],[0,1,2]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_ARRAY_APPEND_REAL_COPY_FILL_WRAPPERS','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':4,'limits':['Full append and consumed-void zero wrapper, equality-only capacity gate/full32 resize result, wrapped destination, fresh field/count reloads, controlled copy/fill/resize args, ordered descriptor accesses/fullguard/returningR0/SP and NULL-data log/fail-stop existence match with child mutations. Actual copy/fill wrappers execute; resize/lowercopy/lowerfill/logger remain controlled. Destination memory/lifecycle/placement/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
