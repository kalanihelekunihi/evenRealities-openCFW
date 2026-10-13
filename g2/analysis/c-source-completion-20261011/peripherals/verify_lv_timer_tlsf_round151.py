from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-timer-tlsf-round151';D.mkdir(exist_ok=True)
paths=['file_pool_allocate_candidate/pool_allocate.c','tlsf_adjust_request_candidate/adjust.c','tlsf_locate_free_candidate/locate.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_free_lists.c','tlsf_prepare_allocation_candidate/prepare.c','tlsf_split_block_candidate/split.c','file_pool_free_candidate/tlsf_block_next.c','file_pool_free_candidate/tlsf_mark_free.c','file_pool_free_candidate/tlsf_lists.c','file_pool_free_candidate/tlsf_align.c','file_pool_free_candidate/tlsf_leaf.c']
S=[R/'components/audio'/p for p in paths]+[R/'components/audio/uart_thread_source_candidate'/p for p in ['display_font_alloc.c','tlsf_reallocate.c','display_lv_event_init.c','display_font_lru_insert.c','display_lv_transition_schedule.c','display_timer_children.c']]
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
W=lambda *v:struct.pack('<'+'I'*len(v),*v);ROOT=0x2006f548;POOL=0x20000338;ARENA=0x20010000;TICK=0x2006f600
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);shim=t/'shim.c';shim.write_text('void g2_file_close_error(const char*a,const char*b,unsigned c){} void audio_ble_hci_boot_log_4733ee(const char*p,...){}');e=t/'test.elf'
 defs={'audio_uart_display_lv_root':ROOT,'audio_uart_lv_heap_pool':POOL,'audio_uart_lv_static_slot':0x2006f5ac,'xQueueSemaphoreTake':0x101071,'audio_uart_queue_send':0x101081,'audio_uart_lv_tick_state':TICK,'audio_uart_lvgl_log':0x101041}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_timer_create_464466','-Wl,-u,g2_tlsf_create_with_pool_4d06ec',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,size,count,seed,take):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(ARENA,bytes([seed])*16384);u.mem_write(0x78f4b4,W(1,2,4,8,12,0x40000000));events=[]
  cuts=({0x101070:'take',0x101080:'send',0x101040:'log'} if isc else {0x441c44:'take',0x4417ee:'send',0x44d25c:'log'})
  cuts.update({(sym[s] if isc else a)&~1:op for s,a,op in [('audio_ble_hci_boot_log_4733ee',0x4733ee,'tlsf_log'),('g2_file_close_error',0x4d09b4,'error')]})
  def string(a):return bytes(u.mem_read(a,220)).split(b'\0',1)[0].decode('ascii')
  def hook(uc,a,n,user):
   if a not in cuts:return
   op=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=1
   if op=='take':events.append((op,*r[:2]));ret=take
   elif op=='send':events.append((op,*r))
   elif op=='log':
    stack=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));events.append((op,r[0],string(r[1]),r[2],string(r[3]),*[string(v) for v in stack]))
   else:events.append((op,*r[:3]))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  def call(name,native,args):
   u.reg_write(UC_ARM_REG_CPSR,0x33)
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
   try:u.emu_start((sym[name] if isc else native)|1,0x600000,count=100000)
   except UcError as ex:fault=ex.errno
   if fault is None:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   return fault,u.reg_read(UC_ARM_REG_R0) if fault is None else None,u.reg_read(UC_ARM_REG_SP) if fault is None else None
  init=call('g2_tlsf_create_with_pool_4d06ec',0x4d06ec,[ARENA,size]);assert init[0] is None
  u.mem_write(POOL,W(0x20009000,init[1],0,0));u.mem_write(ROOT,bytes(256));u.mem_write(ROOT+0x74,W(24,0,0));u.mem_write(TICK,W(0xffffffff,0,0,0));results=[]
  for i in range(count):
   result=call('audio_uart_lv_timer_create_464466',0x464466,[0x12345679,(i*17)&0xffffffff,0x20008000+i*4]);results.append(result)
   if result[0] is not None:break
  return init,results,events,bytes(u.mem_read(ARENA,16384)),bytes(u.mem_read(ROOT,256)),bytes(u.mem_read(POOL,16)),bytes(u.mem_read(TICK,16))
 count=0;faults=0
 for size,n,seed,take in itertools.product([3212,3248,4096,8192],[1,2,8],[0,0xa5],[0,1]):
  a=run(False,size,n,seed,take);b=run(True,size,n,seed,take);assert a==b,(size,n,seed,take,a,b);count+=1;faults+=a[1][-1][0] is not None
 receipt={'status':'PASS_CONNECTED_TIMER_ACTUAL_TLSF_ALLOCATION','cases':count,'fault_cases':faults,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual TLSF construction,allocation,split/free-list effects and LV heap/list/timer/tick/update execute; full16384 arena plus root/pool/tick bytes and return/SP compared.','Mutex and logger controlled cuts; no callback in this fixture. Full image data/layout,physical scheduling and hardware gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
