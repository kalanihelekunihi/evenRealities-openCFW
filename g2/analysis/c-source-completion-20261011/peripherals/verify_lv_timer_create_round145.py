from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-timer-create-round145';S=D/'candidate.c'
if '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_lv_event_init.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ROOT=0x2006f548;T=0x20001000
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';defs={'audio_uart_display_lv_root':ROOT,'audio_uart_lv_list_prepend_482b12':0x101011,'audio_uart_lv_tick':0x101021,'audio_uart_lv_timer_update_464696':0x101031,'audio_uart_lvgl_log':0x101041}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_timer_create_464466',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_lv_timer_create_464466')
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  cuts=({0x101010:'prepend',0x101020:'tick',0x101030:'update',0x101040:'log'} if isc else {0x482b12:'prepend',0x473482:'tick',0x464696:'update',0x44d25c:'log'});engines.append((u,cuts,isc))
 def string(u,a):return bytes(u.mem_read(a,200)).split(b'\0',1)[0].decode('ascii')
 count=0
 for period,seed,allocated,mutation,tick in itertools.product([0,1,16,0xffffffff],[0,0xa5a5a5a5,0xffffffff],[0,1],[0,1,2],[0,0xffffffff]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(T,W(*[seed]*16));u.mem_write(ROOT,bytes([seed&255])*256);events=[]
   def code(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0x12345678
    if op=='prepend':events.append((op,r[0]));ret=T if allocated else 0
    elif op=='tick':
     events.append((op,bytes(uc.mem_read(T,24)).hex()));ret=tick
     if mutation==1:uc.mem_write(T+20,W(0x55))
    elif op=='update':
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
   outs.append((events,fault,u.reg_read(UC_ARM_REG_R0) if allocated else None,u.reg_read(UC_ARM_REG_SP) if allocated else None,bytes(u.mem_read(T,64)),bytes(u.mem_read(ROOT,256))));u.hook_del(h)
  assert outs[0]==outs[1],(period,seed,allocated,mutation,tick,outs);count+=1
 receipt={'status':'PASS_LV_TIMER_CREATE_NATIVE_FIELDS_FAILURE_CALLS','cases':count,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Prepend/tick/update/logger controlled cuts; actual timer body executes. Timer64bytes,root256bytes,call-entry snapshots,mutations and genuineNULL assertion fault compared.','Fullconnected list/tick/update,rootdata/layout and hardware remainopen.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
