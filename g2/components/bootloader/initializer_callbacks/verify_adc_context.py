#!/usr/bin/env python3
"""ADC context/calibration original-source comparisons; resident ROM controlled."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
POOL,CACHE,TRIMS,PAIR,OUT=0x20026df0,0x200267f8,0x20026fc0,0x20026fe0,0x20004000
class Machine(v.Machine):
 def __init__(self,source,segs,syms,fixture):
  super().__init__(source,segs,syms);self.cpu.mem_map(0,0x1000);self.cpu.mem_map(0x40020000,0x2000);self.fixture=fixture;self.records=[];self.rom=[]
 def memwrite(self,uc,access,address,size,value,user):
  if POOL<=address<POOL+72 or TRIMS<=address<TRIMS+16 or PAIR<=address<PAIR+8 or address in [OUT,0x2002702c,0x20027199,0x4002010c]:self.records.append([address,size,value&((1<<(size*8))-1)])
 def code(self,uc,pc,size,user):
  if pc==0x48:
   address,out,count=[uc.reg_read(r) for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2)];assert count==1
   offsets={0x42003300:0,0x42003304:1,0x42003308:2,0x42003328:3,0x4200332c:4,0x42006900:0,0x42006904:1,0x42006908:2,0x42006928:3,0x4200692c:4};index=offsets[address];value=self.fixture['values'][index]
   self.rom.append([address,out,count,value,self.fixture['rom_status'],self.r(OUT),self.r(POOL)])
   uc.mem_write(out,struct.pack('<I',value));self.records.append([out,4,value])
   if self.fixture.get('cache_switch') and len(self.rom)==1:
    self.w(CACHE,0x1f01600d);self.w(CACHE+0x48,0x11112222);self.w(CACHE+0x4c,0x33334444)
   uc.reg_write(a.UC_ARM_REG_R0,self.fixture['rom_status']);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def r(self,p):return int.from_bytes(self.cpu.mem_read(p,4),'little')
 def w(self,p,n):self.cpu.mem_write(p,struct.pack('<I',n&0xffffffff))
 def call(self,kind,params):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for reg,n in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),params+[0]*4):self.cpu.reg_write(reg,n)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);pc=self.symbols['opencfw_bl_adc_context_initialize' if kind=='init' else 'opencfw_bl_adc_reset']&~1 if self.source else 0x42e8d0 if kind=='init' else 0x42ea32;self.cpu.emu_start(pc|1,v.STOP+2,count=50000);assert self.done;return self.cpu.reg_read(a.UC_ARM_REG_R0)
 def observation(self,status):return dict(status=status,writes=self.records,rom_calls=self.rom,output=self.r(OUT),context=bytes(self.cpu.mem_read(POOL,72)).hex(),trims=bytes(self.cpu.mem_read(TRIMS,16)).hex(),pair=bytes(self.cpu.mem_read(PAIR,8)).hex(),pair_valid=self.cpu.mem_read(0x20027199,1)[0],flag=self.r(0x2002702c),register=self.r(0x4002010c),cache_magic=self.r(CACHE))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segs,syms=v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,fixture,sequence=[('init',[0,OUT])]):
  results=[]
  for source in (False,True):
   m=Machine(source,segs,syms,fixture);m.cpu.mem_write(POOL,b'\xa5'*72);m.w(POOL,fixture.get('flags',0));m.w(POOL+4,0x12345678);m.w(OUT,0xcccccccc);m.w(CACHE,0x1f01600d if fixture.get('cached') else 0)
   for address,value in zip((CACHE+0x38,CACHE+0x3c,CACHE+0x40,CACHE+0x48,CACHE+0x4c),fixture['values']):m.w(address,value)
   m.cpu.mem_write(TRIMS,b'\xee'*16);m.cpu.mem_write(PAIR,b'\xdd'*8);m.w(0x2002702c,0xdeadbeef);m.cpu.mem_write(0x20027199,b'\xcc');m.w(0x4002010c,0xaabbccdd);m.w(0x400201bc,fixture.get('info_state',0));m.w(0x40021008,fixture.get('ready',1<<27));m.records.clear();status=[m.call(k,a) for k,a in sequence];results.append(m.observation(status))
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert results[0]==results[1],(label,results);cases.append(dict(label=label,fixture=fixture,observation=results[0]));return results[0]
 base=dict(values=[0x4395c001,0x3f800001,0xbb000001,0x12345678,0x87654321],rom_status=0)
 for cached,info,ready,status in itertools.product((False,True),(0,8),(0,1<<27),(0,9,0xffffffff)):
  f=dict(base,cached=cached,info_state=info,ready=ready,rom_status=status);o=compare('calibration-route-'+str((cached,info,ready,status)),f);assert o['status']==[0]
  if cached or not(info&8) or ready:
   assert int(o['trims'][24:26],16)==1 and o['pair_valid']==1
  else:assert int(o['trims'][24:26],16)==0 and o['pair_valid']==0
 for cached,index,value in itertools.product((False,True),range(5),(0,1,0x80000000,0x7fc00000,0xffffffff)):
  values=base['values'].copy();values[index]=value;o=compare('word-validity-'+str((cached,index,value)),dict(base,values=values,cached=cached));assert o['status']==[0];assert int(o['trims'][24:26],16)==(0 if index<3 and value==0 else 1);assert o['pair_valid']==(0 if index>=3 and value==0 else 1)
 for module,output,flags in itertools.product((0,1,256,0xffffffff),(0,OUT),(0,0x01000000,0x01afafaf,0x02000000,0x80000000,0xfeffffff)):
  o=compare('claim-guard-'+str((module,output,flags)),dict(base,flags=flags),[('init',[module,output])]);expected=5 if module else 6 if not output else 7 if flags&0x01000000 else 0;assert o['status']==[expected]
  if expected:assert o['writes']==[] and o['output']==0xcccccccc
  else:
   assert o['output']==POOL;assert o['context'][:8]==struct.pack('<I',(flags&0xff000000)|0x01afafaf).hex()
   if o['rom_calls']:assert all(x[5]==POOL and x[6]&0x01ffffff==0x01afafaf for x in o['rom_calls'])
 for cached,flags in itertools.product((False,True),(0,0x02000000,0x80000000)):
  compare('claim-reset-reclaim-'+str((cached,flags)),dict(base,cached=cached,flags=flags),[('init',[0,OUT]),('init',[0,OUT]),('reset',[POOL]),('init',[0,OUT])])
 for handle,flags in [(0,0),(POOL,0),(POOL,0x01afafaf),(POOL,0x03afafaf),(POOL,0xffafafaf),(POOL,0x01ffffff)]:compare('reset-'+str((handle,flags)),dict(base,flags=flags),[('reset',[handle])])
 o=compare('synthetic-cache-switch-after-first-rom',dict(base,cache_switch=True));assert len(o['rom_calls'])==3 and o['pair']==struct.pack('<II',0x33334444,0x11112222).hex()
 blob=v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.LOCKED_SHA
 for pc,raw in trace.items():a0=int(pc,16);assert bytes.fromhex(raw)==blob[a0-v.BASE:a0-v.BASE+len(bytes.fromhex(raw))]
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,original_trace=trace,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Initializer/reset, selector421548, INFO dispatch4213e6 and ROM thunk41d28a execute original/source instructions. Only absent resident ROM48 is modeled as explicit word/status callback.','MMIO INFO selection/readiness is RAM; no OTP read/power/electrical/calibration validity proof. ROM errors are ignored by the retained dispatch.','Static72-byte context claim/reset does not allocate/free heap or prove peripheral stop/IRQ/task/callback quiescence.','Synthetic cache mutation demonstrates reread order only, not a hardware race. Markers test raw nonzero words, not finite/ranged calibration values.']);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
