from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_WRITE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-vector-font-push-pair-connected-round289';S=D/'candidate.c';P=0x20001000;O=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_lv_array_push_488506','audio_uart_ambiq_vector_data_pair_53d87c','audio_uart_ambiq_vector_array_front_53d6d0','audio_uart_ambiq_vector_array_count_53d6cc','audio_uart_nema_vg_path_process_561c68','audio_uart_nema_vg_path_create_514ebc','audio_uart_lvgl_log'];native=[0x488506,0x53d87c,0x53d6d0,0x53d6cc,0x561c68,0x514ebc,0x44d25c];cuts=[0x180000+i*16 for i in range(7)];entry='audio_uart_ambiq_vector_font_push_53d8fc'
globals={'audio_uart_nema_vg_context_cell':0x20074f04,'audio_uart_ambiq_vector_current_path_200746c4':0x200746c4,'audio_uart_ambiq_vector_path_data_20073cd4':0x20073cd4,'audio_uart_ambiq_vector_path_segments_20073cc0':0x20073cc0}
if '--selected' in sys.argv:
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();assert (B/'root-ambiq-vector-font-push-round281/candidate.c').read_text() in selected;assert (B/'root-ambiq-vector-array-accessors-round282/candidate.c').read_text() in selected;assert (B/'root-nema-vg-path-shape-round286/candidate.c').read_text() in selected;assert (D/'selected-error-fixture.c').read_text() in selected;assert (B/'root-ambiq-vector-coordinate-pair-round288/candidate.c').read_text() in selected
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry]+['-Wl,--defsym='+n+'='+hex(a|1) for k,(n,a) in enumerate(zip(names,cuts)) if k not in [1,2,3]]+['-Wl,--defsym='+n+'='+hex(a) for n,a in globals.items()]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,existing,kind,result,seed,mutation,data_result,rounding):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  ranges=[(P,128),(O,128),(0x20073cc0,40),(0x200746c4,4)]
  for a,n in ranges:u.mem_write(a,bytes([seed])*n)
  u.mem_write(P,W(O if existing else 0));u.mem_write(P+4,bytes([kind]));u.mem_write(0x20074f04,W(0x20009000));u.mem_write(0x200746c4,W(0 if seed==0 else 0x20008000));events=[];trace=[];segment_address=None
  def string(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def child(u,a,n,unused):
   nonlocal segment_address
   addresses=cuts if isc else native
   if a not in addresses:return
   k=addresses.index(a)
   if k in [1,2,3]:return
   regs=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
   if k==0:
    if regs[0]==0x20073cc0:
     segment_address=regs[1];events.append([k,regs[0],u.mem_read(segment_address,1)[0]]);ret=result
    else:
     assert regs[0]==0x20073cd4;events.append([k,regs[0],bytes(u.mem_read(regs[1],4)).hex()]);ret=data_result
   elif k==1:events.append([k,regs[0],regs[1]])
   elif k==2:events.append([k,regs[0]]);ret=0x20003000+len(events)*16
   elif k==3:events.append([k,regs[0]]);ret=0xffffffff-len(events)
   elif k==4:events.append([k,regs[0],bytes(u.mem_read(regs[0],16)).hex()])
   elif k==5:events.append([k]);ret=0 if seed==0xff else 0x20007000
   else:
    words=3 if regs[2]==209 else 2;stack=struct.unpack('<'+'I'*words,u.mem_read(u.reg_read(UC_ARM_REG_SP),4*words));extra=[string(v) for v in stack] if regs[2]!=235 else [string(stack[0]),stack[1]];events.append([k,regs[0],string(regs[1]),regs[2],string(regs[3])]+extra)
   if mutation and k<6:
    for i in range(2,8):u.mem_write(P+i*4,W(seed+i*100+len(events)*mutation))
    u.mem_write(O+4,W(0x20006000+len(events)*16));u.mem_write(0x200746c4,W(0x20005000+len(events)*32));u.mem_write(P+4,bytes([(kind+len(events))&255]))
    if segment_address:u.mem_write(segment_address,bytes([6 if mutation==1 else (5 if len(events)%2 else 0)]))
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def mem(u,access,a,n,value,unused):
   if any(x<=a<x+z for x,z in ranges):trace.append(['w' if access==UC_MEM_WRITE else 'r',a,n,(value if access==UC_MEM_WRITE else int.from_bytes(u.mem_read(a,n),'little'))&((1<<(8*n))-1)])
  u.hook_add(UC_HOOK_CODE,child);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_FPSCR,rounding<<22);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym[entry] if isc else 0x53d8fc)|1,0x600000,count=4000)
  except UcError as e:assert e.errno==UC_ERR_WRITE_UNMAPPED;fault='unmapped_fail_stop_store'
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  assert bool(fault)==(not existing or result&255!=1 or (data_result&255!=1 and any(e[0]==0 and e[1]==0x20073cd4 for e in events)))
  return events,trace,[bytes(u.mem_read(a,n)).hex() for a,n in ranges]+[bytes(u.mem_read(0x20005000,0x3100)).hex(),bytes(u.mem_read(0x20009000,256)).hex()],None if fault else u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_FPSCR),fault
 count=0
 for c in itertools.product([0,1],[0,1,2,3,4,5,6,255],[0,1,257],[0,0xff],[0,1,2],[0,1,257],range(4)):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_OUTLINE_COMMANDS_REAL_PAIR_ACCESSORS_SHAPE','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':4,'limits':['Full outline command mapping, unknown diagnostics, lowbyte gate, cached type/outline, postchild segment and field reloads, ordered accesses/fullguards/returningSP match with child mutations. NULL outline and failed append diagnostics/unmapped fail-stop existence match. Four append/postprocessor/pathcreate/logger cuts remain; actual pair/item/front/count/shape/error execute; path/VG memory guards andfinalFPSCR compared acrossfourroundingmodes withcoordinateappend failure gates. State lifecycle/placement/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
