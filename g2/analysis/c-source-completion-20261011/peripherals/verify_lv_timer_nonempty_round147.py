from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-timer-connected-round147';D.mkdir(exist_ok=True);S=R/'components/audio/uart_thread_source_candidate/display_lv_event_init.c';V=R/'components/audio/uart_thread_source_candidate/display_font_lru_insert.c';U=R/'components/audio/uart_thread_source_candidate/display_lv_transition_schedule.c'
if '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_lv_event_init.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ROOT=0x2006f548;T=0x20001000
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';defs={'audio_uart_display_lv_root':ROOT,'audio_uart_lv_malloc':0x101011,'audio_uart_lv_tick':0x101021,'audio_uart_lvgl_log':0x101041}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_timer_create_464466',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),str(V),str(U),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()};entry=syms['audio_uart_lv_timer_create_464466']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  cuts=({0x101010:'malloc',0x101020:'tick',0x101050:'callback',0x101040:'log'} if isc else {0x44f718:'malloc',0x473482:'tick',0x101050:'callback',0x44d25c:'log'});engines.append((u,cuts,isc))
 def string(u,a):return bytes(u.mem_read(a,200)).split(b'\0',1)[0].decode('ascii')
 count=0
 for period,seed,allocated,mutation,tick,shape in itertools.product([0,1,16,0xffffffff],[0,0xa5a5a5a5,0xffffffff],[0,1],[0,1,2],[0,0xffffffff],[0,1,2]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(T,W(*[seed]*16));u.mem_write(ROOT,bytes([seed&255])*256);u.mem_write(0x20002000,bytes([seed&255])*64);u.mem_write(0x20003000,bytes([seed&255])*64);u.mem_write(ROOT+0x74,W(24,0x20002000 if shape else 0,0x20003000 if shape==2 else 0x20002000 if shape else 0));u.mem_write(ROOT+0x9c,W(0x101051 if mutation else 0,0x20008000));events=[]
   def code(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0x12345678
    if op=='malloc':events.append((op,r[0]));ret=T if allocated else 0
    elif op=='tick':
     events.append((op,bytes(uc.mem_read(T,24)).hex()));ret=tick
     if mutation==1:uc.mem_write(T+20,W(0x55))
    elif op=='callback':
     events.append((op,r[0]));
     events.append((op,bytes(uc.mem_read(T,24)).hex(),bytes(uc.mem_read(ROOT+0x80,8)).hex()))
     if mutation==2:uc.mem_write(T,W(0xabcdef01));uc.mem_write(ROOT+0x83,b'\x07')
    else:
     stack=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));events.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),*[string(uc,v) for v in stack]))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_CPSR,0x33)
   for reg,v in [(UC_ARM_REG_R0,0x12345679),(UC_ARM_REG_R1,period),(UC_ARM_REG_R2,0x20008000),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
   fault=None
   try:u.emu_start((entry if isc else 0x464466)|1,0x600000,count=1000)
   except UcError as error:fault=error.errno
   assert (fault is not None)==(not allocated)
   if allocated:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((events,fault,u.reg_read(UC_ARM_REG_R0) if allocated else None,u.reg_read(UC_ARM_REG_SP) if allocated else None,bytes(u.mem_read(T,64)),bytes(u.mem_read(ROOT,256)),bytes(u.mem_read(0x20002000,64)),bytes(u.mem_read(0x20003000,64))));u.hook_del(h)
  assert outs[0]==outs[1],(period,seed,allocated,mutation,tick,outs);count+=1
 receipt={'status':'PASS_CONNECTED_LV_TIMER_NONEMPTY_LIST_UPDATE','cases':count,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,V,U]},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual timer/listprepend/update bodies execute; malloc/tick/callback/logger controlled cuts. Timer64bytes,root256bytes,call-entry snapshots,mutations and genuineNULL assertion fault compared.','Empty/single/multiple-node list headers sampled; actual allocator/tick,rootdata/layout and hardware remainopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
