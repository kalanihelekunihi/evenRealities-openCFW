from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-vector-font-allocate-arrays-connected-round280';S=D/'candidate.c';P=0x20001000;O=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_lv_malloc','audio_uart_nema_vg_path_create_514ebc','audio_uart_lv_array_clear_488478','audio_uart_lv_array_init_external_488440','audio_uart_lvgl_log','audio_uart_lv_heap_free'];native=[0x44f718,0x514ebc,0x488478,0x488440,0x44d25c,0x44f758];cuts=[0x180000+i*16 for i in range(6)];entry='audio_uart_ambiq_vector_font_allocate_53da54'
globals={'audio_uart_ambiq_vector_current_path_200746c4':0x200746c4,'audio_uart_ambiq_vector_path_data_20073cd4':0x20073cd4,'audio_uart_ambiq_vector_path_segments_20073cc0':0x20073cc0}
if '--selected' in sys.argv:
 assert (D/'selected-array-clear-fixture.c').read_text().strip() in (R/'components/audio/uart_thread_source_candidate/display_lv_event_compact.c').read_text()
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert (B/'root-ambiq-vector-font-allocate-round277/candidate.c').read_text() in selected;assert (B/'root-lv-array-external-init-round278/candidate.c').read_text() in selected
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for k,(n,a) in enumerate(zip(names,cuts)) if k not in [2,3]]+['-Wl,--defsym='+n+'='+hex(a) for n,a in globals.items()]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,existing,fail,size,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  ranges=[(P,128),(O,128),(0x20073cc0,40),(0x200746c4,4)]
  for a,n in ranges:u.mem_write(a,bytes([seed])*n)
  u.mem_write(P,W(O if existing else 0));u.mem_write(P+32,W(size)+W(size^0x80000000));events=[];trace=[];allocations=0
  def string(a):
   data=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return data.decode()
    data.append(c);assert len(data)<300
  def child(u,a,n,unused):
   nonlocal allocations
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a)
   if k in [2,3]:return
   regs=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0
   if k==0:
    allocations+=1;events.append([k,regs[0]]);result=0 if allocations==fail else (O if allocations==1 and not existing else 0x20003000+allocations*256)
   elif k==1:events.append([k]);result=0 if seed==0xff else 0x20005000
   elif k==2:events.append([k,regs[0]])
   elif k==3:events.append([k]+regs)
   elif k==5:events.append([k,regs[0]])
   else:
    stack=struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12));events.append([k,regs[0],string(regs[1]),regs[2],string(regs[3])]+[string(v) for v in stack])
   if mutation and k in [0,1,5]:
    u.mem_write(P+32,W(size+len(events)*mutation)+W((size^0x80000000)-len(events)*mutation));u.mem_write(O,W(0x20006000+len(events)*16))
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,n,value,unused):
   if any(x<=a<x+z for x,z in ranges):trace.append(['w' if access==UC_MEM_WRITE else 'r',a,n,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,n),'little'))&((1<<(8*n))-1)])
  u.hook_add(UC_HOOK_CODE,child);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym[entry] if isc else 0x53da54)|1,0x600000,count=4000)
  except UcError as err:assert err.errno==UC_ERR_WRITE_UNMAPPED;fault='unmapped_fail_stop_store'
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  assert bool(fault)==(0<fail<=(2 if existing else 3))
  return events,trace,[bytes(u.mem_read(a,n)).hex() for a,n in ranges],None if fault else u.reg_read(UC_ARM_REG_SP),fault
 count=0
 for c in itertools.product([0,1],range(4),[0,1,0x3fffffff,0x80000000,0xffffffff],[0,0x5a,0xff],[0,1,7]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_VECTOR_FONT_ALLOCATION_REAL_ARRAYS','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':4,'limits':['Full allocation control, wrapped dimensions, child args/logs, watched ordered accesses/fullguards and returningSP match with child mutations; all reachable allocation failures hit diagnostic/unmapped fail-stop store. Real malloc/path-create/heap-free/logger providers, state ownership/init/placement, fault instruction/bus/FPU/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
