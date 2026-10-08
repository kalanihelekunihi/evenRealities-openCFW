from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-preparation-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split("for kind in ['fields'")[0],ns);g=ns['g'];rows=[]
regions=ns['regions']+[(0x40002000,0x1000),(0x20008800,1024),(0x20009200,64)]+[(0x20006500+j*40,40) for j in range(3)]
def fixture(enabled=7,hw_iir=0,cycles=2,slots=1,method=1,sign=0,callbacks=0,control=0,mrss=0x1000000):
 u,bus=ns['fixture'](2,0,False,0,True,0,0);u.mem_write(0x20002000+56,struct.pack('<I',0x20008800));u.mem_write(0x20008800,b'\xa5'*1024);u.mem_write(0x20003500+118,bytes([hw_iir]));u.mem_write(0x20003200+8,struct.pack('<I',0xa5a58081));u.mem_write(0x20003200+4,struct.pack('<H',65535));u.mem_write(0x20003200+27,b'\xff');u.mem_write(0x20009200+60,struct.pack('<I',control));u.mem_write(0x40000180,struct.pack('<I',mrss));u.mem_write(0x40003410,struct.pack('<I',cycles*slots));u.mem_write(0x40003414,struct.pack('<I',sign));u.mem_write(0x20003500,struct.pack('<II',g['symbols']['touch_test_scan_start'] if callbacks&1 else 0,g['symbols']['touch_test_scan_end'] if callbacks&2 else 0))
 for j in range(3):
  u.mem_write(0x20005000+j*60+35,bytes([6 if enabled&(1<<j) else 0]));u.mem_write(0x20005000+j*60+4,struct.pack('<H',100));u.mem_write(0x20004000+j*144+122,bytes([method if j==1 else 1]))
  for sensor in range(4):u.mem_write(0x20006500+j*40+sensor*10+6,b'\xa7')
 for j in range(21):u.mem_write(0x40002000+j*44+12,struct.pack('<I',0xab123456+j))
 reads=[]
 def fifo(u,access,a,n,v,data):
  if a==0x40003200:
   value=[0x12340032,0x10065,0x1ffff,0x123456][len(reads)%4];u.mem_write(a,struct.pack('<I',value));reads.append(value)
 u.hook_add(UC_HOOK_MEM_READ,fifo);return u,bus,reads

def snap(u,bus,reads,normalize=False):
 values=[]
 for a,n in regions:
  b=bytearray(u.mem_read(a,n))
  if normalize and a==0x20003500:b[16:20]=b'\0'*4
  values.append(b.hex())
 return (bus,reads,*values,u.reg_read(UC_ARM_REG_PRIMASK))

def run_pair(name,pc,args,prepare,normalize=False):
 vals=[]
 for native in [False,True]:
  u,bus,reads=prepare(native)
  g['call'](u,g['symbols'][name] if native else pc,args);vals.append(snap(u,bus,reads,normalize))
 assert vals[0]==vals[1],(name,args,[(i,a,b) for i,(a,b) in enumerate(zip(vals[0],vals[1])) if a!=b]);return vals[0]
for start,count,enable,iir,irq in itertools.product([0,1,3],[1,2],[0,3,7],[0,1],[0,1]):
 def f(native):
  u,b,r=fixture(enable,iir);u.reg_write(UC_ARM_REG_PRIMASK,irq);return u,b,r
 a=run_pair('touch_transfer_active',0x6462,[start,count,0x20002000],f);rows.append({'kind':'active_transfer','start':start,'count':count,'enabled':enable,'hw_iir':iir,'primask':irq,'fifo_reads':len(a[1])})
for start,count,enable,cycles,method,sign in itertools.product([0,1,2],[1,2],[0,1,2,3,4,7],[0,1,2,256],[1,2,10],[0,0x80000000]):
 def f(native):return fixture(enable,0,cycles,count,method,sign)
 a=run_pair('touch_transfer_low_power',0x6530,[start,count,0x20002000],f);rows.append({'kind':'lp_transfer','start':start,'count':count,'enabled':enable,'cycles':cycles,'method_widget1':method,'category_bit31':bool(sign),'fifo_reads':len(a[1])})
for count,first,callback,control,mrss in itertools.product([0,1,2,5,21,30],[0,1,2],[0,1],[0,1],[0,0x1000000]):
 def f(native):
  u,b,r=fixture(callbacks=callback,control=control,mrss=mrss);u.mem_write(0x20003500+97,bytes([first]));u.mem_write(0x20002000+40,struct.pack('<I',0x20006000));u.mem_write(0x20006000,b''.join(struct.pack('<7I',*[0x1020304*(j+1)+k for k in range(7)]) for j in range(21)));return u,b,r
 a=run_pair('touch_scan_slots',0x664c,[0,count,0x20002000],f);rows.append({'kind':'scan_slots','requested_count':count,'first':first,'callback':callback,'control':control,'mrss_bit24':bool(mrss)})
for intr,mask,processing,count,last,callbacks,enable,iir in itertools.product([0,1,0x10000,0x10001],[0,0x10000],[0,1],[1,2],[1,4],[0,2],[3,7],[0,1]):
 def f(native):
  u,b,r=fixture(enable,iir,2,count,2,0,callbacks);u.mem_write(0x40000120,struct.pack('<I',intr));u.mem_write(0x40000128,struct.pack('<I',mask));u.mem_write(0x20003200+22,struct.pack('<H',processing));u.mem_write(0x20003500+52,struct.pack('<HH',0,last));u.mem_write(0x20003500+70,struct.pack('<H',count));return u,b,r
 a=run_pair('touch_scan_isr',0x6780,[0x20002000],f);rows.append({'kind':'isr','intr':intr,'mask':mask,'processing':processing,'count':count,'last':last,'end_callback':callbacks==2,'enabled':enable,'hw_iir':iir,'fifo_reads':len(a[1])})
for active,bad,lock,callback in itertools.product([False,True],[False,True],[0,2,255],[0,2]):
 vals=[]
 for native in [False,True]:
  u,bus,reads=fixture(callbacks=callback);u.mem_write(0x20003700,bytes([lock]));
  if bad:u.mem_write(0x20005000+60+14,struct.pack('<H',7))
  status=g['call'](u,g['symbols']['touch_prepare_scan_isr_bound'] if native else 0x71c8,[0x20002000]);entry=struct.unpack('<I',u.mem_read(0x20003500+16,4))[0];assert entry==(g['symbols']['touch_scan_isr'] if native else 0x6781)
  u.mem_write(0x40000120,struct.pack('<I',0x10000 if active else 1));u.mem_write(0x40000128,struct.pack('<I',0x10000 if active else 0));u.mem_write(0x20003200+22,struct.pack('<H',1));u.mem_write(0x20003500+52,struct.pack('<HH',0,0));u.mem_write(0x20003500+70,struct.pack('<H',1));g['call'](u,entry,[0x20002000]);vals.append((status,snap(u,bus,reads,True)))
 assert vals[0]==vals[1],(active,bad,lock,callback,vals);rows.append({'kind':'preparation_bound_isr','active':active,'clock_error':bad,'lock':lock,'end_callback':bool(callback),'prepare_status':vals[0][0],'isr_pointer_identity_normalized':True})
for which,arg,active in itertools.product(['dispatch','msclp'],[0,1,255],[False,True]):
 vals=[]
 for native in [False,True]:
  u,bus,reads=fixture(callbacks=2);u.mem_write(0x20003500+16,struct.pack('<I',g['symbols']['touch_scan_isr'] if native else 0x6781));u.mem_write(0x40000120,struct.pack('<I',0x10000 if active else 1));u.mem_write(0x40000128,struct.pack('<I',0x10000 if active else 0));u.mem_write(0x20003200+22,struct.pack('<H',1));u.mem_write(0x20003500+52,struct.pack('<HH',0,0));u.mem_write(0x20003500+70,struct.pack('<H',1));name='touch_interrupt_dispatch' if which=='dispatch' else 'touch_msclp_interrupt';pc=0x5fba if which=='dispatch' else 0x5c98;g['call'](u,g['symbols'][name] if native else pc,[arg,0x20002000]);vals.append(snap(u,bus,reads,True))
 assert vals[0]==vals[1],(which,arg,active,vals);rows.append({'kind':'dispatch_chain','wrapper':which,'ignored_argument':arg,'active':active,'isr_pointer_identity_normalized':True})
# Actual locked project context pointers from reset-copied data; direct entry calls.
for active,process,enable in itertools.product([False,True],[False,True],[False,True]):
 vals=[]
 for native in [False,True]:
  u=g['guest']();u.mem_write(0x20000400,g['fw'][32:32+0xc0]);u.mem_write(0x200004c0,g['fw'][32+0xb58c-0x3300:32+0xb58c-0x3300+0xf1*4]);u.mem_write(0x200008a8,b'\0'*(0x1ac*4));u.mem_map(0x40290000,0x10000);u.mem_write(0x20000c50+16,struct.pack('<I',g['symbols']['touch_scan_isr'] if native else 0x6781));u.mem_write(0x20000c50+52,struct.pack('<HH',0,0));u.mem_write(0x20000c50+70,struct.pack('<H',1));u.mem_write(0x20000528+22,struct.pack('<H',int(process)));u.mem_write(0x20000548+35,bytes([6 if enable else 0]));u.mem_write(0x40290120,struct.pack('<I',0x10000 if active else 1));u.mem_write(0x40290128,struct.pack('<I',0x10000 if active else 0));u.mem_write(0x40293410,struct.pack('<I',1));u.mem_write(0x40293200,struct.pack('<I',0x10032));bus=[]
  def project_read(u,access,a,n,v,data):
   if 0x40290000<=a<0x402a0000:bus.append(['read',a,n])
  def project_write(u,access,a,n,v,data):
   if 0x40290000<=a<0x402a0000:bus.append(['write',a,n,v])
  u.hook_add(UC_HOOK_MEM_READ,project_read);u.hook_add(ns['UC_HOOK_MEM_WRITE'],project_write);g['call'](u,g['symbols']['touch_project_msclp_irq'] if native else 0x3948,[]);ram=bytearray(u.mem_read(0x20000000,0x2000));ram[0xc60:0xc64]=b'\0'*4;vals.append((bus,ram.hex(),u.mem_read(0x40290000,0x4000).hex()))
 assert vals[0]==vals[1],(active,process,enable,vals);rows.append({'kind':'locked_project_irq_entry','active':active,'lp_processing':process,'enabled_widget0':enable,'context':'0x200004ec','hardware':'0x40290000','isr_pointer_identity_normalized':True})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Complete original ISR/helpers vs actual independent source; no function-entry stubs.','Synthetic FIFO pop sequences, registers/factory trim, direct calls not hardware interrupt delivery.','External callbacks are null or compiled synthetic ABI/order probes; no unknown callback-body claim.','LP count>0 and coherent stable context pointers; active ranges bounded by allocated descriptors.','Preparation composition normalizes only bound ISR address; not byte equality.','Scan-slot capacity21 tested with separately allocated21-frame synthetic source; locked project generation has5 active slots.']},indent=2)+'\n');print('PASS',len(rows))
