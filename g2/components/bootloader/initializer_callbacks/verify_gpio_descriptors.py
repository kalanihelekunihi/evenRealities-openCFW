#!/usr/bin/env python3
"""Native locked bootloader descriptor/GPIO comparisons; no physical IRQ/W1C."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_INVALID
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ENTRIES={'registrar':('opencfw_bl_descriptor_register',0x430280),'status':('opencfw_boot_gpio_mask_status',0x41dcca),'clear':('opencfw_boot_gpio_mask_clear',0x41de3c),'register':('opencfw_boot_gpio_callback_register',0x41e000),'control':('opencfw_boot_gpio_interrupt_control',0x41da84),'priority':('opencfw_boot_gpio_priority',0x43025c)}
TABLE=0x20004000;MASK=0x20005000
class Machine(v.Machine):
 def __init__(self,source,segs,syms):
  super().__init__(source,segs,syms);self.cpu.mem_map(0x40010000,0x2000);self.cpu.mem_map(0xe000e000,0x2000);self.accesses=[];self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.invalid);self.cpu.hook_add(UC_HOOK_MEM_READ,self.memread,begin=0x40010530,end=0x4001060b)
 def code(self,uc,pc,size,user):
  if not self.source and pc==0x415ff4:
   dest=uc.reg_read(a.UC_ARM_REG_R0);length=uc.reg_read(a.UC_ARM_REG_R1);assert length==28
   uc.mem_write(dest,b"\0"*length);uc.reg_write(a.UC_ARM_REG_R0,dest+length);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def invalid(self,uc,access,address,size,value,user):raise RuntimeError(("invalid memory",self.source,hex(uc.reg_read(a.UC_ARM_REG_PC)),hex(address),size,hex(value)))
 def memread(self,uc,access,address,size,value,user):self.accesses.append(['read',address,size,int.from_bytes(uc.mem_read(address,size),'little')])
 def memwrite(self,uc,access,address,size,value,user):
  if 0x40010000<=address<0x40012000 or 0xe000e000<=address<0xe0010000:self.accesses.append(['write',address,size,value&((1<<(size*8))-1)])
 def call(self,entry,values):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for r,n in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),values+[0]*4):self.cpu.reg_write(r,n)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);pc=self.symbols[ENTRIES[entry][0]]&~1 if self.source else ENTRIES[entry][1];self.execute(pc,entry);assert self.done,(entry,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)));return self.cpu.reg_read(a.UC_ARM_REG_R0) if entry!='priority' else None
 def execute(self,pc,entry):
  try:self.cpu.emu_start(pc|1,v.STOP+2,count=100000)
  except Exception as ex:raise RuntimeError((entry,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)),hex(self.cpu.reg_read(a.UC_ARM_REG_R0)),hex(self.cpu.reg_read(a.UC_ARM_REG_R1)))) from ex
 def w(self,p,n):self.cpu.mem_write(p,struct.pack('<I',n&0xffffffff))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();_,segs,syms=v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,values,prepare=lambda m:None,entry='registrar'):
  obs=[]
  for source in (False,True):
   m=Machine(source,segs,syms);m.cpu.mem_write(MASK,b'\x55'*32);m.cpu.mem_write(0x20023600,b'\xcc'*3584)
   for ch,i in itertools.product((0,1),range(7)):m.w(0x40010530+ch*112+i*16,0xa5a5a5a5);m.w(0x40010534+ch*112+i*16,0x12345678+i)
   prepare(m);m.cpu.reg_write(a.UC_ARM_REG_PRIMASK,len(cases)&1);m.accesses.clear();status=m.call(entry,values)
   obs.append(dict(status=status,accesses=m.accesses,mask=bytes(m.cpu.mem_read(MASK,32)).hex(),callbacks_sha256=hashlib.sha256(m.cpu.mem_read(0x20023600,3584)).hexdigest(),gpio_sha256=hashlib.sha256(m.cpu.mem_read(0x40010000,0x1000)).hexdigest(),scb_sha256=hashlib.sha256(m.cpu.mem_read(0xe000e000,0x2000)).hexdigest(),primask=m.cpu.reg_read(a.UC_ARM_REG_PRIMASK)))
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert obs[0]==obs[1],(label,{k:(obs[0][k],obs[1][k]) for k in obs[0] if k!='accesses' and obs[0][k]!=obs[1][k]},next(((i,x,y) for i,(x,y) in enumerate(zip(obs[0]['accesses'],obs[1]['accesses'])) if x!=y),None),(len(obs[0]['accesses']),len(obs[1]['accesses'])));cases.append(dict(label=label,observation=obs[0]));return obs[0]
 compare('stock97',[0x42f674,97]);compare('null',[0,1]);compare('zero-count',[TABLE,0])
 for pin,kind,initial in itertools.product((0,31,32,63,93,127,156,200,223,224),(0,1,2,3,4,255),(0,1,2)):
  def prep(m):m.cpu.mem_write(TABLE,struct.pack('<IBBBBI',pin,kind,initial,0,0,0))
  compare('row-'+str((pin,kind,initial)),[TABLE,1],prep)
 for pin,mode in itertools.product((0,31,32,63,93,127),(1,2,3,4,255)):
  def prep(m):m.cpu.mem_write(TABLE,struct.pack('<IBBBBI',pin,2,0,mode,0,0x08000101))
  compare('irq-row-'+str((pin,mode)),[TABLE,1],prep)
 for ch,en in itertools.product((0,1,2,256,257,258),(0,1,256,257)):compare('status-'+str((ch,en)),[ch,en,MASK],entry='status')
 for ch in (0,1,2,3,256,257,258,259):compare('clear-'+str(ch),[ch,MASK],entry='clear')
 compare('clear-null',[0,0],entry='clear')
 for ch,pin in itertools.product((0,1,2,3,256,257,258),(0,31,32,127,223,224)):compare('register-'+str((ch,pin)),[ch,pin,0x08000101,0xcafe1234],entry='register')
 for ch,op,pin in itertools.product((0,1,2,3,256),(0,1,2,3,4,256,257),(0,223,224)):
  compare('control-'+str((ch,op,pin)),[ch,op,MASK],lambda m:m.w(MASK,pin),entry='control')
 compare('control-null',[0,1,0],entry='control')
 for irq,priority in itertools.product((0,56,59,255,0xffff,0xfffe,0xfff1,0x10038),(0,4,15,16,255)):compare('priority-'+str((irq,priority)),[irq,priority],entry='priority')
 blob=v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.LOCKED_SHA
 for pc,raw in trace.items():a0=int(pc,16);assert bytes.fromhex(raw)==blob[a0-v.BASE:a0-v.BASE+len(bytes.fromhex(raw))]
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,original_trace=trace,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['GPIO/pin-config/mode/critical helpers execute original/source instructions. Original zero-fill415ff4/417c30 is explicitly modeled for28 stack bytes: installed Unicorn misexecutes its IT/STM carry loop, independently reproduced.','MMIO is RAM, no physical W1C; clear readback/access order compared. Actual IRQ callback bodies and exception delivery not executed.','Registrar IRQ fixtures restricted to pin0..127 because locked local IRQ map has four entries. No invented mapping for banks4..6.','Raw low-byte channel/control and signed-low-halfword priority semantics tested; invalid pin registration preserves stock absence of validation.'])
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
