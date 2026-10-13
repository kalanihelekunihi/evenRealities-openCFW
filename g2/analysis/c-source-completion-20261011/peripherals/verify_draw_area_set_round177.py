from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-draw-area-set-round177';S=B/'root-draw-cache-round176/candidate.c';P=0x20001000;H=0x20002000;ALT=0x20003000;AREA=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native48ab30..48abb8.');fixture=Path(t)/'selected.c';z=selected.index('#include <stdint.h>',a);fixture.write_text(S.read_text().split('/* Native48ab30')[0]+selected[a:z]);S=fixture
  a=selected.index('/* Native450b5c..450b6c;');af=Path(t)/'selected-area-set.c';af.write_text('#include <stdint.h>\n'+selected[a:]);AS=af
 else:AS=D/'candidate.c'
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_draw_invalidate_cache_48ab30','-Wl,--defsym=audio_uart_lvgl_log=0x101011',str(S),str(AS),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,kind,hasbuf,hashandler,hasarea,hascallback,mutation,header,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for a in [P,H,ALT,AREA]:u.mem_write(a,bytes([seed])*128)
  u.mem_write(P+4,W(header));u.mem_write(P+24,W(H if hashandler else 0));u.mem_write(H+12,W(0x101041 if hascallback else 0,0x101041 if hascallback else 0));u.mem_write(AREA,W(3,5,7,11));events=[];trace=[];fault=[]
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
   if a==(0x101010 if isc else 0x44d25c):
    stk=struct.unpack('<3I',uc.mem_read(sp,12));events.append(('log',r[0],string(r[1]),r[2],string(r[3]),*[string(x) for x in stk]))
   elif a==((sym['audio_uart_lv_area_set_450b5c']&~1) if isc else 0x450b5c):
    y2=struct.unpack('<I',uc.mem_read(sp,4))[0];events.append(('set',r[1],r[2],r[3],y2))
    if mutation:uc.mem_write(P+24,W(ALT));uc.mem_write(H+12,W(0x101051,0x101051))
    return
   elif a in [0x101040,0x101050]:events.append(('callback',a,r[0],bytes(uc.mem_read(r[1],16)).hex(),r[1]==AREA))
   else:return
   uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if any(x<=a<x+128 for x in [P,H,ALT,AREA]):trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  def bad(uc,access,a,n,v,user):fault.append((a,n,v));return False
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,P if hasbuf else 0);u.reg_write(UC_ARM_REG_R1,AREA if hasarea else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  name=['audio_uart_lv_draw_invalidate_cache_48ab30','audio_uart_lv_draw_flush_cache_48abb8'][kind];entry=sym[name] if isc else [0x48ab30,0x48abb8][kind]
  try:u.emu_start(entry|1,0x600000,count=3000)
  except UcError:
   assert fault==[(0xffffffff,4,0)],fault
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,fault,None if fault else u.reg_read(UC_ARM_REG_SP),tuple(bytes(u.mem_read(a,128)) for a in [P,H,ALT,AREA])
 cases=list(itertools.product(range(2),[0,1],[0,1],[0,1],[0,1],[0,1],[0,1,0xffff0000,0x1234ffff],[0,165]))
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_CONNECTED_CACHE_WRAPPERS_REAL_FULL_AREA_AND_SET','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Actual full-area/area-set bodies; logger/callback cuts. Area-set entry hook observes and mutates handler metadata without replacing execution. NULL assertions log/full fault, saved handlers/fresh callback mutation, width/height zero wraps, ordered input accesses, four128byte regions and valid-return SP compared. Void scratchR0 ignored.','Physical cache coherency and full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
