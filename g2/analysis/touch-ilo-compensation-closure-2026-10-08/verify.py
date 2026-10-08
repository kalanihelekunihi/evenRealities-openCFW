from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-lp-application-closure-2026-10-08/verify.py';ns={'__file__':str(s)};text=s.read_text();exec(text.split('from elftools.elf')[0],ns);exec('def fixture'+text.split('def fixture',1)[1].split('# Full wrapper')[0],ns);g=ns['g'];rows=[]
def bare():
 u=g['guest']();u.mem_map(0x40030000,0x1000);return u
def trace(u):
 events=[]
 def read(u,access,a,n,v,data):
  if 0x40030000<=a<0x40030100:events.append(['read',a,n])
 def write(u,access,a,n,v,data):
  if 0x40030000<=a<0x40030100:events.append(['write',a,n,v])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);return events
def snap(u):return (bytes(u.mem_read(0x20000f1c,3)),bytes(u.mem_read(0x20003000,4)),bytes(u.mem_read(0x40030000,0x100)))
for stop,prevent,measuring,sel,ctl in itertools.product([False,True],[0,1],[0,1],[0,0xffffffff],[0,0x908,0xffffffff]):
 vals=[]
 for mode in range(3):
  u=bare();u.mem_write(0x20000f1c,bytes([1,prevent,measuring]));u.mem_write(0x40030034,struct.pack('<I',sel));u.mem_write(0x40030018,struct.pack('<I',ctl));bus=trace(u);entry=(0x9ddc if stop else 0x9d90) if mode==0 else g['symbols'][('touch_ilo_stop' if stop else 'touch_ilo_start') if mode==1 else ('Cy_SysClk_IloStopMeasurement' if stop else 'Cy_SysClk_IloStartMeasurement')];g['call'](u,entry,[]);vals.append((bus,snap(u)))
 assert vals[0]==vals[1]==vals[2];rows.append({'kind':'start_stop','stop':stop,'prevent':prevent,'initial_measurement':measuring,'initial_selection':hex(sel),'initial_control':hex(ctl)})
for delay,core,counter,configuration,null,running,done in itertools.product([99,100,500,2000000,2000001],[1024,24000000],[0,40,256,0x100000,0xffffffff],['valid','control_bad','selection_bad'],[False,True],[0,1],[False,True]):
 vals=[]
 for mode in range(3):
  u=bare();u.mem_write(0x20000878,struct.pack('<I',core));u.mem_write(0x20000f1c,bytes([running,0,1]));u.mem_write(0x20003000,struct.pack('<I',0xabcdef01));u.mem_write(0x40030018,struct.pack('<I',0x1908 if configuration=='control_bad' else 0x908));u.mem_write(0x40030034,struct.pack('<I',0 if configuration=='selection_bad' else 0x100));u.mem_write(0x4003001c,struct.pack('<I',0x80000000 if done else 0));u.mem_write(0x40030020,struct.pack('<I',counter));bus=trace(u);entry=[0x9e18,g['symbols']['touch_ilo_measure'],g['symbols']['Cy_SysClk_IloCompensate']][mode];r=g['call'](u,entry,[delay,0 if null else 0x20003000]);vals.append((r,bus,snap(u)))
 assert vals[0]==vals[1]==vals[2],(delay,core,counter,configuration,null,running,done,[j for j,(a,b,c) in enumerate(zip(*vals)) if a!=b or a!=c]);rows.append({'kind':'measurement','requested_us':delay,'system_core_clock_input':core,'synthetic_counter2':counter,'configuration':configuration,'null_output':null,'running':running,'done':done,'return':hex(vals[0][0]),'output':struct.unpack('<I',vals[0][2][1])[0]})
for counter,prevent,running,flags,ready_after in itertools.product([0,39,40,255,256],[0,1],[0,1],[0,0x10,0x20,0x30],[0,1,3]):
 vals=[]
 for mode in range(3):
  u=ns['fixture'](2,False,True,0);u.mem_write(0x20000f1c,bytes([running,prevent,0]));u.mem_write(0x20000878,struct.pack('<I',24000000));u.mem_write(0x20000530,struct.pack('<I',flags));u.mem_write(0x20000c50+28,struct.pack('<I',7773));u.mem_write(0x20000c50+36,struct.pack('<I',62500));u.mem_write(0x40030020,struct.pack('<I',counter));u.mem_write(0x40290070,struct.pack('<I',0xa5a50000));state={'reads':0,'attempts':0,'stopped':False};bus=trace(u);measure=[0x9e18,g['symbols']['touch_ilo_measure']&~1,g['symbols']['Cy_SysClk_IloCompensate']&~1][mode]
  def read_ready(u,access,a,n,v,data):
   if a==0x4003001c:
    state['reads']+=1
    if ready_after and state['reads']>=ready_after:u.mem_write(a,struct.pack('<I',0x80000000))
  def code(u,a,n,data):
   if a==measure:
    state['attempts']+=1
    if state['attempts']==6:state['stopped']=True;u.emu_stop()
  u.hook_add(UC_HOOK_MEM_READ,read_ready);u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,0x200004ec);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);entry=[0x5dd8,g['symbols']['touch_ilo_compensate'],g['symbols']['Cy_CapSense_IloCompensate']][mode];u.emu_start(entry|1,0x20000000,count=300000);assert state['stopped'] or u.reg_read(UC_ARM_REG_PC)==0x20000000
  selected=struct.unpack('<I',u.mem_read(0x40290070,4))[0];factor=struct.unpack('<I',u.mem_read(0x20000c50+44,4))[0]
  if not state['stopped']:
   assert u.reg_read(UC_ARM_REG_R0)==0;assert factor==((counter<<24)&0xffffffff)//1000000;chosen=struct.unpack('<I',u.mem_read(0x20000c50+(40 if flags&0x20 else 32),4))[0];assert selected==0xa5a50000|chosen
  else:assert factor==655 and selected==0xa5a50000
  vals.append((state,bus,bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(0x40030000,0x100)),bytes(u.mem_read(0x40290000,0x4000))))
 assert vals[0]==vals[1]==vals[2],('outer',counter,prevent,running,hex(flags),ready_after,[j for j,(a,b,c) in enumerate(zip(*vals)) if a!=b or a!=c]);rows.append({'kind':'full_compensation','synthetic_counter2':counter,'prevent':prevent,'initial_running':running,'status_flags':hex(flags),'synthetic_done_after_reads':ready_after,'bounded_wait':vals[0][0]['stopped'],'attempts_seen':vals[0][0]['attempts'],'factor':factor,'selected_aos':hex(selected)})
for mode in range(3):
 u=ns['fixture'](2,False,True,0);before=(snap(u),bytes(u.mem_read(0x20000c50,128)));r=g['call'](u,[0x5dd8,g['symbols']['touch_ilo_compensate'],g['symbols']['Cy_CapSense_IloCompensate']][mode],[0]);assert r==1 and before==(snap(u),bytes(u.mem_read(0x20000c50,128)))
rows.append({'kind':'null_compensation_three_way','return':1})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Three-way original/independent/public selected source with explicit ARM32 macro/global environment; no function-entry stubs.','Public CapSense calculator peer resolves original5d71; independent reconstruction uses sealed native calculator.','Synthetic register readiness/counts; bounded_wait stops before sixth measurement body, not hardware deadlock/physical frequency evidence.','Stable coherent globals and SystemCoreClock>=1024; zero denominator behavior not reconstructed.','Actual reset configuration seeded by validated init/prepare source, not full startup; prevention-lock/PM callback registration lifecycle not established.','No generated history-allocation, hardware safety, physical cadence or whole-image source/byte-equality claim.']},indent=2)+'\n');print('PASS',len(rows))
