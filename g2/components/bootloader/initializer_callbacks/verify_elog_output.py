#!/usr/bin/env python3
"""Stock output/filters/packaging vs adapted pinned upstream; formatter explicit."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v);a=v.a
old_uc=v.Uc
def m33_uc(*args,**kwargs):
 cpu=old_uc(*args,**kwargs);cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);return cpu
v.Uc=m33_uc
TAG=0x20001000;FILE=TAG+0x100;FUNC=TAG+0x200;FMT=TAG+0x300;TEXT=TAG+0x400;TIME=TAG+0x500;PROCESS=TAG+0x600;THREAD=TAG+0x700;BUFFER=0x200258d0;GLOBAL=0x20026700
class Machine(v.Machine):
 def __init__(self,source,segs,syms,f):super().__init__(source,segs,syms);self.f=f;self.events=[];self.recent=[]
 def u(self,p):return int.from_bytes(self.cpu.mem_read(p,4),'little')
 def string(self,p):
  if not p:return None
  out=bytearray()
  while len(out)<4096:
   c=self.cpu.mem_read(p,1)[0]
   if not c:break
   out.append(c);p+=1
  return out.decode()
 def code(self,uc,pc,size,user):
  self.recent.append([hex(pc),hex(uc.reg_read(a.UC_ARM_REG_R0))]);self.recent=self.recent[-30:]
  args=[uc.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]]
  if pc==0x41560c:
   uc.mem_write(args[0],bytes([args[2]&255])*args[1]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc in [0x41a69a,0x41a6a2] or self.source and pc in [self.symbols['opencfw_bl_service_wake']&~1,self.symbols['opencfw_bl_service_sleep']&~1]:
   self.events.append(['lock' if pc in [0x41a69a,self.symbols.get('opencfw_bl_service_wake',1)&~1] else 'unlock']);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  metadata={0x41a6aa:TIME,0x41a6f0:PROCESS,0x41a6f8:THREAD} if not self.source else {self.symbols[n]&~1:value for n,value in [('elog_port_get_time',TIME),('elog_port_get_p_info',PROCESS),('elog_port_get_t_info',THREAD)]}
  if pc in metadata:
   result=metadata[pc];self.events.append(['metadata',{TIME:'time',PROCESS:'process',THREAD:'thread'}[result]]);uc.reg_write(a.UC_ARM_REG_R0,result);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc in [0x41b218,0x41b25c]:
   dest,capacity,fmt,arg=args
   if pc==0x41b218:
    number=arg if arg<0x80000000 else arg-0x100000000;text=str(number).encode();ret=min(len(text),max(capacity-1,0));self.events.append(['line-format',capacity,self.string(fmt),number])
   else:text=self.f.get('message','hello').encode();ret=self.f.get('formatter_return',min(len(text),max(capacity-1,0)));self.events.append(['message-format',capacity,self.string(fmt)])
   if capacity:uc.mem_write(dest,text[:capacity-1]+b'\0')
   uc.reg_write(a.UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc==0x41a692 or self.source and pc==(self.symbols['opencfw_boot_elog_uart_output']&~1):
   self.events.append(['output',args[2],bytes(uc.mem_read(args[0],args[1])).hex()]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def run(self):
  f=self.f;self.cpu.mem_write(GLOBAL,bytes(256));self.cpu.mem_write(BUFFER,bytes([0xa5])*1024)
  def text(p,s):self.cpu.mem_write(p,s.encode()+b'\0')
  for p,t in [(TAG,f.get('tag','app')),(FILE,'file.c'),(FUNC,'run'),(FMT,'fixture'),(TIME,'1234'),(PROCESS,'proc'),(THREAD,'thread')]:text(p,t)
  text(GLOBAL+1,f.get('tag_filter',''));text(GLOBAL+0x20,f.get('keyword',''))
  for i in range(6):
   cp=0x20003000+i*64;lp=cp+32;text(cp,str(30+i)+'m');text(lp,str(i)+'/');self.cpu.mem_write(0x20000334+i*4,struct.pack('<I',cp));self.cpu.mem_write(0x2000031c+i*4,struct.pack('<I',lp));self.cpu.mem_write(GLOBAL+0xd8+i*4,struct.pack('<I',f.get('mask',0x87)))
  self.cpu.mem_write(GLOBAL,bytes([f.get('filter_level',5)]));self.cpu.mem_write(GLOBAL+0xf0,bytes([f.get('initialized',1),f.get('enabled',1),f.get('locking',1),7,9,f.get('color',0)]))
  if 'slot_level' in f:self.cpu.mem_write(GLOBAL+0x31,bytes([f['slot_level']]));text(GLOBAL+0x32,f.get('slot_tag','app'));self.cpu.mem_write(GLOBAL+0x51,b'\1')
  self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000|f.get('exception',0));self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
  for r,n in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],[f.get('level',4),TAG,FILE if f.get('file',True) else 0,FUNC if f.get('function',True) else 0]):self.cpu.reg_write(r,n)
  self.cpu.mem_write(v.SP,struct.pack('<III',f.get('line',123),FMT,0x12345678));pc=self.symbols['opencfw_boot_elog_output']&~1 if self.source else 0x4176ce;self.cpu.emu_start(pc|1,v.STOP+2,count=300000);assert self.done,(self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return dict(events=self.events,buffer=bytes(self.cpu.mem_read(BUFFER,1024)).hex(),logger=bytes(self.cpu.mem_read(GLOBAL,256)).hex())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);arg=ap.parse_args();_,segs,syms=v.elf.elf_info(arg.elf);assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;cases=[];trace={};fixtures=[]
 for level,mask,color,locking in itertools.product([0,1,2,3,4,5,256,257,261],[0,1,2,4,8,16,32,64,128,0x1c,0x87,0xff],[0,1],[0,1]):fixtures.append(dict(level=level,mask=mask,color=color,locking=locking))
 for kw,msg,ret in itertools.product(['','hello','absent'],['hello','x'*1100],[-1,0,5,1024,0x7fffffff]):fixtures.append(dict(keyword=kw,message=msg,formatter_return=ret))
 for key,values in [('tag_filter',['','app','absent']),('enabled',[0,2]),('initialized',[0]),('filter_level',[0,3]),('slot_level',[0,3,5]),('exception',[1,15]),('tag',['a'*15,'a'*16,'a'*40,'a'*1100]),('line',[0,12345,0xffffffff])]:
  for value in values:fixtures.append({key:value, 'mask':0xff})
 for file,function,line in itertools.product([False,True],[False,True],[0,1,99999]):fixtures.append(dict(file=file,function=function,line=line,mask=0xff))
 for f in fixtures:
  obs=[]
  for source in [False,True]:
   m=Machine(source,segs,syms,f)
   try:obs.append(m.run())
   except Exception:
    print('FAILED',source,f,hex(m.cpu.reg_read(a.UC_ARM_REG_PC)),m.recent,[hex(m.cpu.reg_read(r)) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R4,a.UC_ARM_REG_R5,a.UC_ARM_REG_SP]]);raise
   if not source:trace.update(m.trace)
  assert obs[0]==obs[1],(f,{k:[o[k] for o in obs] for k in obs[0] if obs[0][k]!=obs[1][k]});cases.append(dict(fixture=f,observation=obs[0]))
 blob=v.BLOB.read_bytes()
 for pc,raw in trace.items():assert bytes.fromhex(raw)==blob[pc-v.BASE:pc-v.BASE+len(bytes.fromhex(raw))]
 used={pc+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};ranges={'output':[0x4176ce,0x417ace],'tag-level':[0x41760a,0x4176ce],'lock':[0x417570,0x417592],'unlock':[0x417592,0x4175b4],'format':[0x417ad4,0x417b3e],'append':[0x41b158,0x41b1fa]}
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(arg.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),visited_body_bytes={n:len(used&set(range(*r))) for n,r in ranges.items()},original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=cases,limits=['IAR snprintf/vsnprintf, metadata, mutex wake/sleep and final UART sink are injected equally; this tests native output filtering/packaging/clamping/locks, not formatter or UART ownership.','Original fill41560c modeled due reproduced Unicorn IT/STM issue; source memset native.','Synthetic coherent SRAM string tables/filter/tag slots. Only accepted levels0..5 here; assertion-return paths are separate setter tests.','Exact full1024-byte retained buffer and256-byte logger state compare. No hardware output, release/drain, live scheduling or byte-identical source claim.']);arg.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
