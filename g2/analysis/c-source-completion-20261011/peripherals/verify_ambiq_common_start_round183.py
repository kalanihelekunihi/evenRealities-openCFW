from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-common-start-round183';S=D/'candidate.c';BF=0x20001000;U=0x20002000;RAW=0x20003000;W=lambda *v:struct.pack('<'+'I'*len(v),*[x&0xffffffff for x in v])
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_ambiq_default_unit_4c791a','audio_uart_lv_memzero_48949c','audio_uart_lv_area_intersect_450bcc','audio_uart_ambiq_color_format_dst_4b064e','audio_uart_ambiq_context_lock_4b07de','audio_uart_nema_power_control_51419a','audio_uart_nema_cl_get_bound_5144fa','audio_uart_nema_cl_rewind_514384','audio_uart_nema_cl_bind_sectored_5143d4','audio_uart_nema_last_cl_id_51418e','audio_uart_nema_last_submission_id_514194','audio_uart_lv_basic_box_clear_454746','audio_uart_ambiq_blend_clear_4b075e','audio_uart_ambiq_context_unlock_4b0886','audio_uart_nema_bind_tex_4b1298','audio_uart_checksum_copy','audio_uart_ambiq_clip_change_4b077e','audio_uart_lvgl_log'];native=[0x4c791a,0x48949c,0x450bcc,0x4b064e,0x4b07de,0x51419a,0x5144fa,0x514384,0x5143d4,0x51418e,0x514194,0x454746,0x4b075e,0x4b0886,0x4b1298,0x439c04,0x4b077e,0x44d25c]
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4b092a..4b0b5a;');z=selected.index('#include <stdint.h>',a);fixture=Path(t)/'selected.c';fixture.write_text(S.read_text().split('/* Native4b092a')[0]+selected[a:z]);S=fixture
 e=Path(t)/'test.elf';cuts=[0x101010+i*16 for i in range(len(names))];subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_bind_buffer_4b092a']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,cf,extend,mapped,clipmode,power,bound,lastcl,lastsub,cached,mutation,field,raw):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(U,bytes([165])*256);u.mem_write(BF,bytes([90])*128);u.mem_write(RAW,W(1,2,3,4));u.mem_write(BF,W(0x12340019|(cf<<8),(5<<16)|4,16,1024,0x20008000,0x20008000,0x20009000))
  if field==1:u.mem_write(BF+16,W(0))
  if field==2:u.mem_write(BF+4,W(5<<16))
  if field==3:u.mem_write(BF+4,W(4))
  if cached:u.mem_write(U+88,bytes(u.mem_read(BF,28)))
  events=[];trace=[];fault=[]
  def area(a):return struct.unpack('<4I',u.mem_read(a,16))
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0xabcdef01
   if i==0:events.append((i,));ret=U
   elif i==1:events.append((i,r[1]));uc.mem_write(r[0],bytes(r[1]))
   elif i==2:
    events.append((i,area(r[1]),area(r[2]),r[1]==r[2]));values=[(1,2,3,4),(1,2,1,4),(1,2,3,2),(0x80000000,0,0x7fffffff,2),(0xffffffff,0,1,2)][max(0,clipmode-1)];uc.mem_write(r[0],W(*values));ret=0 if clipmode==0 else 1
   elif i==3:
    events.append((i,r[0]));ret=mapped
    if mutation==1:uc.mem_write(BF,W(0x1400));uc.mem_write(BF+16,W(0xfffffffc))
   elif i==5:
    events.append((i,r[0],r[1]));ret=power
    if mutation==2:uc.mem_write(BF+4,W((7<<16)|9));uc.mem_write(BF+16,W(0x2000b000))
   elif i==6:events.append((i,));ret=[0,U+144,0x2000a000][bound]
   elif i in [9,10]:events.append((i,));ret=lastcl if i==9 else lastsub
   elif i==11:events.append((i,*r[:3]));uc.mem_write(r[0],bytes([r[1]&255])*r[2])
   elif i==14:
    stk=struct.unpack('<3I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));events.append((i,*r,stk))
    if mutation==3:uc.mem_write(BF,W(0x1000,0x12345678,99,42,0x2000c000,0,0))
   elif i==15:events.append((i,*r[:3],bytes(uc.mem_read(r[1],r[2])).hex()));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])))
   elif i==16:events.append((i,r[0],area(r[1]),r[2]))
   elif i==17:
    sp=uc.reg_read(UC_ARM_REG_SP);fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];arg=struct.unpack('<I',uc.mem_read(sp+4,4))[0] if r[2]==385 else None;events.append(('log',r[0],string(r[1]),r[2],string(r[3]),string(fmt),arg))
   elif i==8:events.append((i,r[0],r[1]))
   else:events.append((i,r[0]))
   uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if BF<=a<BF+128 or U<=a<U+256:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  def bad(uc,access,a,n,v,user):fault.append((a,n));return False
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_MEM_READ_UNMAPPED,bad);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0 if field==4 else BF);u.reg_write(UC_ARM_REG_R1,RAW if raw else 0);u.reg_write(UC_ARM_REG_R2,extend);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  try:u.emu_start((sym['audio_uart_ambiq_bind_buffer_4b092a'] if isc else 0x4b092a)|1,0x600000,count=3000)
  except UcError:assert fault==[(4,4)],fault
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,fault,None if fault else u.reg_read(UC_ARM_REG_R0),None if fault else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(BF,128)),bytes(u.mem_read(U,256))
 cases=[(cf,ext,mapped,1,0,0,0,0,cached,0,0,1) for cf,ext,mapped,cached in itertools.product(range(256),[0,1,257],[-1,9],[0,1])]
 cases +=[(16,1,9,clip,power,bound,lastcl,lastsub,1,mut,field,raw) for clip,power,bound,lastcl,lastsub,mut,field,raw in itertools.product(range(6),[0,1],[0,1,2],[-1,0],[0,1],range(4),range(5),[0,1])]
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_AMBIQ_COMMON_START_CONTROLLED_CHILDREN','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['18childcuts; allcolorbytes/extendedformat/fallback/cache branches, clipping/wrapped rejection, rawNULL/bufferNULL earlyfault,invalidfields,power/bound/reset/childmutation,orderedinput accesses/full384bytes/return/SP compared.','Real intersect/map/context/Nema/buffer children and hardware/fullimage unqualified.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
