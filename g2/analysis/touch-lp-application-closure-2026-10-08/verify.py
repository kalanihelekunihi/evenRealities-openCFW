from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-isr-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for start,count,enable,iir,irq')[0],ns);g=ns['g'];rows=[]
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
with Path(sys.argv[1]).open('rb') as f:
 elf=ELFFile(f);sym={x.name:x for x in elf.get_section_by_name('.symtab').iter_symbols()};app=sym['touch_app_lp_phase'];app_start=app['st_value']&~1;app_end=app_start+app['st_size'];deep=g['symbols']['Cy_SysPm_CpuEnterDeepSleep']&~1;low=g['symbols']['Cy_SysPm_CpuEnterDeepSleepNoCallbacks']&~1;section=elf.get_section_by_name('.text');blob=section.data();base=section['sh_addr'];cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);native_wfi=next(i.address for i in cs.disasm(blob[low-base:low-base+sym['Cy_SysPm_CpuEnterDeepSleepNoCallbacks']['st_size']],low) if i.mnemonic=='wfi')

def fixture(old,busy,ready,mask):
 u=g['guest']();u.mem_write(0x20000400,g['fw'][32:32+0xc0]);u.mem_write(0x200004c0,g['fw'][32+0xb58c-0x3300:32+0xb58c-0x3300+964]);u.mem_write(0x200008a8,b'\0'*1712);u.mem_map(0x40000000,0x400000);u.mem_map(0x0fff0000,0x10000);u.mem_map(0xe000e000,0x1000);u.mem_write(0x0fff0000,bytes(range(256))*256);u.mem_write(0x20000870,b'\x01');g['call'](u,g['symbols']['touch_cap_init_fields'],[0x200004ec]);assert g['call'](u,g['symbols']['touch_prepare_scan_fields'],[0x200004ec])==0;u.mem_write(0x20000c50+85,bytes([old]));u.mem_write(0x20000530,struct.pack('<I',0x400|(0x80 if busy else 0)));u.mem_write(0x40290180,struct.pack('<I',0x1000001));u.mem_write(0x4029341c,struct.pack('<I',int(ready)));u.mem_write(0x200009cc,b'\x03');u.mem_write(0x200009c8,struct.pack('<I',999));u.reg_write(UC_ARM_REG_PRIMASK,mask);return u
# Full wrapper through recovered LP launch, not a launch-entry stub.
for old,busy,ready,null in itertools.product([2,3],[False,True],[False,True],[False,True]):
 vals=[]
 for native in [False,True]:
  u=fixture(old,busy,ready,0);r=g['call'](u,g['symbols']['touch_start_all_lp'] if native else 0x7050,[0 if null else 0x200004ec]);vals.append((r,bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(0x40290000,0x4000))))
 assert vals[0]==vals[1];rows.append({'kind':'all_lp_wrapper','prior_mode':old,'initial_busy':busy,'bridge_ready':ready,'null_context':null,'return':vals[0][0]})
for old,busy,ready,signal,after,mask in itertools.product([2,3],[False,True],[False,True],[False,True],[0,1,3],[0,1]):
 vals=[];metadata=[]
 for native in [False,True]:
  u=fixture(old,busy,ready,mask);u.mem_write(0x20002000,struct.pack('<III',0x4493,0x449b,(deep|1) if native else 0xa58d));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001)
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x200004ec,0x200009cc,0x200009c8,0x20002000]):u.reg_write(reg,value)
  state={'restores':0,'sleep':0,'wfi':0,'irq':0,'action':None,'skip':False};bus=[]
  def code(u,a,n,data):
   if not native and a in [0x3e6e,0x3e8c]:state['action']='done';u.emu_stop()
   if a in [0xa58c,deep]:state['sleep']+=1
   if a in [0xa3a0,native_wfi]:state['wfi']+=1
   if a==0x449e:
    caller=u.reg_read(UC_ARM_REG_LR)&~1
    if not (0x3e28<=caller<0x3e60 or app_start<=caller<app_end):return # Exclude PM's nested critical restoration.
    if state['skip']:state['skip']=False;return
    state['restores']+=1;still_busy=bool(struct.unpack('<I',u.mem_read(0x20000530,4))[0]&0x80)
    # Inject after restoring PRIMASK, never dispatch through a masked critical section.
    if still_busy and after and state['restores']==after and u.reg_read(UC_ARM_REG_PRIMASK)==0 and (ready or busy):state['action']='irq';u.emu_stop()
    elif still_busy and state['restores']>=3:state['action']='bounded_wait';u.emu_stop()
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40400000 or 0xe000e000<=a<0xe000f000:bus.append(['read',a,n])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40400000 or 0xe000e000<=a<0xe000f000:bus.append(['write',a,n,v])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);pc=g['symbols']['touch_app_lp_phase'] if native else 0x3e29
  for resume in range(30):
   state['action']=None;u.emu_start(pc|1,0x20000000,count=300000);pc=u.reg_read(UC_ARM_REG_PC)
   if state['action']=='irq':
    saved=u.context_save();u.mem_write(0x40290120,struct.pack('<I',int(signal)));g['call'](u,g['symbols']['touch_scan_isr'] if native else 0x6780,[0x200004ec]);u.context_restore(saved);state['irq']+=1;state['skip']=True;continue
   if state['action'] in ['done','bounded_wait'] or pc==0x20000000:break
   # Unicorn may yield at WFI; resume sequential instructions with no timing model.
   assert pc in [0xa3a0,0xa3a2,native_wfi,native_wfi+2],('unexpected stop',hex(pc),state)
  else:raise AssertionError('resume bound')
  endpoint='bounded_wait' if state['action']=='bounded_wait' else 'done';metadata.append(dict(endpoint=endpoint,restores=state['restores'],sleep_calls=state['sleep'],wfi_instructions=state['wfi'],irq_injections=state['irq'],final_primask=u.reg_read(UC_ARM_REG_PRIMASK),application_state=u.mem_read(0x200009cc,1)[0],budget=struct.unpack('<I',u.mem_read(0x200009c8,4))[0],common_status=hex(struct.unpack('<I',u.mem_read(0x20000530,4))[0])));vals.append((metadata[-1],bus,bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(0x40290000,0x4000)),bytes(u.mem_read(0xe000ed00,0x100))))
 assert vals[0]==vals[1],(old,busy,ready,signal,after,mask,[j for j,(a,b) in enumerate(zip(*vals)) if a!=b],metadata);rows.append({'kind':'application_lp_slice','prior_mode':old,'initial_busy':busy,'bridge_ready':ready,'injected_signal':signal,'requested_irq_after_restore':after,'initial_primask':mask,**metadata[0]})
# Public no-callback helper is behaviorally tested, not byte-exact attributed.
for key,scr in itertools.product([0,1,0x8000,0xffff],[0,0xffffffff]):
 vals=[]
 for native in [False,True]:
  u=fixture(2,False,True,0);u.mem_write(0x0ffff152,struct.pack('<H',key));u.mem_write(0xe000ed10,struct.pack('<I',scr));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);target=native_wfi if native else 0xa3a0
  def stop_wfi(u,a,n,data):
   if a==target:u.emu_stop()
  u.hook_add(UC_HOOK_CODE,stop_wfi);u.emu_start((low|1) if native else 0xa389,0x20000000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==target;out=struct.unpack('<II',u.mem_read(0x40030000,8))[1];new=struct.unpack('<I',u.mem_read(0xe000ed10,4))[0];assert out==key and new==(scr|4);vals.append((out,new,u.reg_read(UC_ARM_REG_PRIMASK)))
 assert vals[0]==vals[1];rows.append({'kind':'public_no_callbacks_pre_wfi_behavior','synthetic_key_delay':key,'initial_scr':hex(scr),'stored_key_delay':vals[0][0],'final_scr':hex(vals[0][1])})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Wrapper executes full original/recovered LP launch; app comparison stops before logs/config/deferred/report/common-loop dependencies.','Original4492/449a critical providers execute on both sides; native side uses compiled pinned public PM sleep/NoCallbacks source, original side stocka58c/a388; PM callback table synthetic-zero. Callback executor remains original address boundary and is not exercised.','IRQ injected with CPU-context save/restore after PRIMASK restoration; direct original/native ISR, not hardware delivery/timing.','Bounded_wait means stopped after3 restored busy iterations, not proof of a hardware deadlock or eventual completion.','Initialization/preparation setup uses independently validated source with actual reset pointers, not full application startup.','Eight no-callback helper cases compare preparation before WFI; no physical sleep/wake or arbitrary SCR-mode execution claim.']},indent=2)+'\n');print('PASS',len(rows))
