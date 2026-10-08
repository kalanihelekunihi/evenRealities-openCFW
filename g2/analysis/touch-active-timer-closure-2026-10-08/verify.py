from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-lp-application-closure-2026-10-08/verify.py';ns={'__file__':str(s)};text=s.read_text();exec(text.split('from elftools.elf')[0],ns);exec('def fixture'+text.split('def fixture',1)[1].split('# Full wrapper')[0],ns);g=ns['g'];rows=[]
def fixture():return ns['fixture'](2,False,True,0)
def snapshot(u):return (bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(0x40290000,0x4000)))
for interval,factor,flags in itertools.product([0,1,24,25,7773,31211,62500,65536,1000000,0xffffffff],[0,1,655,16384,65536,0xffffffff],[0,0x10,0x20,0x30]):
 vals=[]
 for native in [0,1,2]:
  u=fixture();u.mem_write(0x20000c50+44,struct.pack('<I',factor));u.mem_write(0x20000530,struct.pack('<I',flags));u.mem_write(0x40290070,struct.pack('<I',0xa5a5ffff));bus=[]
  def write(u,access,a,n,v,data):
   if a==0x40290070:bus.append(v)
  u.hook_add(UC_HOOK_MEM_WRITE,write);entry=0x5d90 if native==0 else g['symbols']['touch_set_active_interval'] if native==1 else g['symbols']['Cy_CapSense_ConfigureMsclpTimer'];r=g['call'](u,entry,[interval,0x200004ec]);expected=((interval*factor)&0xffffffff)>>14;expected=max(expected-1,0);expected=min(expected,65535);assert struct.unpack('<II',u.mem_read(0x20000c50+28,8))==(interval,expected);assert struct.unpack('<I',u.mem_read(0x40290070,4))[0]==(0xa5a50000|expected if flags&16 else 0xa5a5ffff);vals.append((r,bus,snapshot(u)))
 assert vals[0]==vals[1]==vals[2];rows.append({'kind':'active_setter','microseconds':interval,'injected_factor':factor,'status_flags':hex(flags),'cycles_minus_one':expected,'live_aos_updated':bool(flags&16),'return':vals[0][0]})
for interval in [0,7773,31211,0xffffffff]:
 vals=[]
 for native in [0,1,2]:
  u=fixture();before=snapshot(u);entry=0x5d90 if native==0 else g['symbols']['touch_set_active_interval'] if native==1 else g['symbols']['Cy_CapSense_ConfigureMsclpTimer'];r=g['call'](u,entry,[interval,0]);assert snapshot(u)==before;vals.append(r)
 assert vals==[1,1,1];rows.append({'kind':'setter_null','microseconds':interval,'return':1})
for first,count,flags,old,mrss,reuse in itertools.product([0,1,4],[0,1,2,5,6],[0,0x10,0x20,0x2010,0x90],[2,3,4],[0,0x1000001],[False,True]):
 vals=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20000530,struct.pack('<I',flags));u.mem_write(0x20000c50+85,bytes([old]));u.mem_write(0x20000c50+70,struct.pack('<H',count if reuse else 0));u.mem_write(0x20000c50+72,struct.pack('<H',first if reuse else 65535));u.mem_write(0x20000c50+118,bytes([int(bool(flags&16))]));u.mem_write(0x40290180,struct.pack('<I',mrss));g['call'](u,g['symbols']['touch_set_active_interval'] if native else 0x5d90,[31211,0x200004ec]);bus=[]
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40400000:bus.append(['read',a,n])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40400000:bus.append(['write',a,n,v])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);r=g['call'](u,g['symbols']['touch_start_active_slots'] if native else 0x6bd4,[first,count,0x200004ec]);vals.append((r,bus,snapshot(u)))
 assert vals[0]==vals[1],(first,count,hex(flags),old,hex(mrss),reuse,[j for j,(a,b) in enumerate(zip(*vals)) if a!=b]);rows.append({'kind':'active_launch_composition','first':first,'slots':count,'status_flags':hex(flags),'prior_mode':old,'mrss':hex(mrss),'reuse_metadata':reuse,'return':vals[0][0]})
# Actual LP completion -> caller interval setter -> active launch/ISR/reuse.
for signal,hw_iir in itertools.product([False,True],[0,1]):
 vals=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20000c50+118,bytes([hw_iir]));assert g['call'](u,g['symbols']['touch_start_lp_slots'] if native else 0x6d74,[0,4,0x200004ec])==0;u.mem_write(0x40290120,struct.pack('<I',int(signal)));g['call'](u,g['symbols']['touch_scan_isr'] if native else 0x6780,[0x200004ec]);lp_timer=struct.unpack('<I',u.mem_read(0x40290070,4))[0];interval=7773 if signal else 31211;assert g['call'](u,g['symbols']['touch_set_active_interval'] if native else 0x5d90,[interval,0x200004ec])==0;assert struct.unpack('<I',u.mem_read(0x40290070,4))[0]==lp_timer;expected=struct.unpack('<I',u.mem_read(0x20000c50+32,4))[0];assert g['call'](u,g['symbols']['touch_start_active_slots'] if native else 0x6bd4,[0,5,0x200004ec])==0;assert struct.unpack('<I',u.mem_read(0x40290070,4))[0]&65535==expected
  u.mem_write(0x40290120,struct.pack('<I',0x10000));g['call'](u,g['symbols']['touch_scan_isr'] if native else 0x6780,[0x200004ec]);other=31211 if signal else 7773;g['call'](u,g['symbols']['touch_set_active_interval'] if native else 0x5d90,[other,0x200004ec]);other_cycles=struct.unpack('<I',u.mem_read(0x20000c50+32,4))[0];assert struct.unpack('<I',u.mem_read(0x40290070,4))[0]&65535==other_cycles;stores=[]
  def writes(u,access,a,n,v,data):
   if 0x40292000<=a<0x40292400:stores.append(a)
  u.hook_add(UC_HOOK_MEM_WRITE,writes);assert g['call'](u,g['symbols']['touch_start_active_slots'] if native else 0x6bd4,[0,5,0x200004ec])==0;assert not stores;vals.append((snapshot(u),lp_timer,expected,other_cycles))
 assert vals[0]==vals[1];rows.append({'kind':'locked_lp_active_timer_isr_reuse','lp_signal':signal,'injected_hw_iir':hw_iir,'requested_active_us':interval,'active_cycles_minus_one':vals[0][2],'updated_active_us':other,'updated_cycles_minus_one':vals[0][3],'reuse_sensor_stores':0})
for budget,flags in itertools.product([0,1,2,160,640,0xffffffff],[0x10,0x20]):
 vals=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x200009cc,b'\x01');u.mem_write(0x200009c8,struct.pack('<I',budget));u.mem_write(0x20000530,struct.pack('<I',flags));
  if native:g['call'](u,g['symbols']['touch_active_budget_step'],[0x200009cc,0x200009c8,0x200004ec])
  else:u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x3d7f,0x3d4c,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x3d4c
  vals.append(snapshot(u))
 assert vals[0]==vals[1];rows.append({'kind':'successful_state1_budget_tail','initial_budget':budget,'status_flags':hex(flags),'final_budget':160 if budget==1 else (budget-1)&0xffffffff,'final_state':2 if budget==1 else 1})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'validation_modes':{'active_setter_and_null':'Three-way original/independent/public-body comparisons; public body resolves original calculator peer.','active_launch_and_sequences':'Original vs independent closed source composition plus pinned public PDL; synthetic peripherals.','budget_tail':'Original successful state1 slice includes real no-op logger; native omits that no-op.'},'limits':['Full stock5d90/6bd4 vs independent source plus validated loader/mode/pinned PDL, no function-entry stubs.','Actual reset-copied configuration seeded through validated init/prepare source, not full startup; synthetic MMIO/MRSS/IRQ/FIFO.','Interval units supported by pinned SDK comparator; factor/time accuracy depends on real compensation/hardware, not established here.','Budget tail begins only after successful state1 processing; original executes proven no-op logger, native omits it; report/reset/other state paths outside this tail.','No physical timing/deadlock/callback/hardware-safety/source-complete/byte-equal claim.']},indent=2)+'\n');print('PASS',len(rows))
