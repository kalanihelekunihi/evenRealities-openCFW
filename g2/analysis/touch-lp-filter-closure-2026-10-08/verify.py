from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-isr-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for start,count,enable,iir,irq')[0],ns);g=ns['g'];rows=[]
for first,count,busy,repeat,mrss,ready,lock,old in itertools.product([0,1,3,4],[0,1,2,4,9],[False,True],[False,True],[0,1,0x1000001],[False,True],[0,2],[0,2]):
 vals=[]
 for native in [False,True]:
  u,b,r=ns['fixture']();u.mem_write(0x20003700,bytes([lock]));u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20003500+52,struct.pack('<HH',first,(first+count-1)&65535));u.mem_write(0x20003200+8,struct.pack('<I',0x400|(0x80 if busy else 0)|(0x20 if repeat else 0)));u.mem_write(0x40000180,struct.pack('<I',mrss));u.mem_write(0x4000341c,struct.pack('<I',int(ready)));u.mem_write(0x20003500+74,struct.pack('<H',0xffff));u.mem_write(0x20003500+40,struct.pack('<I',0x1234));bus=[]
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40041000:bus.append(['read',a,n])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40041000:bus.append(['write',a,n,v])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);ret=g['call'](u,g['symbols']['touch_start_lp_slots'] if native else 0x6d74,[first,count,0x20002000]);vals.append((ret,bus,bytes(u.mem_read(0x20000000,0x7c00))+bytes(u.mem_read(0x20008000,0x8000)),bytes(u.mem_read(0x40000000,0x10000))))
 assert vals[0]==vals[1],(first,count,busy,repeat,hex(mrss),ready,lock,[(a[0],len(a[1])) for a in vals],[j for j,(a,b) in enumerate(zip(*vals)) if a!=b],[(hex(0x20000000+k),a,b) for k,(a,b) in enumerate(zip(vals[0][2],vals[1][2])) if a!=b][:20]);rows.append({'kind':'lp_scan_composition','first':first,'slots':count,'busy':busy,'reuse_requested':repeat,'mrss':hex(mrss),'bridge_ready':ready,'driver_lock':lock,'prior_mode':old,'return':vals[0][0]})
# Actual reset-copied configuration: original initialization/prepare slices -> LP scan.
for ready,mrss,coeff,count in itertools.product([False,True],[0,0x1000001],[1,15],[1,2,3,4]):
 vals=[]
 for native in [False,True]:
  u=g['guest']();u.mem_write(0x20000400,g['fw'][32:32+0xc0]);u.mem_write(0x200004c0,g['fw'][32+0xb58c-0x3300:32+0xb58c-0x3300+964]);u.mem_write(0x200008a8,b'\0'*1712);u.mem_map(0x40000000,0x400000);u.mem_map(0x0fff0000,0x10000);u.mem_write(0x0fff0000,bytes(range(256))*256);u.mem_write(0x20000870,b'\x01')
  if native:g['call'](u,g['symbols']['touch_cap_init_fields'],[0x200004ec])
  else:
   u.reg_write(UC_ARM_REG_R0,0x200004ec);u.reg_write(UC_ARM_REG_R4,0x200004ec);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x4c85,0x4d8e,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x4d8e
  u.mem_write(0x20000c50+96,bytes([coeff]));
  if native:prep=g['call'](u,g['symbols']['touch_prepare_scan_fields'],[0x200004ec])
  else:
   u.reg_write(UC_ARM_REG_R0,0x200004ec);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x71c9,0x7228,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x7228;prep=u.reg_read(UC_ARM_REG_R6)
  u.mem_write(0x20000c50+85,b'\x02');u.mem_write(0x40290180,struct.pack('<I',mrss));u.mem_write(0x4029341c,struct.pack('<I',int(ready)));frame=bytes(u.mem_read(0x200009fc,176));ret=g['call'](u,g['symbols']['touch_start_lp_slots'] if native else 0x6d74,[0,count,0x200004ec]);reused=None; history_observation=None
  if not ret:
   hwcoeff=struct.unpack('<I',u.mem_read(0x40292000,4))[0]&15;u.mem_write(0x40290120,struct.pack('<I',1));g['call'](u,g['symbols']['touch_scan_isr'] if native else 0x6780,[0x200004ec]);assert not(struct.unpack('<I',u.mem_read(0x20000530,4))[0]&0x81)
   word=struct.unpack('<I',u.mem_read(0x200009fc,4))[0];u.mem_write(0x200009fc,struct.pack('<I',(word&~15)|(15 if coeff==1 else 1)));stores=[]
   def writes(u,access,a,n,v,data):
    if 0x40292000<=a<0x40292000+176:stores.append(a)
   u.hook_add(UC_HOOK_MEM_WRITE,writes);reused=g['call'](u,g['symbols']['touch_start_lp_slots'] if native else 0x6d74,[0,count,0x200004ec]);assert reused==0 and not stores;assert struct.unpack('<I',u.mem_read(0x40292000,4))[0]&15==hwcoeff
   # Nominal configured result-window arithmetic, supplied synthetically.
   start_word=(struct.unpack('<I',u.mem_read(0x40290008,4))[0]>>16)&1023;used=((256-start_word)//count)*count;history_stores=[]
   def history_write(u,access,a,n,v,data):
    if 0x2000065e<=a<0x200008a8:history_stores.append([a,n,v])
   u.hook_add(UC_HOOK_MEM_WRITE,history_write);u.mem_write(0x20000528+22,struct.pack('<H',1));u.mem_write(0x40293410,struct.pack('<I',used));u.mem_write(0x40293200,struct.pack('<I',0));g['call'](u,g['symbols']['touch_scan_isr'] if native else 0x6780,[0x200004ec]);history_observation={'result_start_word':start_word,'synthetic_used':used,'frames':u.mem_read(0x20000528+26,1)[0],'logical_bytes':used*2,'stores':len(history_stores),'stores_touching_next_object':sum(a+n>0x20000808 for a,n,v in history_stores)}
  ram=bytearray(u.mem_read(0x20000000,0x2000));# prepare stores stock ISR metadata identically on both sides.
  vals.append((prep,ret,bytes(ram),bytes(u.mem_read(0x40290000,0x4000)),frame))
 assert vals[0]==vals[1],('actual',ready,hex(mrss),coeff,[j for j,(a,b) in enumerate(zip(*vals)) if a!=b]);prefix=struct.unpack('<5I',vals[0][4][:20]);rows.append({'kind':'locked_init_prepare_lp_composition','bridge_ready':ready,'mrss':hex(mrss),'injected_rc_coefficient':coeff,'slots':count,'prepare_status':vals[0][0],'return':vals[0][1],'lp_prefix_words':[hex(v) for v in prefix],'ce_ctl':hex(struct.unpack_from('<I',vals[0][3],0x74)[0]),'reused_scan_return_after_irq_and_frame_mutation':reused,'configured_window_synthetic_history':history_observation})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['No function-entry stubs; original LP scan and independent mode/GPIO/wait plus pinned public PDL execute.','Actual configuration compositions use explicit4c84..4d8e initialization and71c8..7228 preparation slices, not full initialization/preparation.','Synthetic MMIO/SFLASH/bridge/MRSS; direct calls not physical IRQ/analog filter/timing.','Locked composition forces currentmode2 after preparation and injects coefficient1/15; no whole application startup claim.']},indent=2)+'\n');print('PASS',len(rows))
