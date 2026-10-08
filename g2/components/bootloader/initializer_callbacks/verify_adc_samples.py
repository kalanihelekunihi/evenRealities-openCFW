#!/usr/bin/env python3
"""Original/source ADC correction, enumeration and lifecycle; explicit FIFO RAM fixtures."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
from unicorn import UC_HOOK_MEM_READ
s=importlib.util.spec_from_file_location('adc',Path(__file__).with_name('verify_adc_control.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
COUNT,OUTPUT,BUFFER=0x20004200,0x20004300,0x20004500
ENTRIES={'correct':('opencfw_boot_adc_correct_sample',0x42ee00),'enumerate':('opencfw_bl_adc_enumerate',0x42ee70),'activate':('opencfw_bl_adc_activate',0x42ed60),'enable':('opencfw_bl_adc_enable',0x42ebaa),'disable':('opencfw_bl_adc_disable',0x42ebe2),'command':('opencfw_bl_adc_command',0x42eff4),'deactivate':('opencfw_bl_adc_normalize',0x42eda0)}
class Machine(v.Machine):
 def __init__(self,source,segs,syms,fixture):
  super().__init__(source,segs,syms,fixture);self.cpu.mem_map(0x40004000,0x1000);self.fifo=list(fixture.get('fifo',[]));self.fifo_index=0;self.accesses=[];self.cpu.hook_add(UC_HOOK_MEM_READ,self.sample_read)
 def sample_read(self,uc,access,address,size,value,user):
  if address==0x4003803c:
   assert self.fifo_index<len(self.fifo),'unexpected extra FIFO read';word=self.fifo[self.fifo_index];self.fifo_index+=1;uc.mem_write(address,struct.pack('<I',word));self.accesses.append(['fifo',word])
  elif 0x4003800c<=address<0x4003802c:self.accesses.append(['slot',address])
  elif BUFFER<=address<BUFFER+128:self.accesses.append(['buffer',address,int.from_bytes(uc.mem_read(address,size),'little')])
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if address in (COUNT,0x40038000,0x40038008,0x40038200,0x40038040,0x40004044,0x20026e94,0x20026e98) or OUTPUT<=address<OUTPUT+128:self.records.append([address,size,value&((1<<(size*8))-1)])
 def invoke(self,kind,params):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for reg,n in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),params+[0]*4):self.cpu.reg_write(reg,n)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.v.v.SP);self.w(v.v.v.SP,params[4] if len(params)>4 else 0);self.cpu.reg_write(a.UC_ARM_REG_LR,v.v.v.STOP|1);name,orig=ENTRIES[kind];pc=self.symbols[name]&~1 if self.source else orig;self.cpu.emu_start(pc|1,v.v.v.STOP+2,count=50000);assert self.done;return self.cpu.reg_read(a.UC_ARM_REG_R0)
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segs,syms=v.v.v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,sequence,fixture=None):
  f=dict(flags=0x01afafaf,valid=1,gain=0,offset=0,fpscr=0,config=0,interrupt_enable=0x12345678,users=0,count=1,slots=[0x300]*8,buffer=[0x100000|(3200<<6)]*8,fifo=[0x100000|(3200<<6)]*8);f.update(fixture or {});observations=[]
  for source in (False,True):
   m=Machine(source,segs,syms,f);m.w(v.v.POOL,f['flags']);m.w(v.v.POOL+4,0);m.w(0x20026fe0,f['offset']);m.w(0x20026fe4,f['gain']);m.cpu.mem_write(0x20027199,bytes([f['valid']]));m.w(0x40038000,f['config']);m.w(0x40038200,f['interrupt_enable']);m.w(0x40038040,f.get('trigger_timer',0x87654321));m.w(0x40004044,0xabcdefff);m.w(0x20026e94,f['users']);m.w(0x20026e98,0);m.w(COUNT,f['count']);m.cpu.mem_write(OUTPUT,b'\xcc'*128);m.cpu.mem_write(BUFFER,b''.join(struct.pack('<I',x) for x in f['buffer']))
   for i,n in enumerate(f['slots']):m.w(0x4003800c+4*i,n)
   m.cpu.reg_write(a.UC_ARM_REG_FPSCR,f['fpscr']);m.cpu.reg_write(a.UC_ARM_REG_PRIMASK,f.get('primask',0));m.records.clear();status=[m.invoke(kind,params) for kind,params in sequence];o=dict(status=status,writes=m.records,reads=m.reads,accesses=m.accesses,fifo_reads=m.fifo_index,output=bytes(m.cpu.mem_read(OUTPUT,128)).hex(),count=m.r(COUNT),context=m.r(v.v.POOL),config=m.r(0x40038000),interrupt_enable=m.r(0x40038200),trigger_timer=m.r(0x40038040),command=m.r(0x40038008),users=m.r(0x20026e94),hfadj=m.r(0x40004044),fpscr=m.cpu.reg_read(a.UC_ARM_REG_FPSCR),primask=m.cpu.reg_read(a.UC_ARM_REG_PRIMASK));observations.append(o)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert observations[0]==observations[1],(label,f,observations);cases.append(dict(label=label,fixture=f,observation=observations[0]));return observations[0]
 for valid,enabled,word in itertools.product((0,1,255),(0,1,256,257),(0,63,0xfffff,0xa5ffffff)):
  o=compare('correction-gate-'+str((valid,enabled,word)),[('correct',[word,enabled])],dict(valid=valid));
  if not valid or not(enabled&255):assert o['status']==[word]
 for gain,offset,word,fpscr in itertools.product((0,bits(.1),bits(1),bits(2),0x7fc00000,0x7f800001),(0,bits(.001),bits(-.001),0x7fc00000),(0,0x80000,0xfffff),(0,0x400000,0x800000,0xc00000,0x1000000,0x2000000)):
  compare('correction-fp-'+str((gain,offset,word,fpscr)),[('correct',[word,1])],dict(gain=gain,offset=offset,fpscr=fpscr))
 for kind,handle,flags in itertools.product(('activate','enable','disable','command','deactivate'),(0,v.v.POOL),(0,0x01afafaf,0x03afafaf,0xffafafaf)):
  o=compare('lifecycle-guard-'+str((kind,handle,flags)),[(kind,[handle])],dict(flags=flags));
  if not handle or flags&0x01ffffff!=0x01afafaf:assert o['status']==[2]
 for config,flags,users,primask in itertools.product((0,1,4,0x03000005,0x02000005,0xffffffff),(0x01afafaf,0x03afafaf),(0,1<<15,3<<15),(0,1)):
  compare('lifecycle-'+str((config,flags,users,primask)),[(k,[v.v.POOL]) for k in ('enable','activate','activate','enable','command','disable','deactivate')],dict(config=config,flags=flags,users=users,primask=primask))
 for buffered,full,count,valid,slot in itertools.product((False,True),(0,1,256,257),(0,1,3),(0,1),range(8)):
  slots=[0x300]*8;slots[slot]=0x800;word=(slot<<28)|(1<<20)|(3200<<6);o=compare('enumeration-'+str((buffered,full,count,valid,slot)),[('enumerate',[v.v.POOL,full,BUFFER if buffered else 0,COUNT,OUTPUT])],dict(slots=slots,count=count,valid=valid,fifo=[word]*8,buffer=[word]*8));assert o['status']==[0] and o['count']==max(count,1)
 for final,count in itertools.product((0,1),(1,3)):
  compare('fifo-empty-stop-'+str((final,count)),[('enumerate',[v.v.POOL,0,0,COUNT,OUTPUT])],dict(count=count,fifo=[(final<<20)|(1000<<6)]*4))
 for handle,flags,out in itertools.product((0,v.v.POOL),(0,0x01afafaf),(0,OUTPUT)):
  o=compare('enumeration-errors-'+str((handle,flags,out)),[('enumerate',[handle,0,0,COUNT,out])],dict(flags=flags));assert o['status']==[2 if not handle or flags==0 else 6 if not out else 0]
 blob=v.v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.v.LOCKED_SHA
 for pc,raw in trace.items():p=int(pc,16);assert blob[p-v.v.v.BASE:p-v.v.v.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 ranges=[(0x42ebaa,0x42ec0c),(0x42ed60,0x42edf6),(0x42ee00,0x42ee6c),(0x42ee70,0x42eff4),(0x42eff4,0x42f014)];visited=sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if any(lo<=int(pc,16)<hi for lo,hi in ranges));assert visited==776
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.LOCKED_SHA,original_trace=trace,visited_new_body_bytes=visited,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['All ADC FP32, enumeration and lifecycle instructions execute without stubs. Reused clock release/provider4 execute, with mapped HFADJ and synthetic user bitmap.','FIFO values are explicitly supplied per read; peripheral readiness, empty behavior and actual analog sampling not established.','NaN/overflow/rounding/FZ/DN comparisons reflect Unicorn original/source agreement, not hardware certification.','Zero requested count still processes one record in valid fixtures; output capacity/readable pointer behavior and fault behavior not made safe by reconstruction.','Deactivation is register/clock/context metadata, not a proved ISR/task/callback quiesce or buffer-drain boundary.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_new_body_bytes']}))
if __name__=='__main__':main()
