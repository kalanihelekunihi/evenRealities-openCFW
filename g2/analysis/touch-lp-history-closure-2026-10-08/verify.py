from pathlib import Path
import sys,json,struct,itertools,hashlib,random
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-isr-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for start,count,enable,iir,irq')[0],ns);g=ns['g'];rows=[];rng=random.Random(0x7e04)
for n in range(48):
 common=rng.randbytes(32);vals=[]
 for native in [False,True]:
  u,b,r=ns['fixture']();u.mem_write(0x20003200,common);g['call'](u,g['symbols']['touch_lp_history_reset'] if native else 0x7e04,[0x20002000]);vals.append((u.mem_read(0x20003200,32).hex(),u.mem_read(0x20008800,1024).hex()))
 assert vals[0]==vals[1];rows.append({'kind':'stock_reset','case':n,'common':vals[0][0]})
def actual(native,gate,enabled,used,sign,count,raw):
 u=g['guest']();u.mem_write(0x20000400,g['fw'][32:32+0xc0]);u.mem_write(0x200004c0,g['fw'][32+0xb58c-0x3300:32+0xb58c-0x3300+0xf1*4]);u.mem_write(0x200008a8,b'\0'*(0x1ac*4));u.mem_map(0x40290000,0x10000);u.mem_write(0x20000c50+16,struct.pack('<I',g['symbols']['touch_scan_isr'] if native else 0x6781));u.mem_write(0x20000c50+52,struct.pack('<H',0));u.mem_write(0x20000c50+70,struct.pack('<H',count));u.mem_write(0x20000528+22,struct.pack('<H',gate));u.mem_write(0x20000548+35,bytes([6 if enabled else 0]));u.mem_write(0x2000065e,b'\xa5'*426);u.mem_write(0x40290120,struct.pack('<I',1));u.mem_write(0x40290128,struct.pack('<I',0));u.mem_write(0x40293410,struct.pack('<I',used));u.mem_write(0x40293414,struct.pack('<I',sign));u.mem_write(0x40293200,struct.pack('<I',raw));writes=[];fifo_reads=[0]
 def read(u,access,a,n,v,data):
  if a==0x40293200:fifo_reads[0]+=1
 def write(u,access,a,n,v,data):
  if 0x2000065e<=a<0x20000e60:writes.append([a,n,v])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);g['call'](u,g['symbols']['touch_project_msclp_irq'] if native else 0x3948,[]);return u,writes,fifo_reads[0]
for used,count,gate,enabled,sign,raw in itertools.product([0,1,4,5,212,213,215,216,1024,1028,2047],[1,4],[0,1],[False,True],[0,0x80000000],[0,64]):
 vals=[];original=None
 for native in [False,True]:
  u,writes,reads=actual(native,gate,enabled,used,sign,count,raw);ram=bytearray(u.mem_read(0x20000000,0x2000))
  # Normalize only untouched bytes of the deliberately bound ISR address.
  # Any bytes overwritten by history are compared exactly, including corruption.
  for offset in range(0xc60,0xc64):
   if not any(a<=0x20000000+offset<a+n for a,n,v in writes):ram[offset]=0
  vals.append((ram.hex(),writes,reads,u.mem_read(0x40290000,0x4000).hex()))
  if not native:original=u
 assert vals[0]==vals[1],(used,count,gate,enabled,sign,raw,[i for i,(a,b) in enumerate(zip(vals[0],vals[1])) if a!=b]);overlap=[x for x in vals[0][1] if x[0]+x[1]>0x20000808];meta=original.mem_read(0x20000528,32);frames=meta[26];needed=0x20009000;status=g['call'](original,g['symbols']['touch_lp_history_span'],[0x20000528,426,needed]);byte_need=struct.unpack('<I',original.mem_read(needed,4))[0]
 expected=1 if not gate else 2 if not frames else 4 if 2*meta[25]*frames>426 else 0
 assert status==expected,(used,count,gate,frames,status,expected)
 if status==0:
  for frame in {0,frames-1}:
   for slot in {0,count-1}:
    original.reg_write(UC_ARM_REG_R3,15 if enabled else 0);original.mem_write(0x20008000,struct.pack('<III',frame,slot,0x20009100));original.mem_write(0x20009100,b'\xcc'*8);r=g['call'](original,g['symbols']['touch_lp_history_read'],[0x20000528,0x2000065e,426]);out=original.mem_read(0x20009100,8);v,sn,fn,ctr,reset,valid,written=struct.unpack('<H6B',out);assert (sn,fn,ctr,reset,valid,written)==(slot,frame,meta[27],meta[28]&1,(meta[28]>>1)&1,int(enabled));assert r==(0 if enabled else 5);assert v==(raw if enabled else 0)
 rows.append({'kind':'locked_irq_history_and_decoder','used':used,'slots':count,'gate':gate,'enabled_lp_widget':enabled,'fifo_overflow':bool(sign),'raw':raw,'fifo_reads':vals[0][2],'frames_stored':frames,'needed_bytes':byte_need,'decoder_status':status,'history_writes':len(vals[0][1]),'writes_touching_lp_descriptors':overlap})
# Sparse synthetic descriptors: original transfer -> new decoder, every position.
for start,enable,method,sign in itertools.product([0,1,2],[0,1,2,3,4,7],[1,2,10],[0,0x80000000]):
 u,b,reads=ns['fixture'](enable,0,2,2,method,sign);u.mem_write(0x20003200+22,struct.pack('<H',1));g['call'](u,0x6530,[start,2,0x20002000]);history=bytes(u.mem_read(0x20008800,8));meta=bytes(u.mem_read(0x20003200,32));mask=0
 # Slot descriptors identify widgets independently of history positions.
 slotptr=struct.unpack('<I',u.mem_read(0x20002000+52,4))[0]
 widgets=[struct.unpack('<H',u.mem_read(slotptr+4*(start+k),2))[0] for k in range(2)]
 for k,w in enumerate(widgets):
  if enable&(1<<w):mask|=1<<(start+k)
 for frame in range(2):
  for slot,w in enumerate(widgets):
   outptr=0x20009100;u.reg_write(UC_ARM_REG_R3,mask);u.mem_write(0x20008000,struct.pack('<III',frame,slot,outptr));u.mem_write(outptr,b'\xcc'*8);r=g['call'](u,g['symbols']['touch_lp_history_read'],[0x20003200,0x20008800,8]);value,sn,fn,ctr,reset,valid,written=struct.unpack('<H6B',u.mem_read(outptr,8));on=bool(enable&(1<<w));assert (r,sn,fn,written)==(0 if on else 5,start+slot,frame,int(on));assert (reset,valid)==(1,0 if sign else 1)
   raw=reads[frame*2+slot]&65535;expected=max(100-raw,0) if w==1 and method in [2,10] else raw
   assert value==(expected if on else 0)
   if not on:assert history[2*(frame*2+slot):2*(frame*2+slot)+2]==b'\xa5\xa5'
 # Reset disables interpretation without erasing samples/count/frame/counter.
 before=bytes(u.mem_read(0x20008800,8));g['call'](u,0x7e04,[0x20002000]);assert bytes(u.mem_read(0x20008800,8))==before;assert bytes(u.mem_read(0x20003200+24,4))==meta[24:28];assert g['call'](u,g['symbols']['touch_lp_history_span'],[0x20003200,8,0x20009000])==1
 rows.append({'kind':'sparse_original_producer_decoder_reset','first':start,'enabled_widgets':enable,'slot_widgets':widgets,'method_widget1':method,'fifo_overflow':bool(sign),'samples_checked':4})
# Read rejection does not touch output; caller supplies stable copied metadata.
for frame,slot,data,out in itertools.product([0,1,2,255],[0,1,2,255],[0,0x20008800],[0,0x20009100]):
 u,b,r=ns['fixture']();c=bytearray(32);struct.pack_into('<H',c,22,1);c[24:27]=bytes([0,2,2]);u.mem_write(0x20003200,bytes(c));u.mem_write(0x20009100,b'\xcc'*8);u.reg_write(UC_ARM_REG_R3,3);u.mem_write(0x20008000,struct.pack('<III',frame,slot,out));status=g['call'](u,g['symbols']['touch_lp_history_read'],[0x20003200,data,8]);bad=not data or not out or frame>=2 or slot>=2;assert status==(3 if bad else 0)
 if bad:assert bytes(u.mem_read(0x20009100,8))==b'\xcc'*8
 rows.append({'kind':'new_decoder_read_guard','frame':frame,'slot':slot,'null_data':not data,'null_output':not out,'status':status})
# New decoder malformed/short-buffer guards: it is not stock firmware code.
for first,count,frames,capacity in itertools.product([0,3,4,255],[0,1,4,255],[0,1,255],[0,2,426,2040]):
 u=g['guest']();common=bytearray(32);struct.pack_into('<H',common,22,1);common[24:27]=bytes([first,count,frames]);u.mem_write(0x20003000,bytes(common));r=g['call'](u,g['symbols']['touch_lp_history_span'],[0x20003000,capacity,0x20009000]);expected=2 if not frames else 3 if not count or first>=4 or first+count>4 else 4 if capacity<2*count*frames else 0;assert r==expected;rows.append({'kind':'new_decoder_metadata_guard','first':first,'slots':count,'frames':frames,'capacity':capacity,'status':r})
# Stock CPU APIs skip the actual type7 LP widget; no invented processing body.
for pc in [0x4e6c,0x5c02]:
 u,writes,reads=actual(False,0,True,0,0,4,0);before=u.mem_read(0x20000000,0x2000);access=[]
 def history_read(u,access_type,a,n,v,data):
  if 0x2000065e<=a<0x20000808:access.append(a)
 u.hook_add(UC_HOOK_MEM_READ,history_read);g['call'](u,pc,[0,0x200004ec]);assert u.mem_read(0x20000000,0x2000)==before;assert not access;rows.append({'kind':'original_type7_cpu_skip','function':hex(pc),'history_reads':0})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Original reset and full locked-project IRQ/producer vs independent source, no call stubs.','New capacity-aware decoder is an app/offline helper, not an existing stock consumer.','426 bytes is only the window before the next known LP-descriptor object; actual declaration may be smaller.','Over-window writes are synthetic fault-injection observations, not evidence of hardware/default-stock manifestation.','No physical IRQ/analog/timing, unknown callback-body or whole-image source claim.']},indent=2)+'\n');print('PASS',len(rows))
