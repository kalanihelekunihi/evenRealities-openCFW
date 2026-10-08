#!/usr/bin/env python3
"""Stock output/filters/packaging vs adapted pinned upstream; formatter explicit."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('base',Path('g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py').resolve());v=importlib.util.module_from_spec(s);s.loader.exec_module(v);a=v.a
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

if __name__=='__main__':
 N=Path(__file__).resolve().parent;c=json.loads((N/'current-candidate.json').read_text());elf=Path(c['directory'])/'candidate.elf';_,segments,symbols=v.elf.elf_info(elf)
 TIME=0x20026f18 # Stock/native time provider returns this fixed written buffer.
 capture=json.loads(Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/logger-call-metadata/captured-calls.json').read_text());blob=v.BLOB.read_bytes();rows=[]
 for index,r in enumerate(capture['calls']):
  pair=[]
  for source in [False,True]:
   f=dict(level=r['level'],line=r['line'],tag=r['tag'],mask=0x87);m=Machine(source,segments,symbols,f);start=m.cpu.emu_start
   def begin(pc,end,*args,**kw):
    import re
    def text(p,s):m.cpu.mem_write(p,s.encode()+b'\0')
    for p,key in [(TAG,'tag'),(FILE,'file'),(FUNC,'function'),(FMT,'format')]:text(p,r[key])
    values=list(r['argument_words'])
    for k,kind in enumerate(re.findall(r'%(?:z)?([sdux])',r['format'])):
     if kind=='s':off=values[k]-v.BASE;text(TEXT,blob[off:blob.index(b'\0',off)].decode());values[k]=TEXT
    m.cpu.mem_write(v.SP,struct.pack('<8I',r['line'],FMT,*values));kw['count']=700000
    return start(pc,end,*args,**kw)
   m.cpu.emu_start=begin
   try:pair.append(m.run())
   except Exception as e:(N/'native-elog-failure.json').write_text(json.dumps(dict(index=index,source=source,record=r,pc=hex(m.cpu.reg_read(a.UC_ARM_REG_PC)),recent=m.recent,error=repr(e)),indent=2));raise
  if pair[0]!=pair[1]:(N/'native-elog-failure.json').write_text(json.dumps(dict(index=index,record=r,original=pair[0],source=pair[1]),indent=2));raise AssertionError(index)
  rows.append(dict(call_index=index,family=r['family'],line=r['line'],events=pair[0]['events']))
 result=dict(status='PASS_ELOG_PACKAGING_WITH_ACTUAL_NATIVE_IAR_FORMATTERS',cases=len(rows),candidate_sha256=c['sha256'],comparisons=rows,limits=['Actual original/native elog filtering/packaging and IAR snprintf/vsnprintf instructions execute on captured nonfloating logger inputs. Full1024buffer/256logger compare, output bytes at UART sink compare.','Metadata/mutex/UART sink remain controlled; original memset41560c retains existing IT/STM fixture model. Native memset executes. No UART ownership/hardware or floating formatter proof added here.'])
 (N/'native-elog-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['cases'])
