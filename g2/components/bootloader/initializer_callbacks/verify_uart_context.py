#!/usr/bin/env python3
"""UART original/source instruction comparisons with native power/clock children.
Peripheral acknowledgement is fixed RAM; absent ROM40 remains explicit.
"""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
from unicorn import UC_HOOK_MEM_READ
s=importlib.util.spec_from_file_location('profile',Path(__file__).with_name('verify_adc_profile.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
base=v.v.v.v.v
POOL,OUT,PRIOR,CONFIG,TX,RX=0x20024400,0x20004000,0x20004100,0x20004200,0x20004400,0x20004600
ENTRIES={'claim':('opencfw_bl_post_context_register',0x422ad4),'activate':('opencfw_bl_post_activate',0x422dc6),'configure':('opencfw_boot_control_power_apply',0x422ba8),'validate':('opencfw_bl_post_validate',0x42308e),'baud':('opencfw_boot_uart_baud',0x422e28),'finish':('opencfw_bl_post_finish',0x4236ce),'clear':('opencfw_boot_uart_interrupt_clear',0x423700),'clear-pending':('opencfw_bl_post_enable',0x41f512),'irq-enable':('opencfw_bl_post_precommit',0x41f4f4),'priority':('opencfw_bl_register_mode',0x41f530)}
class Machine(v.Machine):
 def __init__(self,source,segs,syms,fixture):
  super().__init__(source,segs,syms,fixture);self.cpu.mem_map(0x40039000,0x4000);self.cpu.mem_map(0xe000e000,0x10000);self.uart_reads=[];self.cpu.hook_add(UC_HOOK_MEM_READ,self.uart_read)
 def uart_read(self,uc,access,address,size,value,user):
  if 0x40039000<=address<0x4003d000 or address==0x28:self.uart_reads.append([address,size,int.from_bytes(uc.mem_read(address,size),'little')])
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if POOL<=address<POOL+4*0x11c or address in (OUT,0x400201b0) or 0x40039000<=address<0x4003d000 or 0xe000e000<=address<0xe001e000:self.records.append([address,size,value&((1<<(size*8))-1)])
 def uart_call(self,kind,params):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for reg,n in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),params+[0]*4):self.cpu.reg_write(reg,n)
  self.cpu.reg_write(a.UC_ARM_REG_SP,base.SP);self.w(base.SP,params[4] if len(params)>4 else 0);self.cpu.reg_write(a.UC_ARM_REG_LR,base.STOP|1)
  name,original=ENTRIES[kind];pc=self.symbols[name]&~1 if self.source else original
  self.cpu.emu_start(pc|1,base.STOP+2,count=100000);assert self.done,(kind,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return self.cpu.reg_read(a.UC_ARM_REG_R0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segs,syms=base.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,seq,fixture=None):
  f=dict(module=0,flags=0x01ea9e06,prior=0,prior_flags=0,saved=1,allowed=0,revision=34,baud=115200,selector=1,clock=0,fields=[3,2,0,0,0,0,2,2],power_control=0,power_status=0x1e00);f.update(fixture or {});results=[]
  for source in (False,True):
   m=Machine(source,segs,syms,f);m.cpu.mem_write(POOL,b'\xa5'*(4*0x11c))
   for i in range(4):m.w(POOL+i*0x11c,f['flags']);m.w(POOL+i*0x11c+0x28,i);m.cpu.mem_write(POOL+i*0x11c+4,bytes([f['saved']]));m.w(POOL+i*0x11c+0x30,f['baud']);m.cpu.mem_write(POOL+i*0x11c+0x118,b'\x04')
   m.w(OUT,f['prior']);m.w(PRIOR,f['prior_flags']);m.cpu.mem_write(CONFIG,struct.pack('<I',f['baud'])+bytes(f['fields'])+bytes([f['clock']])+b'\x00'*3);m.cpu.mem_write(TX,b'\xaa'*128);m.cpu.mem_write(RX,b'\xbb'*128)
   for module in range(4):
    for off in (0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x40,0x44,0x48):m.w(0x40039000+(module<<12)+off,0xa5000000+off)
    m.w(0x40039000+(module<<12)+0x30,0xa5000000|(f['selector']<<4))
   m.w(0x4002000c,f['revision']);m.w(0x400201b0,0xffffffff);m.w(0x40021004,f['power_control']);m.w(0x40021008,f['power_status']);m.cpu.mem_write(0x20000550,bytes([f['allowed']]));m.w(0x20026e94,0);m.w(0x20026e98,0);m.w(0x20026ea4,0);m.w(0x20026ea8,0);m.cpu.mem_write(0x2002719a,b'\x00');m.cpu.mem_write(0x2002719c,b'\x00');m.cpu.mem_write(0x2002719e,b'\x00');m.w(0x20027030,0);m.w(0x20027044,0);m.w(0x40004044,0xabcdef00);m.w(0x20026e3c,0);m.w(0x20026e44,0);m.w(0x20026e48,0);m.cpu.reg_write(a.UC_ARM_REG_PRIMASK,f.get('primask',0));m.records.clear();m.uart_reads.clear();status=[m.uart_call(k,p) for k,p in seq]
   ptr=m.r(0x20027044);assert not ptr or base.SP-0x1000<=ptr<base.SP
   results.append(dict(status=status,writes=m.records,reads=m.uart_reads,pool=bytes(m.cpu.mem_read(POOL,4*0x11c)).hex(),output=m.r(OUT),config=bytes(m.cpu.mem_read(CONFIG,16)).hex(),registers=[[m.r(0x40039000+(module<<12)+off) for off in (0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x40,0x44,0x48)] for module in range(4)],buffers=[bytes(m.cpu.mem_read(TX,128)).hex(),bytes(m.cpu.mem_read(RX,128)).hex()],power_control=m.r(0x40021004),highspeed=m.r(0x400201b0),users=[m.r(0x20026e94),m.r(0x20026ea4)],hfadj=m.r(0x40004044),callback_pointer='stack-local' if ptr else 'null',external=m.external,primask=m.cpu.reg_read(a.UC_ARM_REG_PRIMASK)))
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert results[0]==results[1],(label,f,results);cases.append(dict(label=label,fixture=f,observation=results[0]));return results[0]
 for module,out,prior,flags in itertools.product((0,1,2,3,4,256,0xffffffff),(0,OUT),(0,PRIOR),(0,0x01ea9e06,0xffea9e06,0x00ea9e06)):
  o=compare('constructor-'+str((module,out,prior,flags)),[('claim',[module,out])],dict(prior=prior,prior_flags=flags));assert o['status']==[5 if module>=4 else 6 if out==0 else 7 if prior and flags&0x01ffffff==0x01ea9e06 else 0]
 for module in range(4):
  p=POOL+module*0x11c;compare('claim-reuse-'+str(module),[('claim',[module,OUT]),('claim',[module,OUT])]);compare('occupied-pool-replaced-'+str(module),[('claim',[module,OUT])],dict(flags=0xffea9e06));compare('self-output-'+str(module),[('claim',[module,p+0x30])],dict(baud=0))
 for handle,flags in itertools.product((0,POOL),(0,0x01ea9e06,0xffea9e06)):
  for tx,ntx,rx,nrx in itertools.product((0,TX),(0,17),(0,RX),(0,31)):compare('activate-'+str((handle,flags,tx,ntx,rx,nrx)),[('activate',[handle,tx,ntx,rx,nrx])],dict(flags=flags))
 compare('activate-reinitialize',[('activate',[POOL,TX,17,RX,31]),('activate',[POOL,0,0,0,0]),('activate',[POOL,RX,4,TX,8])])
 for module,selector,baud in itertools.product(range(4),range(8),(0,1,115200,1500000,1500001,3000001,0x10000000,0xffffffff)):
  compare('baud-'+str((module,selector,baud)),[('baud',[module,baud,OUT])],dict(selector=selector))
 for handle,flags in itertools.product((0,POOL),(0,0x01ea9e06,0xffea9e06)):
  compare('validate-guards-'+str((handle,flags)),[('validate',[handle,CONFIG])],dict(flags=flags))
 for module in range(4):
  compare('native-clock-config-'+str(module),[('validate',[POOL+module*0x11c,CONFIG])],dict(allowed=1))
 for clock,rev,baud in itertools.product((0,1,2,255),(33,34),(0,115200,1500000,1500001,3000001,0x10000000)):
  compare('configuration-'+str((clock,rev,baud)),[('validate',[POOL,CONFIG])],dict(clock=clock,revision=rev,baud=baud))
 for index,value in itertools.product((0,1,2,4,5,6,7),(0,1,3,7,255)):
  fields=[3,2,0,0,0,0,2,2];fields[index]=value;compare('field-'+str((index,value)),[('validate',[POOL,CONFIG])],dict(fields=fields))
 for operation,save,saved,handle,flags in itertools.product((0,1,2,3,256),(0,1,256,257),(0,1),(0,POOL),(0,0x01ea9e06)):
  o=compare('power-guards-'+str((operation,save,saved,handle,flags)),[('configure',[handle,operation,save])],dict(flags=flags,saved=saved));assert o['status']==[2 if not handle or not flags else 6 if operation>2 else 7 if operation==0 and save&255 and not saved else 0]
 for module,operation,baud,rev,allowed,primask in itertools.product(range(4),(1,2),(115200,1500001),(33,34),(0,1),(0,1)):
  p=POOL+module*0x11c;compare('save-restore-'+str((module,operation,baud,rev,allowed,primask)),[('configure',[p,operation,1]),('configure',[p,0,1])],dict(baud=baud,revision=rev,allowed=allowed,primask=primask))
 for kind,handle,flags,mask in itertools.product(('finish','clear'),(0,POOL),(0,0x01ea9e06),(0,1,0x471,0xffffffff)):compare('interrupt-'+str((kind,handle,flags,mask)),[(kind,[handle,mask])],dict(flags=flags))
 for kind,irq,priority in itertools.product(('irq-enable','clear-pending','priority'),(0,15,18,31,32,63,0x7fff,0x8000,0xffff,0x10010),(0,3,15,16,255)):
  compare('nvic-'+str((kind,irq,priority)),[(kind,[irq,priority])])
 blob=base.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==base.LOCKED_SHA
 for pc,raw in trace.items():p=int(pc,16);assert blob[p-base.BASE:p-base.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 ranges={'constructor':[0x422ad4,0x422ba8],'power':[0x422ba8,0x422d20],'activate':[0x422dc6,0x422e28],'baud':[0x422e28,0x422ee0],'validate':[0x42308e,0x4232c8],'finish':[0x4236ce,0x4236fa],'clear':[0x423700,0x42372a],'ring':[0x4275ea,0x427602],'nvic-enable':[0x41f4f4,0x41f512],'nvic-clear':[0x41f512,0x41f530],'nvic-priority':[0x41f530,0x41f558]}
 visited={k:sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if lo<=int(pc,16)<hi) for k,(lo,hi) in ranges.items()}
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=base.LOCKED_SHA,original_trace=trace,body_ranges=ranges,visited_body_bytes=visited,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Original and source constructor/config/borrowed ring/baud/interrupt/NVIC instructions execute; native power and class4 clock children execute.','Resident ROM40 cycle wait is controlled; power status and UART/NVIC MMIO are fixed RAM. No physical acknowledgement, IRQ delivery, DMA, scheduler or buffer-drain proof.','Class6 feature disabled exercises its native error branch, whose status UART ignores; PLL enabled behavior is outside this fixture.','UART division uses a source specialization for the observed 64/32 ABI; the general 42287c helper is not claimed implemented. UDIV trap disabled, including zero divisor.','Stack-local clock callback addresses are normalized after mapped bounds check; no asynchronous lifetime proof.','No allocator is called. Reinitialization retains unrelated context bytes and never frees borrowed buffers.']);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
