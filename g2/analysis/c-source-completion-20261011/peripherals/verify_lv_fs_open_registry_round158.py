from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-fs-open-round158';D.mkdir(exist_ok=True);S=B/'root-lv-fs-open-round157/candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);F=0x20001000;DR=0x20002000;CACHE=0x20003000;PATH=0x20004000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();prefix=S.read_text().split('/* Native4c6d9a')[0];fixture=Path(t)/'selected-open.c';fixture.write_text(prefix+selected[selected.index('/* Native4c6d9a'):]);S=fixture
 defs={'audio_uart_display_lv_root':0x2006f548,'audio_uart_lv_heap_alloc':0x101021,'audio_uart_lvgl_log':0x101031}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_fs_file_open_4c6d9a',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),str(R/'components/audio/uart_thread_source_candidate/display_lv_fs_registry_bind.c'),str(R/'components/audio/uart_thread_source_candidate/display_timer_children.c'),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,pathbytes,found,ready,opened,cachesize,allocated,mode,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(F,W(*[0xa5a5a5a5]*16));u.mem_write(CACHE,W(*[0xa5a5a5a5]*8));u.mem_write(DR,W(0x4c,cachesize,0 if ready==2 else 0x101041,0 if opened==2 else 0x101051));u.mem_write(PATH,(pathbytes or b'')+bytes(64));u.mem_write(0x2006f6c8,W(4,0x20006000,0x20006100 if found else 0x20006000));u.mem_write(0x20006000,W(0x20006200,0,0x20006100 if found else 0));u.mem_write(0x20006100,W(DR,0x20006000,0));u.mem_write(0x20006200,W(0x58));events=[]
  cuts=({0x101010:'find',0x101020:'alloc',0x101030:'log'} if isc else {0x4c70b4:'find',0x44f730:'alloc',0x44d25c:'log'});cuts.update({0x101040:'ready',0x101050:'open'})
  def string(a):return bytes(u.mem_read(a,220)).split(b'\0',1)[0].decode('ascii')
  cuts={a:op for a,op in cuts.items() if op!='find'}
  def hook(uc,a,n,user):
   if a not in cuts:return
   op=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
   if op=='find':events.append((op,r[0]));ret=DR if found else 0
   elif op=='ready':
    events.append((op,r[0]));ret=ready
    if mutation==1:uc.mem_write(DR+4,W(0xffffffff))
   elif op=='open':events.append((op,r[0],string(r[1]),r[2],bytes(uc.mem_read(F,12)).hex()));ret=opened
   elif op=='alloc':
    events.append((op,r[0]));ret=CACHE if allocated else 0
    if mutation==2:uc.mem_write(DR+4,W(0xffffffff))
   else:
    sp=uc.reg_read(UC_ARM_REG_SP);fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];event=[op,r[0],string(r[1]),r[2],string(r[3]),string(fmt)]
    if r[2] in [88,94,100]:event.append(string(struct.unpack('<I',uc.mem_read(sp+4,4))[0]))
    if r[2]==123:event.extend(string(v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
    events.append(tuple(event))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in [(UC_ARM_REG_R0,F),(UC_ARM_REG_R1,PATH if pathbytes is not None else 0),(UC_ARM_REG_R2,mode),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
  fault=None
  try:u.emu_start((sym['audio_uart_lv_fs_file_open_4c6d9a'] if isc else 0x4c6d9a)|1,0x600000,count=1000)
  except UcError as ex:fault=ex.errno
  if fault is None:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,fault,u.reg_read(UC_ARM_REG_R0) if fault is None else None,u.reg_read(UC_ARM_REG_SP) if fault is None else None,bytes(u.mem_read(F,64)),bytes(u.mem_read(CACHE,32)),bytes(u.mem_read(DR,16))
 count=0
 for pathbytes,found,ready,opened,cachesize,allocated,mode,mutation in itertools.product([None,b'',b'L:file.bmp',b'Lfile.bmp'],[0,1],[0,1,2],[0,0x20008000,0xffffffff,2],[0,16,0xffffffff],[0,1],[2,0x12345678],[0,1,2]):
  a=run(False,pathbytes,found,ready,opened,cachesize,allocated,mode,mutation);b=run(True,pathbytes,found,ready,opened,cachesize,allocated,mode,mutation);assert a==b,(pathbytes,found,ready,opened,cachesize,allocated,mode,mutation,a,b);count+=1
 receipt={'status':'PASS_CONNECTED_LV_FS_OPEN_DRIVER_REGISTRY','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual driver registry/list-first/list-next execute; ready/open/heap/log controlled cuts; null/empty/colon paths,error codes,mode byte,driver/cache mutations,memory-backed cache fields,orderedcalls and file/cache/driver bytes compared.','Native NULLcache assertion fault and return/SP compared. Real driver operations and connected decoder/filesystem/fullimage gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
